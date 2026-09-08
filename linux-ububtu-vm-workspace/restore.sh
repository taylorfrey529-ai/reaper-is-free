#!/usr/bin/env bash
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OUT=${1:-./linux-ububtu-vm-workspace-restored}
ARCHIVE="$OUT/source-snapshot.tar.gz"
PARTS="$HERE/source-snapshot.parts"
LEGACY_PAYLOAD="$HERE/source-snapshot.tar.gz.b64"

mkdir -p "$OUT"
current_hash=$(awk '$2=="source-snapshot.tar.gz"{print $1; exit}' "$HERE/SHA256SUMS")
historical_hash=$(awk '$2=="source-snapshot.tar.gz.historical-record"{print $1; exit}' "$HERE/SHA256SUMS")
[ -n "$current_hash" ] || { echo "Missing current source snapshot hash" >&2; exit 1; }

if [ -d "$PARTS" ] && compgen -G "$PARTS/part-*.b64" >/dev/null; then
  (cd "$PARTS" && sha256sum -c SHA256SUMS)
  cat "$PARTS"/part-*.b64 | base64 -d > "$ARCHIVE"
  format=split-base64
else
  # Compatibility fallback for an externally supplied historical payload. The
  # repository's retired pointer file is intentionally not valid base64/gzip.
  [ -f "$LEGACY_PAYLOAD" ] || { echo "No source snapshot payload found" >&2; exit 1; }
  magic=$(dd if="$LEGACY_PAYLOAD" bs=2 count=1 2>/dev/null | od -An -tx1 | tr -d ' \n')
  if [ "$magic" = "1f8b" ]; then
    cp "$LEGACY_PAYLOAD" "$ARCHIVE"
    format=legacy-raw-gzip
  else
    base64 -d "$LEGACY_PAYLOAD" > "$ARCHIVE" || {
      echo "No valid source snapshot parts and legacy payload is not valid base64" >&2
      exit 1
    }
    format=legacy-base64
  fi
fi

actual=$(sha256sum "$ARCHIVE" | awk '{print $1}')
if [ "$actual" = "$current_hash" ]; then
  identity=current-reconstructed-source-snapshot
elif [ -n "$historical_hash" ] && [ "$actual" = "$historical_hash" ]; then
  identity=historical-source-snapshot
else
  echo "Source snapshot SHA256 mismatch" >&2
  echo "current:    $current_hash" >&2
  echo "historical: ${historical_hash:-unavailable}" >&2
  echo "actual:     $actual" >&2
  exit 1
fi

tar -tzf "$ARCHIVE" >/dev/null
tar -C "$OUT" -xzf "$ARCHIVE"
printf 'Restored source/config snapshot to: %s\n' "$OUT"
printf 'Snapshot transport: %s\n' "$format"
printf 'Snapshot identity: %s (%s)\n' "$identity" "$actual"
echo "Runtime binaries/media remain external; verify RUNTIME-BUNDLES.md before reconstruction."
