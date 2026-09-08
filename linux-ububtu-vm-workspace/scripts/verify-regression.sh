#!/usr/bin/env bash
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
REPO_ROOT=$(CDPATH= cd -- "$HERE/.." && pwd)
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

for rel in \
  GOLDEN-MASTER.md \
  golden-master/MANIFEST.json \
  golden-master/SHA256SUMS \
  golden-master/TOOLCHAINS-PARTS.SHA256SUMS \
  golden-master/GRAPHICS-PARTS.SHA256SUMS \
  golden-master/verify-golden-master.sh; do
  [ -e "$REPO_ROOT/$rel" ] || { echo "MISSING $rel" >&2; exit 1; }
done

bash -n "$HERE/restore.sh"
bash -n "$HERE/verify-runtime-bundles.sh"
bash -n "$REPO_ROOT/golden-master/verify-golden-master.sh"
python3 -m py_compile "$HERE/scripts/start-live-session.py"
python3 -m json.tool "$REPO_ROOT/golden-master/MANIFEST.json" >/dev/null
(cd "$HERE/source-snapshot.parts" && sha256sum -c SHA256SUMS)

GM_ID=$(sha256sum "$REPO_ROOT/golden-master/SHA256SUMS" | awk '{print $1}')
[ "$GM_ID" = '74a13a11fe232bca5bd8a320d11ee0c2e17ce5c2e53d76c74ee9714276a95b1f' ] || {
  echo "Golden Master manifest identity regression: $GM_ID" >&2
  exit 1
}
grep -Fq "$GM_ID" "$REPO_ROOT/golden-master/MANIFEST.json"
grep -Fq "$GM_ID" "$REPO_ROOT/GOLDEN-MASTER.md"

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

REJECTED=$(awk '$2=="source-snapshot.tar.gz.b64.rejected-corrupt-github-blob"{print $1; exit}' "$HERE/SHA256SUMS")
[ "$ACTUAL" != "$REJECTED" ] || { echo "Rejected corrupt transport was re-admitted" >&2; exit 1; }

echo "linux-ububtu-vm-workspace regression verification PASSED"
