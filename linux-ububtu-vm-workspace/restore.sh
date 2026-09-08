#!/usr/bin/env bash
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OUT=${1:-./linux-ububtu-vm-workspace-restored}
PAYLOAD="$HERE/source-snapshot.tar.gz.b64"
ARCHIVE="$OUT/source-snapshot.tar.gz"

mkdir -p "$OUT"
[ -f "$PAYLOAD" ] || { echo "Missing snapshot payload: $PAYLOAD" >&2; exit 1; }

legacy_hash=$(awk '$2=="source-snapshot.tar.gz"{print $1; exit}' "$HERE/SHA256SUMS")
transport_hash=$(awk '$2=="source-snapshot.tar.gz.b64"{print $1; exit}' "$HERE/SHA256SUMS")
[ -n "$legacy_hash" ] || { echo "Missing legacy source archive hash" >&2; exit 1; }
[ -n "$transport_hash" ] || { echo "Missing committed transport hash" >&2; exit 1; }

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

actual=$(sha256sum "$ARCHIVE" | awk '{print $1}')
case "$actual" in
  "$legacy_hash") identity=historical-source-archive ;;
  "$transport_hash") identity=committed-repository-transport ;;
  *)
    echo "SHA256 mismatch" >&2
    echo "accepted historical source archive: $legacy_hash" >&2
    echo "accepted repository transport:     $transport_hash" >&2
    echo "actual:                            $actual" >&2
    exit 1
    ;;
esac

tar -tzf "$ARCHIVE" >/dev/null
tar -C "$OUT" -xzf "$ARCHIVE"
printf 'Restored source/config snapshot to: %s\n' "$OUT"
printf 'Snapshot transport detected: %s\n' "$format"
printf 'Snapshot identity accepted as: %s (%s)\n' "$identity" "$actual"
echo "Third-party/runtime binaries and large media are intentionally excluded; see README.md, SNAPSHOT-INTEGRITY.md, and RUNTIME-BUNDLES.md."
