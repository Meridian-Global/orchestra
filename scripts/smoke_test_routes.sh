#!/bin/sh

BASE_URL="http://localhost:8000"
OPENAPI_URL="$BASE_URL/openapi.json"

check_status() {
  status="$(curl -s -o /tmp/orchestra_openapi_smoke.json -w "%{http_code}" "$OPENAPI_URL")"
  if [ "$status" = "200" ]; then
    echo "PASS: GET /openapi.json returned 200"
  else
    echo "FAIL: GET /openapi.json returned $status"
    exit 1
  fi
}

check_path() {
  path="$1"
  if curl -s "$OPENAPI_URL" | grep -F "\"$path\"" >/dev/null 2>&1; then
    echo "PASS: $path exists in OpenAPI output"
  else
    echo "FAIL: $path is missing from OpenAPI output"
    exit 1
  fi
}

check_status
check_path "/api/run"
check_path "/api/publish/linkedin"
check_path "/api/ideas/scan"

echo "PASS: route smoke test completed successfully"
