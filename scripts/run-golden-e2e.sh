#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JSON=0
KEEP=0
usage(){ cat <<'USAGE'
Usage: scripts/run-golden-e2e.sh [--json] [--keep]

Runs:
  1. a real HTTP + SQLite + log verification for examples/golden-real-app;
  2. a source-of-truth -> bootstrap -> DAG/wiring/next-wave smoke using that golden pack.
  The golden app is not a preferred stack template; real products remain AnyStack.
USAGE
}
while [ "$#" -gt 0 ]; do
  case "$1" in
    --json) JSON=1; shift ;;
    --keep) KEEP=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown flag $1" >&2; usage >&2; exit 2 ;;
  esac
done
GOLDEN_DIR="$ROOT/examples/golden-real-app"
APP_JSON="$(python3 -B -S "$GOLDEN_DIR/verify_golden_app.py" --json)"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/orq-golden-e2e.XXXXXX")"
cleanup(){ [ "$KEEP" = 1 ] || rm -rf "$TMP_ROOT"; }
trap cleanup EXIT
WORK="$TMP_ROOT/repo"
mkdir -p "$WORK"
for name in .claude scripts docs orchestrator-state examples README.md CHEATSHEET.md .gitignore; do
  [ -e "$ROOT/$name" ] && cp -a "$ROOT/$name" "$WORK/"
done
rm -rf "$WORK/docs/source-of-truth"
mkdir -p "$WORK/docs/source-of-truth"
cp -a "$WORK/examples/golden-real-app/source-of-truth/." "$WORK/docs/source-of-truth/"
export CLAUDE_ORCHESTRATOR_ROOT="$WORK"
export CLAUDE_PROJECT_DIR="$WORK"
export CLAUDE_SKIP_MAIN_SYNC_BEFORE_WAVE=1
export CLAUDE_DISABLE_ZOMBIE_WORKTREE_CLEANUP=1
export CLAUDE_CLEAN_MERGED_PR_BRANCHES=0
export PYTHONDONTWRITEBYTECODE=1
(
  cd "$WORK"
  python3 -B -S .claude/bin/bootstrap_source_of_truth.py --validate-only >/tmp/orq_golden_validate.$$ 2>&1
  python3 -B -S .claude/bin/bootstrap_source_of_truth.py --refresh >/tmp/orq_golden_refresh.$$ 2>&1
  ./scripts/check-task-dag.sh --strict >/tmp/orq_golden_dag.$$ 2>&1
  ./scripts/check-journey-matrix.sh --strict >/tmp/orq_golden_journey.$$ 2>&1
  ./scripts/check-wiring-contract.sh --strict --require-new-template-columns >/tmp/orq_golden_wiring.$$ 2>&1
  ./scripts/next-wave.sh --limit 2 --json >/tmp/orq_golden_wave.$$ 2>&1
)
TASKS="$(python3 -B -S - <<PY
import json
from pathlib import Path
registry=json.loads((Path('$WORK')/'orchestrator-state/tasks/registry.json').read_text())
print(len(registry.get('tasks', [])))
PY
)"
WAVE_JSON="$(cat /tmp/orq_golden_wave.$$)"
if [ "$JSON" = 1 ]; then
  python3 -B -S - <<PY
import json
payload={
  "ok": True,
  "app_e2e": json.loads(r'''$APP_JSON'''),
  "orchestrator_bootstrap": {"tasks": int('$TASKS'), "next_wave": json.loads(r'''$WAVE_JSON''')},
  "temp_root": "$TMP_ROOT" if $KEEP else "(removed)",
}
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY
else
  echo "GOLDEN_E2E: OK"
  echo "tasks: $TASKS"
fi
