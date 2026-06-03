#!/usr/bin/env bash
# macOS GUI-launched Claude Code may have a minimal PATH and miss Docker Desktop/Homebrew.
export PATH="/Applications/Docker.app/Contents/Resources/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
# Allocate/source free host ports for a per-slice dev/Docker environment.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 -B -S "$ROOT_DIR/.claude/bin/allocate_slice_ports.py" --root "$ROOT_DIR" "$@"
