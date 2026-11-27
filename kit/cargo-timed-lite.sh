#!/usr/bin/env bash
# Portable single-queue Cargo wrapper with flock serialization and wall/RAM logging.
# Usage: cargo-timed-lite nextest run -p my-crate --lib my_test
set -euo pipefail

LOCK_FILE="${CARGO_QUEUE_LOCK:-/tmp/cargo-agent.lock}"
LOG_DIR="${CARGO_TIMINGS_DIR:-$HOME/.cache/cargo-timings}"
mkdir -p "$LOG_DIR"

start_queue=$(date +%s%3N)
exec 9>"$LOCK_FILE"
flock 9
start_run=$(date +%s%3N)
queue_ms=$((start_run - start_queue))

set +e
/usr/bin/time -f "rss_kb=%M cpu_pct=%P" -o "$LOG_DIR/.last_time" cargo "$@"
exit_code=$?
set -e

end_run=$(date +%s%3N)
wall_ms=$((end_run - start_run))
stats=$(cat "$LOG_DIR/.last_time" 2>/dev/null || echo "rss_kb=0 cpu_pct=0%")

printf '{"ts":"%s","cmd":"%s","exit":%d,"wall_ms":%d,"queue_ms":%d,"stats":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${1:-cargo}" "$exit_code" "$wall_ms" "$queue_ms" "$stats" \
  >> "$LOG_DIR/runs.jsonl"

exit "$exit_code"
