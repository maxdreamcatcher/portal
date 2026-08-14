#!/usr/bin/env bash
# tools/smoke-tests/run-smoke-tests.sh
# Portal‑OS v1 smoke test
# Usage:
#   ./tools/smoke-tests/run-smoke-tests.sh [BASE_URL] [KV_TEST_KEY]
# Example:
#   ./tools/smoke-tests/run-smoke-tests.sh https://portal-os-v1.example.workers.dev test

set -euo pipefail

BASE_URL="${1:-http://localhost:8787}"   # override with deployed worker URL
KV_TEST_KEY="${2:-test}"

WORKER_FILE="dist/worker.js"

echo "== Portal‑OS v1 smoke test =="
echo "BASE_URL = $BASE_URL"
echo

# 1) Confirm worker bundle exists
echo -n "1) Check $WORKER_FILE exists... "
if [[ -f "$WORKER_FILE" ]]; then
  echo "OK"
else
  echo "MISSING: $WORKER_FILE"
  exit 2
fi
echo

# 2) Wrangler dry-run publish (shows binding errors if any)
echo "2) Wrangler publish --dry-run"
if command -v npx >/dev/null 2>&1; then
  if npx --no-install wrangler publish --dry-run --config wrangler.toml 2>&1 | tee /tmp/wrangler-dry-run.log; then
    echo "wrangler dry-run: OK"
  else
    echo "wrangler dry-run: FAILED (see /tmp/wrangler-dry-run.log)"
    exit 3
  fi
else
  echo "npx not found in PATH; skipping wrangler dry-run. Install Node + wrangler to run this check."
fi
echo

# helper to request an endpoint and show status + short body
request() {
  local path="$1"
  local label="$2"
  echo -n "Requesting ${label} -> ${BASE_URL}${path} ... "
  http_code=$(curl -sS -w "%{http_code}" -o /tmp/resp_body "$BASE_URL${path}" || true)
  if [[ -z "$http_code" ]]; then
    echo "NO RESPONSE"
    return 1
  fi
  echo "HTTP ${http_code}"
  echo "Body (first 400 chars):"
  head -c 400 /tmp/resp_body || true
  echo
  return 0
}

# 3) Test top-level endpoints
echo "3) Hit health endpoints"
request "/" "root (status JSON)" || exit 4
echo "----"
request "/tick" "tick" || echo "tick endpoint may not be available"
echo "----"
request "/kv/${KV_TEST_KEY}" "kv test" || echo "kv test may fail (check kv key exists / permissions)"
echo

# 4) Durable Object quick check (best-effort)
echo "4) Durable Object check (best-effort):"
# If your DO exposes specific endpoints for testing, put them here.
# Example placeholder:
DO_TEST_PATH="/do/health"   # adjust to your DO test path if you have one
if curl -sS -o /dev/null -w "%{http_code}" "$BASE_URL${DO_TEST_PATH}" >/dev/null 2>&1; then
  request "${DO_TEST_PATH}" "durable object"
else
  echo "DO test path ${DO_TEST_PATH} returned no response (this is optional; update the script to use your DO test endpoint)."
fi

echo
echo "Smoke test completed. If any step failed above, inspect the output and the wrangler dry-run log (/tmp/wrangler-dry-run.log)."
