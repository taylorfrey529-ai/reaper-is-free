#!/usr/bin/env bash
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=${1:-/mnt/data}

verify_or_assemble() {
  archive=$1
  part_dir=$2
  part_sums=$3
  if [ -f "$ROOT/$archive" ]; then
    return 0
  fi
  if [ ! -d "$ROOT/$part_dir" ]; then
    printf 'MISSING  %s (and %s/)\n' "$ROOT/$archive" "$ROOT/$part_dir" >&2
    return 1
  fi
  (cd "$ROOT/$part_dir" && sha256sum -c "$HERE/$part_sums")
  cat "$ROOT/$part_dir"/part-* > "$ROOT/$archive"
}

verify_or_assemble toolchains.zip toolchains.zip.parts TOOLCHAINS-PARTS.SHA256SUMS
verify_or_assemble graphics.zip graphics.zip.parts GRAPHICS-PARTS.SHA256SUMS

(cd "$ROOT" && sha256sum -c "$HERE/SHA256SUMS")

tar -tzf "$ROOT/linux-ububtu-vm-workspace-backup.tar.gz" >/dev/null
for archive in operating-system.zip toolchains.zip packages.zip audio.zip graphics.zip; do
  unzip -tq "$ROOT/$archive" >/dev/null
done

echo 'REAPER 7.79 Golden Master verification PASSED.'
