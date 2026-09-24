#!/usr/bin/env bash
set -euo pipefail

ROOT="${SUNWELL_ROOT:-/mnt/data/ubuntu-desktop-workspace}"
PROJECT="${SUNWELL_CANONICAL_PROJECT:-$ROOT/projects/Ultra-Realism/Ultra-Realism-seed16-g1-NAM-retained.RPP}"
DISPLAY_NUM="${DISPLAY_NUM:-88}"
export HOME="$ROOT/home"
export XDG_CONFIG_HOME="$ROOT/config"
export DISPLAY=":$DISPLAY_NUM"
export XAUTHORITY="${XAUTHORITY:-$ROOT/home/.X11/xauthority-$DISPLAY_NUM}"
export VST3_PATH="${VST3_PATH:-$HOME/.vst3}"
export LV2_PATH="${LV2_PATH:-$HOME/.lv2}"
LOG="$ROOT/logs/vm-v1.1.0-gateway.log"
mkdir -p "$ROOT/logs"

{
  echo "VM v1.1.0 GATEWAY"
  date -u '+UTC %Y-%m-%dT%H:%M:%SZ'
  echo "display=$DISPLAY"
  echo "project=$PROJECT"
  echo "policy=preserve-live-session/fail-closed/no-cpu-downgrade"
} >> "$LOG"

if ! xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
  if [ -x "$ROOT/start-desktop.sh" ]; then
    "$ROOT/start-desktop.sh" >>"$LOG" 2>&1
  fi
  for _ in $(seq 1 80); do
    xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 && break
    sleep 0.25
  done
fi
xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 || { echo "FAIL: authenticated X11 unavailable" | tee -a "$LOG" >&2; exit 31; }

dimensions=$(xdpyinfo -display "$DISPLAY" 2>/dev/null | sed -n 's/.*dimensions:[[:space:]]*\([0-9]*x[0-9]*\).*/\1/p' | head -1)
[ "$dimensions" = "2560x1440" ] || { echo "FAIL: display geometry=$dimensions expected=2560x1440" | tee -a "$LOG" >&2; exit 32; }

[ -f "$PROJECT" ] || { echo "FAIL: project missing $PROJECT" | tee -a "$LOG" >&2; exit 33; }
[ -x "$ROOT/apps/REAPER/reaper" ] || { echo "FAIL: REAPER binary missing" | tee -a "$LOG" >&2; exit 34; }
[ -x /mnt/data/virtual-apollo/bin/start-apollo.sh ] || { echo "FAIL: Virtual Apollo missing" | tee -a "$LOG" >&2; exit 35; }

/mnt/data/virtual-apollo/bin/start-apollo.sh >>"$LOG" 2>&1

reaper_pid=$(pgrep -f "^$ROOT/apps/REAPER/reaper( |$)" | head -1 || true)
if [ -n "$reaper_pid" ]; then
  echo "REAPER already running pid=$reaper_pid; opening project in existing instance" | tee -a "$LOG"
  "$ROOT/apps/REAPER/reaper" -nonewinst "$PROJECT" >>"$LOG" 2>&1 &
else
  echo "cold-launching REAPER 7.79" | tee -a "$LOG"
  nohup "$ROOT/bin/launch-reaper.sh" "$PROJECT" >>"$LOG" 2>&1 &
fi

for _ in $(seq 1 120); do
  reaper_pid=$(pgrep -f "^$ROOT/apps/REAPER/reaper( |$)" | head -1 || true)
  [ -n "$reaper_pid" ] && break
  sleep 0.25
done
[ -n "$reaper_pid" ] || { echo "FAIL: REAPER did not start" | tee -a "$LOG" >&2; exit 36; }

visible=0
for _ in $(seq 1 120); do
  if command -v wmctrl >/dev/null 2>&1; then
    wmctrl -l 2>/dev/null | grep -Fq 'Ultra-Realism-seed16-g1-NAM-retained' && visible=1 && break
  else
    xwininfo -root -tree 2>/dev/null | grep -Fq 'Ultra-Realism-seed16-g1-NAM-retained' && visible=1 && break
  fi
  sleep 0.25
done
[ "$visible" -eq 1 ] || { echo "FAIL: retained project window not visible" | tee -a "$LOG" >&2; exit 37; }

echo "PASS: vm-v1.1.0 gateway admitted REAPER pid=$reaper_pid display=$DISPLAY geometry=$dimensions" | tee -a "$LOG"
/mnt/data/virtual-apollo/bin/status-apollo.sh 2>&1 | tee -a "$LOG" || true
