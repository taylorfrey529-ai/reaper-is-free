#!/usr/bin/env bash
set -euo pipefail

ROOT="${SUNWELL_ROOT:-/mnt/data/ubuntu-desktop-workspace}"
SRC=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DEST="$ROOT/vm-v1.1.0"

[ -d "$ROOT" ] || { echo "FAIL: workspace root missing: $ROOT" >&2; exit 20; }
mkdir -p "$DEST/bin" "$DEST/config" "$ROOT/config/REAPER/Scripts/Sunwell" "$ROOT/bin" "$ROOT/logs" "$ROOT/config/sunwell"

install -m 0644 "$SRC/config/permanence-v1.1.0.json" "$DEST/config/permanence-v1.1.0.json"
install -m 0755 "$SRC/bin/verify-permanence-v1.1.0.sh" "$DEST/bin/verify-permanence-v1.1.0.sh"
install -m 0755 "$SRC/bin/verify-permanence.sh" "$DEST/bin/verify-permanence.sh"
install -m 0755 "$SRC/bin/enter-v1.1.0.sh" "$DEST/bin/enter-v1.1.0.sh"
install -m 0755 "$SRC/bin/sunwell-gateway-v1.1.0.sh" "$ROOT/bin/sunwell-gateway-v1.1.0.sh"
install -m 0644 "$SRC/reaper/Scripts/Sunwell/Sunwell_VM_v1_1_0_Regression.lua" "$ROOT/config/REAPER/Scripts/Sunwell/Sunwell_VM_v1_1_0_Regression.lua"

ln -sfn "$DEST/bin/enter-v1.1.0.sh" "$ROOT/bin/enter-vm-v1.1.0.sh"
printf '%s\n' "vm-v1.1.0 candidate - owner promotion required" > "$ROOT/config/sunwell/vm-version-v1.1.0.txt"

echo "Installed vm-v1.1.0 gate/launcher files only. Instrument/model/project bytes were not modified."
echo "Running full permanence verification..."
bash "$DEST/bin/verify-permanence-v1.1.0.sh"
echo "PASS: vm-v1.1.0 files installed and full gate passed."
echo "Entry command: $ROOT/bin/enter-vm-v1.1.0.sh"
