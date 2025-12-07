# 🚀 Grafana + InfluxDB Setup Guide

**Status:** Both services installed and started ✅  
**Next:** Configure and deploy dashboards automatically

---

## Step-by-Step Setup (10 minutes)

### Step 1: Access Grafana (1 minute)

1. **Open Grafana:**
   - URL: **http://192.168.10.6:3000**
   - Username: `admin`
   - Password: `admin` (or what you set during install)

2. **You'll see:** Grafana welcome screen

---

### Step 2: Add InfluxDB Data Source (2 minutes)

1. **In Grafana, click:**
   - Left menu → ⚙️ Configuration → Data Sources
   
2. **Click:** "Add data source"

3. **Select:** "InfluxDB"

4. **Configure:**
   ```
   Name: HomeAssistant_InfluxDB
   Query Language: InfluxQL (or Flux if you're using v2)
   URL: http://192.168.10.6:8086
   Database: homeassistant (or your bucket name)
   User: (your InfluxDB username)
   Password: (your InfluxDB password)
   ```

5. **Click:** "Save & Test"

6. **You should see:** ✅ "Data source is working"

---

### Step 3: Auto-Deploy Agent 4's Dashboards (AUTOMATED!)

**Once InfluxDB data source is added, I can auto-deploy all dashboards!**

**Agent 4 Designed:**
1. 🏠 NOC Overview (30k view)
2. 🌐 Network Drilldown (UniFi stats)
3. ⚡ Power Drilldown (energy/cost with your 968 sensors!)
4. 🖨️ Printer Drilldown (Bambu Lab)

**To deploy automatically:**

Option A: I'll create Grafana API deployment script  
Option B: Import manually (I'll provide JSON files)

---

### Step 4: Configure HA → InfluxDB (3 minutes)

**Add to your `configuration.yaml`:**

```yaml
# InfluxDB Integration
influxdb:
  host: 192.168.10.6
  port: 8086
  database: homeassistant  # or your database/bucket name
  username: homeassistant
  password: !secret influxdb_password
  max_retries: 3
  default_measurement: state
  tags:
    instance: production
    source: ha
  include:
    domains:
      - sensor
      - switch
      - binary_sensor
      - light
      - climate
  exclude:
    entities:
      - sensor.time
      - sensor.date
```

**Add to `secrets.yaml`:**
```yaml
influxdb_password: YOUR_INFLUX_PASSWORD
```

**Then restart HA** - Data will start flowing to InfluxDB!

---

## 🎯 What This Gives You

### With InfluxDB (Perfect for 968 sensors!)
- ✅ **Long-term storage** - Keep years of sensor data
- ✅ **Fast queries** - Optimized for time-series
- ✅ **Advanced analytics** - Grafana can query historical trends
- ✅ **Better performance** - Offloads from HA database

### With Grafana Dashboards
- ✅ **NOC Overview** - System health at a glance
- ✅ **Sensor Analytics** - Trends across your 968 sensors
- ✅ **Power Monitoring** - Real-time and cost tracking
- ✅ **Network Monitoring** - UniFi stats and drilldowns
- ✅ **Printer Monitoring** - Bambu Lab telemetry

---

## 🚀 Ready to Auto-Deploy?

**Tell me:**
1. Did you add the InfluxDB data source in Grafana?
2. What's your InfluxDB database/bucket name?
3. Do you want me to create the Grafana API deployment script?

**Then I'll automatically:**
- Generate all 4 dashboard JSONs
- Deploy via Grafana API
- Configure alerts
- Set up auto-refresh
- Create navigation links

**All without you clicking anything!** 🎨

---

## Current Files Ready

**Agent 4 created:**
- `agents/config/nocv3_blueprint.json` - Dashboard architecture

**Agent 3 created:**
- `agents/config/collector_ha_config.yaml` - Data collection config

**Ready to convert these to deployable Grafana dashboards!**

---

**Next:** Tell me you're ready and I'll auto-deploy everything! 🚀

