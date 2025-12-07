# 📊 How to See Your Grafana Dashboards - Simple Steps

**Created:** 4 dashboards ready to import  
**Location:** `\\homeassistant.local\config\grafana_dashboards\`

---

## 🎯 **Simple 3-Step Process (5 Minutes)**

### Step 1: Add InfluxDB Data Source (2 minutes)

**Open Grafana:**
- Click this: http://192.168.10.6:8123/hassio/ingress/a0d7b954_grafana
- Login: admin / admin

**Add Data Source:**
1. Click **⚙️ Configuration** (gear icon on left sidebar)
2. Click **Data Sources**
3. Click blue **"Add data source"** button
4. Click **InfluxDB** (in the list)
5. Fill in:
   ```
   Name: HomeAssistant_InfluxDB
   URL: http://192.168.10.6:8086
   Database: homeassistant
   ```
6. Scroll down, click **"Save & Test"**
7. Should see: ✅ "Data source is working"

---

### Step 2: Import Dashboard #1 (1 minute)

**In Grafana:**
1. Click **+** (plus icon on left sidebar)
2. Click **"Import"**
3. Click **"Upload JSON file"**
4. Browse to: `C:\Users\Sami\Documents\ha-config\grafana_dashboards\noc_overview.json`
5. Click **"Load"**
6. Click **"Import"**

**✅ You'll see:** Your first dashboard with 2,479 entity overview!

---

### Step 3: Import Other 3 Dashboards (2 minutes)

**Repeat Step 2 for:**
- `sensor_analytics.json` - Your 968 sensors
- `network_power.json` - 449 switches + power
- `security_monitoring.json` - 256 binary sensors

---

## 📁 **Your 4 Dashboards**

### 1. 🏠 NOC Overview (`noc_overview.json`)
**What you'll see:**
- Total Entities count (2,479)
- Active Sensors (968)
- Switches (449)
- Cameras (29)
- Automations (40)
- System Health status

### 2. 📊 Sensor Analytics (`sensor_analytics.json`)
**What you'll see:**
- Top 20 most active sensors
- Sensor state changes over 24 hours
- Activity timeline for your 968 sensors

### 3. 🌐 Network & Power (`network_power.json`)
**What you'll see:**
- Total power consumption (live gauge)
- Switch states (449 switches as pie chart)
- Camera status (29 cameras)

### 4. 🔒 Security Monitoring (`security_monitoring.json`)
**What you'll see:**
- Entry point status (doors/windows from 256 binary sensors)
- Motion detection activity timeline
- Real-time security status

---

## ⚠️ **Agent Coordination Lock**

**Before importing, check:** `agents/AGENT_LOCK.json`

If another agent is working, coordinate first to avoid conflicts!

**Lock File Location:** `\\homeassistant.local\config\agents\AGENT_LOCK.json`

---

## 🚀 **Quick Access Links**

**Grafana:**
http://192.168.10.6:8123/hassio/ingress/a0d7b954_grafana

**InfluxDB:**
http://192.168.10.6:8086

**HA File Editor (to see dashboard files):**
http://192.168.10.6:8123/hassio/ingress/core_configurator
- Navigate to: grafana_dashboards/

---

## 💡 **Alternative: Auto-Import**

If you get Grafana API key, I can auto-import all 4 in 30 seconds!

**To get API key:**
1. In Grafana: Configuration → API Keys
2. Click "Add API key"
3. Name: AgentDeploy, Role: Admin
4. Copy the key
5. Give it to me
6. I'll auto-import everything!

---

## ✅ **Files Ready on Your HA**

**Location:** `\\homeassistant.local\config\grafana_dashboards\`

All 4 dashboard files are permanently stored on your HA server!

---

**Ready to import? Start with Step 1 (add InfluxDB data source)!** 📊

