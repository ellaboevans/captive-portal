#!/bin/bash
set -e

NETWORK="captive-portal_portal_net"
AUTH_URL="http://192.168.100.3:3000"
NGINX_URL="http://192.168.100.2"
ADMIN_SECRET="changeme"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; ((PASS++)); }
fail() { echo "  FAIL: $1"; ((FAIL++)); }

run_test() {
  local name="$1"
  local expected="$2"
  shift 2
  local output
  output=$("$@" 2>&1) || true
  if echo "$output" | grep -q "$expected"; then
    pass "$name"
  else
    fail "$name (expected: $expected, got: $output)"
  fi
}

echo "=== Captive Portal Test Suite ==="
echo ""

echo "--- Splash page ---"
run_test "Splash page returns HTML" "<!DOCTYPE html>" \
  docker run --rm --network "$NETWORK" curlimages/curl:latest -s "$NGINX_URL/splash"

echo "--- Auth check (unauthenticated) ---"
run_test "Unauthenticated returns 401" "401" \
  docker run --rm --network "$NETWORK" curlimages/curl:latest -s -o /dev/null -w "%{http_code}" \
    -H "X-Real-IP: 10.0.0.5" "$AUTH_URL/api/check"

echo "--- Authenticate (click-through) ---"
run_test "Authenticate via click-through" "authenticated" \
  docker run --rm --network "$NETWORK" curlimages/curl:latest -s -X POST "$AUTH_URL/api/auth" \
    -H "Content-Type: application/json" -d '{"ip": "10.0.0.5"}'

echo "--- Auth check (authenticated) ---"
run_test "Authenticated returns 200" "200" \
  docker run --rm --network "$NETWORK" curlimages/curl:latest -s -o /dev/null -w "%{http_code}" \
    -H "X-Real-IP: 10.0.0.5" "$AUTH_URL/api/check"

echo "--- Voucher generation ---"
VOUCHER_RESPONSE=$(docker run --rm --network "$NETWORK" curlimages/curl:latest -s -X POST "$AUTH_URL/api/vouchers/generate" \
  -H "Authorization: Bearer $ADMIN_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"count": 3, "duration_hours": 2}')
VOUCHER_CODE=$(echo "$VOUCHER_RESPONSE" | grep -o '"vouchers":\["[^"]*' | grep -o '[A-Z0-9]\{8\}' | head -1)
if [ -n "$VOUCHER_CODE" ]; then
  pass "Voucher generated: $VOUCHER_CODE"
else
  fail "Voucher generation failed: $VOUCHER_RESPONSE"
fi

echo "--- Voucher authentication ---"
run_test "Authenticate via voucher" "authenticated" \
  docker run --rm --network "$NETWORK" curlimages/curl:latest -s -X POST "$AUTH_URL/api/auth" \
    -H "Content-Type: application/json" -d "{\"ip\": \"10.0.0.6\", \"voucher\": \"$VOUCHER_CODE\"}"

echo "--- Duplicate voucher ---"
run_test "Duplicate voucher rejected" "used" \
  docker run --rm --network "$NETWORK" curlimages/curl:latest -s -X POST "$AUTH_URL/api/auth" \
    -H "Content-Type: application/json" -d "{\"ip\": \"10.0.0.7\", \"voucher\": \"$VOUCHER_CODE\"}"

echo "--- Session list ---"
run_test "List sessions" "10.0.0.5" \
  docker run --rm --network "$NETWORK" curlimages/curl:latest -s \
    -H "Authorization: Bearer $ADMIN_SECRET" "$AUTH_URL/api/sessions"

echo "--- Revoke session ---"
run_test "Revoke session" "revoked" \
  docker run --rm --network "$NETWORK" curlimages/curl:latest -s -X POST "$AUTH_URL/api/revoke" \
    -H "Authorization: Bearer $ADMIN_SECRET" \
    -H "Content-Type: application/json" -d '{"ip": "10.0.0.5"}'

echo "--- Auth check (revoked) ---"
run_test "Revoked returns 401" "401" \
  docker run --rm --network "$NETWORK" curlimages/curl:latest -s -o /dev/null -w "%{http_code}" \
    -H "X-Real-IP: 10.0.0.5" "$AUTH_URL/api/check"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
