#!/usr/bin/env bash
set -euo pipefail

ROOT=${SUNWELL_ROOT:-/mnt/data/ubuntu-desktop-workspace}
HERE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
MANIFEST=${VM110_MANIFEST:-$HERE/config/permanence-v1.1.0.json}
VERIFY="$HERE/bin/verify-permanence.sh"
LIVE="$HERE/bin/verify-live.sh"
GATEWAY="$ROOT/bin/sunwell-gateway.sh"

PROJECT=$(python3 - "$ROOT" "$MANIFEST" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
m = json.loads(Path(sys.argv[2]).read_text())
print(root / m["project"]["path"])
PY
)

"$VERIFY"

if [ ! -x "$GATEWAY" ]; then
  echo "VM-V1.1.0 LAUNCH: FAIL - missing executable $GATEWAY" >&2
  exit 8
fi

export SUNWELL_CANONICAL_PROJECT="$PROJECT"
export SUNWELL_REGRESSION_GATE=1
"$GATEWAY" start
"$LIVE"

cat <<EOF
VM-V1.1.0 LAUNCH: PASS
Project: $PROJECT
Policy: fail-closed / verify-only / no automatic download or reinstall
Owner release gate: retained
EOF
