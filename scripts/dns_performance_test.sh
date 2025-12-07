#!/bin/bash

# DNS Performance Testing Script for Home Assistant
# Tests multiple DNS servers and returns response times in JSON format

# Define DNS servers to test
declare -A DNS_SERVERS=(
    ["cloudflare_primary"]="1.1.1.1"
    ["cloudflare_secondary"]="1.0.0.1" 
    ["google_primary"]="8.8.8.8"
    ["google_secondary"]="8.8.4.4"
    ["local_router"]="192.168.10.1"
)

# Test domains (mix of popular and infrastructure sites)
TEST_DOMAINS=("google.com" "github.com" "home-assistant.io")

# Output JSON structure
echo "{"

first_server=true
for server_name in "${!DNS_SERVERS[@]}"; do
    server_ip="${DNS_SERVERS[$server_name]}"
    
    if [ "$first_server" = false ]; then
        echo ","
    fi
    first_server=false
    
    echo "  \"$server_name\": {"
    echo "    \"server_ip\": \"$server_ip\","
    
    # Test each domain and calculate average response time
    total_time=0
    success_count=0
    
    for domain in "${TEST_DOMAINS[@]}"; do
        # Use dig to query DNS server with timeout
        response_time=$(dig @$server_ip $domain +time=2 +tries=1 | grep "Query time:" | awk '{print $4}' 2>/dev/null)
        
        if [[ -n "$response_time" && "$response_time" =~ ^[0-9]+$ ]]; then
            total_time=$((total_time + response_time))
            success_count=$((success_count + 1))
        fi
    done
    
    # Calculate average response time
    if [ $success_count -gt 0 ]; then
        avg_time=$((total_time / success_count))
        echo "    \"avg_response_ms\": $avg_time,"
        echo "    \"success_rate\": $(echo "scale=2; $success_count / ${#TEST_DOMAINS[@]} * 100" | bc),"
        echo "    \"status\": \"online\""
    else
        echo "    \"avg_response_ms\": 9999,"
        echo "    \"success_rate\": 0,"
        echo "    \"status\": \"offline\""
    fi
    
    echo "  }"
done

echo "}"
