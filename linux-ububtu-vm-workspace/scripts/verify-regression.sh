#!/usr/bin/env bash
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

required=(
  README.md RECALL.md SNAPSHOT-INTEGRITY.md BOOT-HANDOFF-CURRENT.md restore.sh SHA256SUMS
  BINARY-MANIFEST.md RUNTIME-BUNDLES.md verify-runtime-bundles.sh
  source-snapshot.parts/SHA256SUMS scripts/start-live-session.py
)
for rel in "${required[@]}"; do
  [ -e "$HERE/$rel" ] || { echo "MISSING $rel" >&2; exit 1; }
done

bash -n "$HERE/restore.sh"
bash -n "$HERE/verify-runtime-bundles.sh"
python3 -m py_compile "$HERE/scripts/start-live-session.py"
(cd "$HERE/source-snapshot.parts" && sha256sum -c SHA256SUMS)

bash "$HERE/restore.sh" "$TMP/restored" >/dev/null
ARCHIVE="$TMP/restored/source-snapshot.tar.gz"
EXPECTED=$(awk '$2=="source-snapshot.tar.gz"{print $1; exit}' "$HERE/SHA256SUMS")
ACTUAL=$(sha256sum "$ARCHIVE" | awk '{print $1}')
[ "$EXPECTED" = "$ACTUAL" ] || { echo "Current source snapshot hash regression" >&2; exit 1; }
tar -tzf "$ARCHIVE" >/dev/null

for token in \
  'linux_audio_mode=1' \
  'alsa_indev=apollo_spdif' \
  'alsa_outdev=apollo_spdif' \
  'linux_audio_srate=48000' \
  'linux_audio_bsize=256' \
  'linux_audio_bufs=3' \
  'linux_audio_nch_in=2' \
  'linux_audio_nch_out=2'; do
  grep -Rqs -- "$token" "$TMP/restored" || {
    echo "Continuity token missing from restored snapshot: $token" >&2
    exit 1
  }
done

# The historical corrupt transport must never be admitted as the current source snapshot.
REJECTED=$(awk '$2=="source-snapshot.tar.gz.b64.rejected-corrupt-github-blob"{print $1; exit}' "$HERE/SHA256SUMS")
[ "$ACTUAL" != "$REJECTED" ] || { echo "Rejected corrupt transport was re-admitted" >&2; exit 1; }

echo "linux-ububtu-vm-workspace regression verification PASSED"
