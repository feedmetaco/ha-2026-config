## SnoPUD ➜ Home Assistant — Backfill and Monthly Automation Plan

This document is a copy-ready runbook you can move to `C:\Users\Sami\Documents\ha-config\snopud-import\README.md`.

### Decisions
- **Backfill method**: write monthly long‑term statistics directly into the Home Assistant Recorder database (SQLite) from `Usage.csv`.
- **Future automation**: n8n Email CSV watcher parses the monthly bill CSV and updates cumulative kWh (and cost) in HA.
- **Entities** (keep existing IDs):
  - `sensor.snopud_meter_snopud_grid_kwh_total` — kWh, `device_class: energy`, `state_class: total_increasing`.
  - `sensor.snopud_meter_snopud_grid_kwh_total_cost` — USD, `device_class: monetary`, `state_class: total`.
- **Cost model** (per month):
  - Base: 0.80 USD per day × billing days
  - Energy: 0.102566 USD × kWh
  - Municipal tax: 5% on subtotal
  - Total = round((base + energy) × 1.05, 2)

---

## Folder layout to create in `ha-config`

```
ha-config/
  snopud-import/
    README.md                      # this file
    data/
      Usage.csv                    # historical CSV (columns: End, Name, Meter, Estimated Indicator, kWh)
    backfill/
      backfill_to_recorder_sqlite.py
    n8n/
      ha-snopud-email-csv.json     # importable workflow
    templates/
      config_includes.yaml         # HA input_numbers + template sensors
```

Place your current `Usage.csv` inside `snopud-import/data/`.

---

## Home Assistant config additions (built‑in only)

Add this include to your `configuration.yaml`:

```yaml
template: !include snopud-import/templates/config_includes.yaml
input_number: !include_dir_merge_named input_number
```

Or, if you prefer a single include file, merge the following content into `snopud-import/templates/config_includes.yaml` and ensure it is loaded by your configuration:

```yaml
input_number:
  snopud_total_kwh:
    name: SnoPUD Total kWh
    min: 0
    max: 100000
    step: 0.001
    mode: box

  snopud_rate_per_kwh:
    name: SnoPUD Rate per kWh
    min: 0
    max: 5
    step: 0.0001
    mode: box
    initial: 0.102566

  snopud_daily_base_fee:
    name: SnoPUD Daily Base Fee
    min: 0
    max: 5
    step: 0.01
    mode: box
    initial: 0.80

  snopud_tax_rate:
    name: SnoPUD Tax Rate
    min: 0
    max: 1
    step: 0.01
    mode: box
    initial: 0.05

template:
  - sensor:
      - name: "SnoPUD Meter SnoPUD Grid kWh Total"
        unique_id: snopud_meter_grid_kwh_total
        unit_of_measurement: "kWh"
        device_class: energy
        state_class: total_increasing
        state: "{{ states('input_number.snopud_total_kwh') | float(0) }}"

      - name: "SnoPUD Grid kWh Total Cost"
        unique_id: snopud_meter_grid_kwh_total_cost
        unit_of_measurement: "USD"
        device_class: monetary
        state_class: total
        # Note: monthly base+tax applied by n8n during monthly import; this formula is a fallback.
        state: >-
          {% set kwh = states('input_number.snopud_total_kwh') | float(0) %}
          {% set rate = states('input_number.snopud_rate_per_kwh') | float(0) %}
          {{ (kwh * rate) | round(2) }}
```

Optional helper (purely for UI):

```yaml
utility_meter:
  snopud_monthly:
    source: sensor.snopud_meter_snopud_grid_kwh_total
    cycle: monthly
```

---

## Backfill — Recorder (SQLite) one‑time write

Prerequisites:
- You use Home Assistant OS with the default Recorder database at `/config/home-assistant_v2.db` (SQLite).
- You can access `/config` via Samba.

High‑level steps:
1. Create a full backup: Supervisor → Backups → Create Full Backup.
2. Stop Core to release the DB: from SSH/Terminal add‑on run: `ha core stop`.
3. Copy `/config/home-assistant_v2.db` to your PC via Samba.
4. Run the backfill script locally against the DB copy and `snopud-import/data/Usage.csv`.
5. Copy the updated DB back to `/config/` (replace the original).
6. Start Core: `ha core start`.
7. Home Assistant → Developer Tools → Statistics: fix any reported issues if prompted.
8. Open Energy Dashboard and pick `sensor.snopud_meter_snopud_grid_kwh_total` as the grid consumption source.

