#!/usr/bin/env bash
# Common environment for running headless Blender renders.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BLENDER_DIR="$REPO_ROOT/blender-4.5.2-linux-x64"
BLENDER_BIN="$BLENDER_DIR/blender"
if [ ! -x "$BLENDER_BIN" ]; then
  echo "Blender binary not found at $BLENDER_BIN" >&2
  echo "Download and extract Blender 4.5.2 to $BLENDER_DIR (ignored by git)." >&2
  exit 127
fi
RUN() { echo "$*"; eval "$@"; }
