
# UniFi API Integration for Home Assistant

## REST Commands for Port Control
```yaml
rest_command:
  unifi_set_poe:
    url: "https://{{ host }}/proxy/network/api/s/{{ site }}/rest/device/{{ device_id }}"
    method: PUT
    verify_ssl: false
    payload: '{"port_overrides":[{"port_idx":{{ port }},"poe_mode":"{{ mode }}"}]}'
```

## Quick Start
```bash
# Test UniFi API connection
curl -k -X POST https://192.168.1.1/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  -c cookies.txt
```
