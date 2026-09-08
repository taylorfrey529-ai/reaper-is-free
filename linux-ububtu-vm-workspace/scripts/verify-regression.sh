#!/usr/bin/env bash
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

required=(
  README.md
  RECALL.md
  BOOT-HANDOFF.md
  restore.sh
  SHA256SUMS
  BINARY-MANIFEST.md
  RUNTIME-BUNDLES.md
  verify-runtime-bundles.sh
  source-snapshot.tar.gz.b64
  scripts/start-live-session.py
)
for rel in "${required[@]}"; do
  [ -e "$HERE/$rel" ] || { echo "MISSING $rel" >&2; exit 1; }
done

bash -n "$HERE/restore.sh"
bash -n "$HERE/verify-runtime-bundles.sh"
python3 -m py_compile "$HERE/scripts/start-live-session.py"

# This is the core transport regression test: restore.sh must succeed whether
# the historical .b64 path contains raw gzip bytes or textual base64.
bash "$HERE/restore.sh" "$TMP/raw-or-current" >/dev/null
ARCHIVE="$TMP/raw-or-current/source-snapshot.tar.gz"
EXPECTED=$(awk '/source-snapshot.tar.gz/{print $1; exit}' "$HERE/SHA256SUMS")
ACTUAL=$(sha256sum "$ARCHIVE" | awk '{print $1}')
[ "$EXPECTED" = "$ACTUAL" ] || { echo "Snapshot checksum regression" >&2; exit 1; }

# Re-encode the verified archive as text base64 and prove the same restore path.
COMPAT="$TMP/compat"
mkdir -p "$COMPAT"
cp "$HERE/restore.sh" "$HERE/SHA256SUMS" "$COMPAT/"
base64 "$ARCHIVE" > "$COMPAT/source-snapshot.tar.gz.b64"
bash "$COMPAT/restore.sh" "$TMP/base64" >/dev/null

for token in \
  'linux_audio_mode=1' \
  'alsa_indev=apollo_spdif' \
  'alsa_outdev=apollo_spdif' \
  'linux_audio_srate=48000' \
  'linux_audio_bsize=256' \
  'linux_audio_bufs=3' \
  'linux_audio_nch_in=2' \
  'linux_audio_nch_out=2'; do
  grep -Rqs -- "$token" "$TMP/raw-or-current" || {
    echo "Continuity token missing from restored snapshot: $token" >&2
    exit 1
  }
done

echo "linux-ububtu-vm-workspace regression verification PASSED"
