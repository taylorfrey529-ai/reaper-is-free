#!/usr/bin/env bash
set -euo pipefail
ROOT=${1:-/mnt/data}

check() {
  expected=$1
  primary=$2
  shift 2
  candidates=("$primary" "$@")
  found=""
  for name in "${candidates[@]}"; do
    if [ -f "$ROOT/$name" ]; then
      found="$ROOT/$name"
      break
    fi
  done
  if [ -z "$found" ]; then
    printf 'MISSING  %s\n' "$primary" >&2
    return 1
  fi
  actual=$(sha256sum "$found" | awk '{print $1}')
  if [ "$actual" != "$expected" ]; then
    printf 'MISMATCH %s\n  expected %s\n  actual   %s\n' "$found" "$expected" "$actual" >&2
    return 1
  fi
  printf 'OK       %s\n' "$found"
}

fail=0
check 568650bc01243a4eee7abaa6512ef4ae58e34e1a11c0178b7f76acbe57fec711 'toolchains.zip' || fail=1
check 093f590ba02b0284dc676d7f8ae499ead6fd93316524f7872cfa3c6fda0660bd 'audio(2).zip' 'audio.zip' || fail=1
check 060c674c9855aee0cb1c14a0e895c8cecfe2fb001a8fee12904956c5951fbb30 'operating-system.zip' || fail=1
check 3a70c1dbdccdf68b766df2c68bcd82e597de7ffafdb8fd2d7f0ec86ffdcad1a2 'packages(2).zip' 'packages.zip' || fail=1
check 746fba7dbf8ef9a72c2596c51f57c81b5112f5537a6001989e2abcf9b907a72d 'graphics.zip' || fail=1

if [ "$fail" -ne 0 ]; then
  echo 'Runtime bundle verification FAILED.' >&2
  exit 1
fi

echo 'Runtime bundle verification PASSED.'
