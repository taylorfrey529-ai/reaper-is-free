#!/usr/bin/env bash
set -euo pipefail

ROOT="${SUNWELL_ROOT:-/mnt/data/ubuntu-desktop-workspace}"
SELF_PATH=$(readlink -f "$0")\nSELF_DIR=$(CDPATH= cd -- "$(dirname -- "$SELF_PATH")" && pwd)
V110_GATE="$SELF_DIR/verify-permanence-v1.1.0.sh"
GATEWAY="$ROOT/bin/sunwell-gateway-v1.1.0.sh"
LOG="$ROOT/logs/vm-v1.1.0-enter.log"
mkdir -p "$ROOT/logs"

{
  echo "VM v1.1.0 ENTER"
  date -u '+UTC %Y-%m-%dT%H:%M:%SZ'
  echo "root=$ROOT"
  echo "policy=verify-only/fail-closed"
} >> "$LOG"

[ -f "$V110_GATE" ] || { echo "FAIL: vm-v1.1.0 permanence gate missing: $V110_GATE" | tee -a "$LOG" >&2; exit 11; }
[ -x "$GATEWAY" ] || { echo "FAIL: vm-v1.1.0 gateway missing: $GATEWAY" | tee -a "$LOG" >&2; exit 12; }

bash "$V110_GATE" 2>&1 | tee -a "$LOG"
echo "PASS: vm-v1.1.0 pre-launch gate admitted runtime" | tee -a "$LOG"
exec "$GATEWAY"
