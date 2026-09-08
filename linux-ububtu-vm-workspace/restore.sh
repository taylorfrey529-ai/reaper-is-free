#!/usr/bin/env bash
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OUT=${1:-./linux-ububtu-vm-workspace-restored}
PAYLOAD="$HERE/source-snapshot.tar.gz.b64"
ARCHIVE="$OUT/source-snapshot.tar.gz"

mkdir -p "$OUT"
[ -f "$PAYLOAD" ] || { echo "Missing snapshot payload: $PAYLOAD" >&2; exit 1; }

# Historical compatibility: this repository has carried the snapshot both as
# textual base64 and as raw gzip bytes under the same .b64 filename. Detect the
# actual bytes instead of trusting the suffix so fresh-workspace restore cannot
# regress on packaging format.
magic=$(dd if="$PAYLOAD" bs=2 count=1 2>/dev/null | od -An -tx1 | tr -d ' \n')
if [ "$magic" = "1f8b" ]; then
  cp "$PAYLOAD" "$ARCHIVE"
  format=raw-gzip
else
  base64 -d "$PAYLOAD" > "$ARCHIVE" || {
    echo "Snapshot payload is neither raw gzip nor valid base64: $PAYLOAD" >&2
    exit 1
  }
  format=base64
fi

EXPECTED="$(awk '/source-snapshot.tar.gz/{print $1; exit}' "$HERE/SHA256SUMS")"
[ -n "$EXPECTED" ] || { echo "Missing source-snapshot.tar.gz checksum in $HERE/SHA256SUMS" >&2; exit 1; }
ACTUAL="$(sha256sum "$ARCHIVE" | awk '{print $1}')"
[ "$EXPECTED" = "$ACTUAL" ] || {
  echo "SHA256 mismatch" >&2
  echo "expected: $EXPECTED" >&2
  echo "actual:   $ACTUAL" >&2
  exit 1
}

tar -tzf "$ARCHIVE" >/dev/null
tar -C "$OUT" -xzf "$ARCHIVE"
printf 'Restored source/config snapshot to: %s\n' "$OUT"
printf 'Snapshot transport detected: %s\n' "$format"
echo "Third-party/runtime binaries and large media are intentionally excluded; see README.md and RUNTIME-BUNDLES.md."
