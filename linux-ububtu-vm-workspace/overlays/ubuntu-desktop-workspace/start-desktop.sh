#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/data/ubuntu-desktop-workspace
DISPLAY_NUM=${DISPLAY_NUM:-88}
SCREEN_WIDTH=${SCREEN_WIDTH:-2560}
SCREEN_HEIGHT=${SCREEN_HEIGHT:-1440}
SCREEN_DEPTH=${SCREEN_DEPTH:-24}
export DISPLAY=:$DISPLAY_NUM
export WORKSPACE_WIDTH="$SCREEN_WIDTH"
export WORKSPACE_HEIGHT="$SCREEN_HEIGHT"
export WORKSPACE_DEPTH="$SCREEN_DEPTH"
export HOME="$ROOT/home"
export XDG_CONFIG_HOME="$ROOT/config"
mkdir -p "$ROOT/run" "$ROOT/logs" "$HOME"

# Reuse a healthy session if one is already running.
if [ -f "$ROOT/run/xvfb.pid" ] && kill -0 "$(cat "$ROOT/run/xvfb.pid")" 2>/dev/null && xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
  echo "Ubuntu workspace desktop already running on $DISPLAY"
  exit 0
fi

rm -f /tmp/.X${DISPLAY_NUM}-lock /tmp/.X11-unix/X${DISPLAY_NUM} 2>/dev/null || true
Xvfb "$DISPLAY" -screen 0 "${SCREEN_WIDTH}x${SCREEN_HEIGHT}x${SCREEN_DEPTH}" -nolisten tcp -ac >"$ROOT/logs/xvfb.log" 2>&1 &
echo $! > "$ROOT/run/xvfb.pid"
for i in $(seq 1 50); do xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 && break; sleep 0.1; done
xdpyinfo -display "$DISPLAY" >/dev/null

openbox --config-file "$ROOT/config/openbox/rc.xml" >"$ROOT/logs/openbox.log" 2>&1 &
echo $! > "$ROOT/run/openbox.pid"
sleep 0.4
python3 "$ROOT/desktop_shell.py" >"$ROOT/logs/desktop-shell.log" 2>&1 &
echo $! > "$ROOT/run/desktop-shell.pid"

for i in $(seq 1 60); do
  if DISPLAY="$DISPLAY" xwininfo -root -tree 2>/dev/null | grep -q '"Ubuntu Workspace Desktop"'; then
    echo "$DISPLAY" > "$ROOT/run/display"
    echo "Ubuntu workspace desktop started on $DISPLAY"
    exit 0
  fi
  sleep 0.15
done

echo 'Desktop shell did not become ready.' >&2
exit 1
