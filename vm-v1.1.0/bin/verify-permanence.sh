#!/usr/bin/env bash
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "$HERE/verify-permanence-v1.1.0.sh" "$@"
