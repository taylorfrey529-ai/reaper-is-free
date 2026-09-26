#!/usr/bin/env bash
set -euo pipefail
WS=${WS:-/mnt/data/ubuntu-desktop-workspace}
FEATURE="$WS/workspace-feature-set-v0.2.0"
fail=0; pass=0
check(){ label=$1; shift; if "$@"; then printf '[PASS] %s\n' "$label"; pass=$((pass+1)); else printf '[FAIL] %s\n' "$label"; fail=$((fail+1)); fi; }
hash_is(){ [ "$(sha256sum "$1" | awk '{print $1}')" = "$2" ]; }
check 'Metal GTX sentinel' test -f "$WS/instruments/Metal-GTX/Programs/03-METAL-GTX XTracking.sfz"
check 'Dark Black sentinel' test -f "$WS/instruments/Black-And-Blue-Basses-Upstream/Programs/01-darkblack_keysw.sfz"
check 'Baby Blue sentinel' test -f "$WS/instruments/Black-And-Blue-Basses-Upstream/Programs/03-babyblue_all.sfz"
check 'ARIA keys sentinel' test -f "$WS/instruments/ARIA-Engine-Free-Sounds-Vol1/Programs-Portable/Garritan/Jazz Piano Lite.sfz"
check 'AVLDrums LV2 retained' test -f "$WS/home/.lv2/avldrums.lv2/avldrums.so"
check 'NAM LV2 retained' test -f "$WS/home/.lv2/neural_amp_modeler.lv2/neural_amp_modeler.so"
check 'Black & Blue sample floor' bash -c '[ "$(find "$1" -type f \( -iname "*.wav" -o -iname "*.flac" \) | wc -l)" -ge 2208 ]' _ "$WS/instruments/Black-And-Blue-Basses-Upstream"
check 'Metal GTX sample floor' bash -c '[ "$(find "$1" -type f \( -iname "*.wav" -o -iname "*.flac" \) | wc -l)" -ge 2739 ]' _ "$WS/instruments/Metal-GTX"
check 'sforzando cache entry' grep -qi 'sforzando' "$WS/config/REAPER/reaper-vstplugins64.ini"
check 'Sunwell action registration count' bash -c '[ "$(grep -c "Sunwell_.*\\.lua" "$1")" -eq 38 ]' _ "$WS/config/REAPER/reaper-kb.ini"
check 'sforzando binary identity' hash_is "$WS/home/.vst3/sforzando.vst3/Contents/x86_64-linux/sforzando.so" 6327bb446f4a0dba8730b29d6598bc039b17db55e895eee7c95f1fa8e439d5d0
check 'AVL binary identity' hash_is "$WS/home/.lv2/avldrums.lv2/avldrums.so" f995c3a4a359e523b78a8417e7e4a9085718659ee72050bc0d5606b21b100c8d
check 'NAM binary identity' hash_is "$WS/home/.lv2/neural_amp_modeler.lv2/neural_amp_modeler.so" 9096a4480621733a6a18c5f1af5edcd7f4d1188a5d7b1327d2b6406dddb1e692
check 'Dark Black identity' hash_is "$WS/instruments/Black-And-Blue-Basses-Upstream/Programs/01-darkblack_keysw.sfz" 98ce9c4a206a4807c934286e663dafaf6d7d89f4b7a98a22cc5d251c1b808699
check 'Metal GTX stock identity' hash_is "$WS/instruments/Metal-GTX/Programs/03-METAL-GTX XTracking.sfz" 4072694674f583befec92f64a52b1cbaf08a00c73913220f95cd2d30429596c7
check 'Metal GTX Clean DI identity' hash_is "$WS/instruments/Metal-GTX/Programs/03-METAL-GTX XTracking Clean DI.sfz" a5cb148de4600a16a8b5ebca7ddfae325a29f49874985f3a7d044e6a49a10d27
check 'Obsidian identity' hash_is "$WS/nam-models/Obsidian.nam" 8d5d62626945e079a34a09e91d6ddef575beaea3bc17efdb4dee4afed9be81c7
if [ -x "$FEATURE/bin/verify-feature-set.sh" ]; then
  if "$FEATURE/bin/verify-feature-set.sh" /tmp/v110-coverage-feature-verify.$$ >/dev/null; then
    printf '[PASS] feature-set verifier 37/0\n'; pass=$((pass+1))
  else
    printf '[FAIL] feature-set verifier\n'; fail=$((fail+1))
  fi
  rm -f /tmp/v110-coverage-feature-verify.$$
fi
printf 'SUMMARY pass=%d fail=%d\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
