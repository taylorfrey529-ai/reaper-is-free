#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/data/ubuntu-desktop-workspace
export HOME="$ROOT/home"
export XDG_CONFIG_HOME="$ROOT/config"
export DISPLAY="${DISPLAY:-127.0.0.1:88}"
export XAUTHORITY="${XAUTHORITY:-$ROOT/run/xauthority}"
/mnt/data/virtual-apollo/bin/start-apollo.sh >/dev/null
if [ -f "$ROOT/scripts/install-astra-reaper-theme.py" ] && [ -f "$ROOT/apps/REAPER/InstallData/ColorThemes/Default_7.0.ReaperThemeZip" ]; then
  python3 "$ROOT/scripts/install-astra-reaper-theme.py"
fi
cd "$ROOT/apps/REAPER"
if [ -f "$ROOT/config/REAPER/libSwell.colortheme" ]; then
  cp "$ROOT/config/REAPER/libSwell.colortheme" "$ROOT/apps/REAPER/libSwell.colortheme"
fi
if [ -f "$ROOT/config/REAPER/ColorThemes/Astra_Workbench.ReaperThemeZip" ] && [ -d "$ROOT/apps/REAPER/InstallData/ColorThemes" ]; then
  cp "$ROOT/config/REAPER/ColorThemes/Astra_Workbench.ReaperThemeZip" "$ROOT/apps/REAPER/InstallData/ColorThemes/Astra_Workbench.ReaperThemeZip"
fi
exec "$ROOT/apps/REAPER/reaper" "$@"
