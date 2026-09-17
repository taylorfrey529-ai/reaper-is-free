#!/usr/bin/env bash
set -euo pipefail
mode=json
display=${DISPLAY:-:88}
while (($#)); do
  case "$1" in
    --shell) mode=shell ;;
    --json) mode=json ;;
    *) display=$1 ;;
  esac
  shift
done
try_display() {
  local auth=${1:-}
  if [[ -n "$auth" ]]; then
    DISPLAY="$display" XAUTHORITY="$auth" xdpyinfo -display "$display" >/dev/null 2>&1
  else
    DISPLAY="$display" xdpyinfo -display "$display" >/dev/null 2>&1
  fi
}
auth=${XAUTHORITY:-}
source_kind=environment
if ! try_display "$auth"; then
  source_kind=server-process
  auth=''
  target=${display##*:}
  target=${target%%.*}
  for proc in /proc/[0-9]*; do
    [[ -r "$proc/cmdline" ]] || continue
    mapfile -d '' -t argv < "$proc/cmdline" || true
    ((${#argv[@]})) || continue
    base=${argv[0]##*/}
    case "$base" in Xvfb|Xorg|X|Xephyr) ;; *) continue ;; esac
    match=0
    candidate=''
    for ((i=1;i<${#argv[@]};i++)); do
      [[ "${argv[$i]}" == ":$target" ]] && match=1
      if [[ "${argv[$i]}" == '-auth' && $((i+1)) -lt ${#argv[@]} ]]; then
        candidate=${argv[$((i+1))]}
      fi
    done
    if ((match)) && [[ -n "$candidate" && -r "$candidate" ]] && try_display "$candidate"; then
      auth=$candidate
      break
    fi
  done
fi
if ! try_display "$auth"; then
  if [[ "$mode" == shell ]]; then
    printf 'return 3 2>/dev/null || exit 3\n'
  else
    printf '{"display":"%s","reachable":false}\n' "$display"
  fi
  exit 3
fi
size=$(if [[ -n "$auth" ]]; then DISPLAY="$display" XAUTHORITY="$auth" xdpyinfo -display "$display"; else DISPLAY="$display" xdpyinfo -display "$display"; fi | awk '/dimensions:/{print $2; exit}')
mode_bits=''
if [[ -n "$auth" && -e "$auth" ]]; then
  mode_bits=$(stat -c '%a' "$auth" 2>/dev/null || true)
fi
if [[ "$mode" == shell ]]; then
  printf 'export DISPLAY=%q\n' "$display"
  if [[ -n "$auth" ]]; then
    printf 'export XAUTHORITY=%q\n' "$auth"
  else
    printf 'unset XAUTHORITY\n'
  fi
else
  printf '{"display":"%s","reachable":true,"dimensions":"%s","xauthority":"%s","authority_mode":"%s","authority_source":"%s"}\n' "$display" "$size" "$auth" "$mode_bits" "$source_kind"
fi
