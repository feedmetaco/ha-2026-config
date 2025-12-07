#!/bin/bash

# Simple DNS Response Time Test
# Usage: dns_test_simple.sh <dns_server> <test_domain>
# Returns: response time in milliseconds or 9999 if failed

DNS_SERVER=${1:-"1.1.1.1"}
TEST_DOMAIN=${2:-"google.com"}

# Use dig to test DNS response time with 2-second timeout
RESPONSE_TIME=$(dig @$DNS_SERVER $TEST_DOMAIN +time=2 +tries=1 2>/dev/null | grep "Query time:" | awk '{print $4}')

# Return response time or 9999 if failed
if [[ -n "$RESPONSE_TIME" && "$RESPONSE_TIME" =~ ^[0-9]+$ ]]; then
    echo $RESPONSE_TIME
else
    echo 9999
fi
