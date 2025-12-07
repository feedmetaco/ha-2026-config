import argparse
import csv
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill SnoPUD monthly cumulative kWh and cost into Home Assistant Recorder (SQLite)")
    parser.add_argument("--db", required=True, help="Path to home-assistant_v2.db (SQLite)")
    parser.add_argument("--csv", required=True, help="Path to Usage.csv")
    parser.add_argument("--sensor-kwh", required=True, help="Entity ID for cumulative kWh sensor")
    parser.add_argument("--sensor-cost", required=True, help="Entity ID for cumulative USD cost sensor")
    parser.add_argument("--tz", default="America/Los_Angeles", help="Timezone name (for display only; timestamps stored as UTC)")
    return parser.parse_args()


def parse_number(text: str) -> float:
    if text is None:
        return 0.0
    return float(str(text).replace(",", "").strip() or 0)


def read_usage_rows(csv_path: Path):
    rows = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            end = datetime.strptime(r["End"], "%m/%d/%Y %I:%M:%S %p")
            kwh = parse_number(r["kWh"])
            rows.append({"end": end, "kwh": kwh, "estimated": r.get("Estimated Indicator", "") == "*"})
    rows.sort(key=lambda r: r["end"])  # ascending
    return rows


def ensure_meta(conn: sqlite3.Connection, statistic_id: str, unit: str, name: str):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO statistics_meta (statistic_id, unit_of_measurement, has_mean, has_sum, name, source)
        VALUES (?, ?, 0, 1, ?, 'external')
        """,
        (statistic_id, unit, name),
    )
    conn.commit()


def upsert_statistic_sum(conn: sqlite3.Connection, statistic_id: str, start_ts: datetime, sum_value: float):
    # Home Assistant expects start timestamps at start-of-hour; we align to hour
    aligned = start_ts.replace(minute=0, second=0, microsecond=0)
    aligned_str = aligned.isoformat(sep=" ")
    aligned_ts = aligned.timestamp()
    
    cur = conn.cursor()
    
    # Get metadata_id
    cur.execute("SELECT id FROM statistics_meta WHERE statistic_id = ?", (statistic_id,))
    meta_row = cur.fetchone()
    if not meta_row:
        raise ValueError(f"No metadata found for {statistic_id}")
    metadata_id = meta_row[0]
    
    # Check if record exists (using start_ts which is part of the unique index)
    cur.execute(
        "SELECT id FROM statistics WHERE metadata_id = ? AND start_ts = ?",
        (metadata_id, aligned_ts)
    )
    existing = cur.fetchone()
    
    if existing:
        # Update existing record
        cur.execute(
            """
            UPDATE statistics 
            SET sum = ?, created = strftime('%Y-%m-%d %H:%M:%f','now'), created_ts = strftime('%s','now')
            WHERE id = ?
            """,
            (float(sum_value), existing[0])
        )
    else:
        # Insert new record
        cur.execute(
            """
            INSERT INTO statistics (created, created_ts, metadata_id, start, start_ts, mean, min, max, last_reset, last_reset_ts, state, sum, mean_weight)
            VALUES (strftime('%Y-%m-%d %H:%M:%f','now'), strftime('%s','now'), ?, ?, ?, NULL, NULL, NULL, NULL, NULL, NULL, ?, NULL)
            """,
            (metadata_id, aligned_str, aligned_ts, float(sum_value))
        )
    
    conn.commit()


def main():
    args = parse_args()
    db_path = Path(args.db)
    csv_path = Path(args.csv)

    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}")
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    usage = read_usage_rows(csv_path)
    if not usage:
        raise SystemExit("No CSV rows found")

    # Compute period starts based on prior row end
    periods = []
    prev_end = None
    for idx, row in enumerate(usage):
        end = row["end"]
        if prev_end is None:
            # infer start as one month before current end (approximate to previous end from next row if available)
            inferred_start = (end - timedelta(days=31))
        else:
            inferred_start = prev_end
        periods.append({"start": inferred_start, "end": end, "kwh": row["kwh"]})
        prev_end = end

    # Cumulative sums
    cumulative_kwh = 0.0
    cumulative_usd = 0.0

    def monthly_cost(kwh: float, days: int) -> float:
        base = 0.80 * days
        energy = 0.102566 * kwh
        total = (base + energy) * 1.05
        return round(total, 2)

    conn = sqlite3.connect(str(db_path))
    try:
        ensure_meta(conn, args.__dict__["sensor_kwh"], "kWh", "SnoPUD Grid kWh Total")
        ensure_meta(conn, args.__dict__["sensor_cost"], "USD", "SnoPUD Grid kWh Total Cost")

        for p in periods:
            days = (p["end"].date() - p["start"].date()).days or 30
            cumulative_kwh += p["kwh"]
            cumulative_usd += monthly_cost(p["kwh"], days)
            upsert_statistic_sum(conn, args.__dict__["sensor_kwh"], p["end"], cumulative_kwh)
            upsert_statistic_sum(conn, args.__dict__["sensor_cost"], p["end"], cumulative_usd)

    finally:
        conn.close()

    print("Backfill complete. Rows upserted:", len(periods))


if __name__ == "__main__":
    main()


