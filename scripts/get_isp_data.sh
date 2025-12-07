#!/bin/bash

# Call UniFi API and save extracted metrics
curl -s -H "Accept: application/json" \
     -H "X-API-Key: $(grep '^ui_api_key:' /config/secrets.yaml | cut -d' ' -f2 || echo '0LKGNrL76Re2DIFTBYwJQNFh3jqLwF7J')" \
     "https://api.ui.com/ea/isp-metrics/1h" \
| tee /config/www/isp_metrics_raw.json \
| jq '.data[0].periods[0].data.wan // {} | {
    isp: .ispName // "Unknown",
    download_bps: ((.download_kbps // 0) * 1000),
    upload_bps: ((.upload_kbps // 0) * 1000),
    avg_latency: .avgLatency // 0,
    max_latency: .maxLatency // 0,
    packet_loss: .packetLoss // 0,
    uptime: .uptime // 0
}' > /config/www/isp_metrics.json
