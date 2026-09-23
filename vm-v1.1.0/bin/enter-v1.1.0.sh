#!/usr/bin/env bash
set -euo pipefail

ROOT="${SUNWELL_ROOT:-/mnt/data/ubuntu-desktop-workspace}"
SELF_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
LEGACY_GATE="$ROOT/bin/verify-sunwell-assets.sh"
V110_GATE="$SELF_DIR/verify-permanence-v1.1.0.sh"
GATEWAY="$ROOT/bin/sunwell-gateway.sh"
LOG="$ROOT/logs/vm-v1.1.0-enter.log"
mkdir -p "$ROOT/logs"

{
  echo "VM v1.1.0 ENTER"
  date -u '+UTC %Y-%m-%dT%H:%M:%SZ'
  echo "root=$ROOT"
  echo "policy=verify-only/fail-closed"
} >> "$LOG"

if [ ! -x "$LEGACY_GATE" ]; then
  echo "FAIL: legacy Sunwell asset gate missing or not executable: $LEGACY_GATE" | tee -a "$LOG" >&2
  exit 10
fi
if [ ! -f "$V110_GATE" ]; then
  echo "FAIL: vm-v1.1.0 permanence gate missing: $V110_GATE" | tee -a "$LOG" >&2
  exit 11
fi
if [ ! -x "$GATEWAY" ]; then
  echo "FAIL: Sunwell gateway missing or not executable: $GATEWAY" | tee -a "$LOG" >&2
  exit 12
fi

"$LEGACY_GATE" 2>&1 | tee -a "$LOG"
bash "$V110_GATE" 2>&1 | tee -a "$LOG"

echo "PASS: both pre-launch gates admitted vm-v1.1.0" | tee -a "$LOG"
exec "$GATEWAY" "${1:-start}"
