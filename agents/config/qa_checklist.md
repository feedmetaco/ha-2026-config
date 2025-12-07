
# NOC Observability QA Checklist

## 📊 Chart Accuracy
- [ ] All power sensors show "W" or "kW"
- [ ] All energy sensors show "Wh" or "kWh"
- [ ] Temperature sensors show "°C" or "°F"
- [ ] Network speeds show "Mbps" or "Gbps"
- [ ] Cost values show "$" or currency symbol

## 🔍 Timezone Consistency
- [ ] HA timezone matches local timezone
- [ ] Grafana timezone set correctly
- [ ] No unexpected time shifts in data

## 📈 Data Gaps
- [ ] No sensors stuck in "unavailable"
- [ ] No sensors with stale data (>1 hour old)
- [ ] Missing data alerts configured

## 🔗 Drilldowns
- [ ] All dashboard links resolve correctly
- [ ] Variables pass through drilldowns
- [ ] Back navigation works

## ⚙️ Control Safety
- [ ] Dangerous actions require confirmation
- [ ] Cooldown periods enforced
- [ ] All actions audit logged

## 🚨 Known-Good Thresholds
| Metric | Min | Max | Unit | Critical |
|--------|-----|-----|------|----------|
| Total Power | 0 | 10000 | W | Yes |
| Printer Power | 0 | 500 | W | No |
| Internet Ping | 0 | 200 | ms | Yes |
| Download Speed | 10 | 10000 | Mbps | Yes |
| Daily Cost | 0 | 100 | $ | No |