CSV expectations:
- Columns: `End, Name, Meter, Estimated Indicator, kWh`
- `End` is the period end timestamp (e.g., `07/11/2025 11:59:59 PM`).
- `kWh` may include thousands separators (e.g., `1,417`).

How periods are derived:
- Period start = previous row’s `End`. For the first row, start is inferred from the delta to the next `End`.
- We import statistics with `start` at the top of the hour for HA (round down), using cumulative `sum` values.

Script CLI (to be placed at `snopud-import/backfill/backfill_to_recorder_sqlite.py`):

```bash
python backfill/backfill_to_recorder_sqlite.py \
  --db "C:/path/to/home-assistant_v2.db" \
  --csv "snopud-import/data/Usage.csv" \
  --sensor-kwh sensor.snopud_meter_snopud_grid_kwh_total \
  --sensor-cost sensor.snopud_meter_snopud_grid_kwh_total_cost \
  --tz America/Los_Angeles
```

What the script does:
- Parses CSV, normalizes numbers, infers period starts.
- Computes cumulative kWh and cumulative USD per period using the cost model above.
- Upserts `statistics_meta` and `statistics` rows for both sensors (idempotent; safe to re‑run).

Verification checklist after start:
- Developer Tools → Statistics: no errors for the two sensors.
- Energy Dashboard shows historical consumption per month.

---

## Monthly automation — n8n Email CSV watcher

Overview:
- Trigger: IMAP Email (filter SnoPUD statement mail with CSV attachment).
- Parse: Spreadsheet File (CSV) → ensure `End` and `kWh` are read.
- State: n8n data store keeps the last imported `End` datetime.
- Compute:
  - Days = (current_End - previous_End) in calendar days.
  - Base = days × 0.80; Energy = kWh × 0.102566; Total = round((Base + Energy) × 1.05, 2).
- Update HA cumulatives via REST:
  - GET `/api/states/input_number.snopud_total_kwh` → parse `state` as float.
  - POST `/api/services/input_number/set_value` with new cumulative kWh.
  - For cost, either compute and import to long‑term statistics (advanced) or maintain a separate cumulative input_number. For simplicity, maintain the cost as long‑term statistics only during backfill; going forward the Energy Dashboard can compute cost from rate if desired. If you prefer cumulative cost too, mirror the same `set_value` pattern to an `input_number.snopud_total_cost` and update the template accordingly.
- Notify success/failure via Email/Telegram.

Required variables (n8n credentials store):
- `HA_URL` (e.g., `http://homeassistant.local:8123`)
- `HA_TOKEN` (Long‑Lived Access Token)
- IMAP mailbox credentials and filter.

Import:
- Use the provided `n8n/ha-snopud-email-csv.json` workflow. After import, open credentials, set URLs/tokens, and enable the Cron/IMAP trigger.

---

## Security and safety
- Always take a **full backup** before touching the Recorder DB.
- Store the HA Long‑Lived Access Token securely in n8n credentials.
- The backfill script is **idempotent**. If you need to change parameters, re‑run and it will upsert the same periods.

---

## Troubleshooting
- If the Energy Dashboard does not show historical months, ensure the sensors have `state_class` as above and that statistics were created with `has_sum=true`.
- If Developer Tools → Statistics shows issues, click Fix to let HA re‑index.
- If the CSV contains estimated months (marked with `*` in `Estimated Indicator`), they will still be imported; you can tag those months in notes if desired.

---

## Quick checklist
- [ ] Create folder structure under `ha-config/snopud-import/`.
- [ ] Drop `Usage.csv` into `snopud-import/data/`.
- [ ] Add `config_includes.yaml` and include it in HA configuration.
- [ ] Create HA Long‑Lived Access Token for n8n.
- [ ] Backup Recorder DB, stop Core, run backfill script, restore DB, start Core.
- [ ] Verify in Statistics + Energy Dashboard.
- [ ] Import n8n workflow, set credentials, enable, and test with a sample CSV email.


