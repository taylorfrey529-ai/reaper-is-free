#!/usr/bin/env bash
set -euo pipefail

ROOT=${SUNWELL_ROOT:-/mnt/data/ubuntu-desktop-workspace}
DISPLAY_NUM=${DISPLAY_NUM:-88}
export DISPLAY=:$DISPLAY_NUM
export HOME="$ROOT/home"
export XDG_CONFIG_HOME="$ROOT/config"
REPORT=${1:-$ROOT/logs/vm-v1.1.0-live.txt}

mkdir -p "$(dirname "$REPORT")"
pass=0
fail=0
check() {
  local label=$1
  shift
  if "$@"; then
    printf '[PASS] %s\n' "$label" | tee -a "$REPORT"
    pass=$((pass+1))
  else
    printf '[FAIL] %s\n' "$label" | tee -a "$REPORT"
    fail=$((fail+1))
  fi
}

: > "$REPORT"
check "authenticated X11 :88" xdpyinfo -display "$DISPLAY"
check "display geometry 2560x1440" bash -c 'xdpyinfo -display "$1" 2>/dev/null | grep -q "dimensions: *2560x1440 pixels"' _ "$DISPLAY"
check "REAPER 7.79 process" pgrep -f '^/mnt/data/ubuntu-desktop-workspace/apps/REAPER/reaper( |$)'

pid=$(pgrep -f '^/mnt/data/ubuntu-desktop-workspace/apps/REAPER/reaper( |$)' | head -1 || true)
if [ -n "$pid" ] && [ -r "/proc/$pid/maps" ]; then
  check "sforzando mapped in REAPER" grep -qi 'sforzando' "/proc/$pid/maps"
  check "AVLDrums mapped in REAPER" grep -qi 'avldrums' "/proc/$pid/maps"
  check "NAM mapped in REAPER" grep -qi 'neural_amp_modeler' "/proc/$pid/maps"
else
  printf '[FAIL] REAPER process maps readable\n' | tee -a "$REPORT"
  fail=$((fail+1))
fi

if command -v wmctrl >/dev/null 2>&1; then
  windows=$(wmctrl -l 2>/dev/null || true)
  if printf '%s\n' "$windows" | grep -Fq 'Ultra-Realism-seed16-g1-NAM-retained'; then
    printf '[PASS] Ultra Realism NAM-retained project visible\n' | tee -a "$REPORT"
    pass=$((pass+1))
  else
    printf '[FAIL] Ultra Realism NAM-retained project visible\n' | tee -a "$REPORT"
    fail=$((fail+1))
  fi
  if printf '%s\n' "$windows" | grep -qiE 'missing.*(fx|plugin|sample)|project load warning'; then
    printf '[FAIL] no missing-plugin/sample warning window\n' | tee -a "$REPORT"
    fail=$((fail+1))
  else
    printf '[PASS] no missing-plugin/sample warning window\n' | tee -a "$REPORT"
    pass=$((pass+1))
  fi
else
  printf '[FAIL] wmctrl available for visible-project proof\n' | tee -a "$REPORT"
  fail=$((fail+1))
fi

APOLLO=/mnt/data/virtual-apollo
if [ -x "$APOLLO/bin/status-apollo.sh" ] && "$APOLLO/bin/status-apollo.sh" 2>/dev/null | grep -qiE 'RUNNING|ACTIVE|playback tap: (RUNNING|ACTIVE)'; then
  printf '[PASS] Virtual Apollo active\n' | tee -a "$REPORT"
  pass=$((pass+1))
else
  printf '[FAIL] Virtual Apollo active\n' | tee -a "$REPORT"
  fail=$((fail+1))
fi

printf 'SUMMARY pass=%d fail=%d\n' "$pass" "$fail" | tee -a "$REPORT"
printf 'policy=live proof only; no project mutation\n' | tee -a "$REPORT"
[ "$fail" -eq 0 ]
