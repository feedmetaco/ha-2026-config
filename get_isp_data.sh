#!/bin/bash

# Read API key from secrets.yaml
API_KEY=$(grep '^ui_api_key:' /config/secrets.yaml | awk '{print $2}')

# Check that API key was extracted
if [ -z "$API_KEY" ]; then
  echo "❌ API key not found in /config/secrets.yaml"
  exit 1
fi

# Call UniFi API, extract metrics, save to JSON
curl -s -H "Accept: application/json" \
     -H "X-API-Key: $API_KEY" \
     "https://api.ui.com/ea/isp-metrics/1h" |
  jq '.data[0].periods[0].data.wan |
      {
        isp: .ispName,
        download_bps: .download_kbps * 1000,
        upload_bps: .upload_kbps * 1000,
        avg_latency: .avgLatency,
        max_latency: .maxLatency,
        packet_loss: .packetLoss,
        uptime: .uptime
      }' > /config/www/isp_metrics.json
