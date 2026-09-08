#!/usr/bin/env bash
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OUT=${1:-./linux-ububtu-vm-workspace-restored}
mkdir -p "$OUT"
base64 -d "$HERE/source-snapshot.tar.gz.b64" > "$OUT/source-snapshot.tar.gz"
EXPECTED="$(awk '/source-snapshot.tar.gz/{print $1; exit}' "$HERE/SHA256SUMS")"
ACTUAL="$(sha256sum "$OUT/source-snapshot.tar.gz" | awk '{print $1}')"
[ "$EXPECTED" = "$ACTUAL" ] || { echo "SHA256 mismatch" >&2; exit 1; }
tar -C "$OUT" -xzf "$OUT/source-snapshot.tar.gz"
echo "Restored source/config snapshot to: $OUT"
echo "Third-party/runtime binaries and large media are intentionally excluded; see README.md."
