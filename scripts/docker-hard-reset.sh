#!/usr/bin/env bash
# macOS GUI-launched Claude Code may have a minimal PATH and miss Docker Desktop/Homebrew.
export PATH="/Applications/Docker.app/Contents/Resources/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
# Hard reset a per-slice Docker Compose project from the active task worktree.
set -euo pipefail
SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ORCHESTRATOR_ROOT="${CLAUDE_ORCHESTRATOR_ROOT:-$SCRIPT_ROOT}"
WORKSPACE_ROOT="${CLAUDE_WORKTREE_ROOT:-}"
if [ -z "$WORKSPACE_ROOT" ]; then
  WORKSPACE_ROOT="$(git -C "$SCRIPT_ROOT" rev-parse --show-toplevel 2>/dev/null || pwd -P)"
fi
TASK_ID="${CLAUDE_ACTIVE_TASK_ID:-}"
PROJECT="${COMPOSE_PROJECT_NAME:-${CLAUDE_COMPOSE_PROJECT_NAME:-}}"
COMPOSE_FILE_OVERRIDE=""
DETACH=1
REQUIRE_COMPOSE=0
usage(){ cat <<'USAGE'
Usage: scripts/docker-hard-reset.sh --task <TASK_ID> [--project <compose-project>] [--compose-file compose.yml] [--require-compose] [--foreground]

Uses docker compose -p <project> down -v --remove-orphans && up -d --build.
Project name and compose files are resolved from STACK_PROFILE.yaml, supporting
compose_project_template with {task_slug} or {{task_slug}} and compose_file paths.
Before `up`, allocates free host ports for the slice and exports CLAUDE_*_PORT.
USAGE
}
while [ $# -gt 0 ]; do
  case "$1" in
    --task|--task-id) TASK_ID="${2:?}"; shift 2 ;;
    --project) PROJECT="${2:?}"; shift 2 ;;
    --compose-file|-f) COMPOSE_FILE_OVERRIDE="${2:?}"; shift 2 ;;
    --require-compose) REQUIRE_COMPOSE=1; shift ;;
    --foreground) DETACH=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[ -n "$TASK_ID" ] || { echo "ERROR: provide --task <TASK_ID>" >&2; exit 2; }
RUNTIME_ARGS=(--root "$ORCHESTRATOR_ROOT" --workspace-root "$WORKSPACE_ROOT" --task "$TASK_ID" --print-env)
[ -n "$PROJECT" ] && RUNTIME_ARGS+=(--project "$PROJECT")
eval "$(python3 -B -S "$ORCHESTRATOR_ROOT/.claude/bin/runtime_context.py" "${RUNTIME_ARGS[@]}")"
PROJECT="$COMPOSE_PROJECT_NAME"
COMPOSE_FILES=()
if [ -n "$COMPOSE_FILE_OVERRIDE" ]; then
  COMPOSE_FILES=("$COMPOSE_FILE_OVERRIDE")
elif [ -n "${CLAUDE_RUNTIME_COMPOSE_FILES:-}" ]; then
  OLD_IFS="$IFS"; IFS=':'; for item in $CLAUDE_RUNTIME_COMPOSE_FILES; do [ -n "$item" ] && COMPOSE_FILES+=("$item"); done; IFS="$OLD_IFS"
fi
if [ "${#COMPOSE_FILES[@]}" -eq 0 ]; then
  echo "DOCKER_HARD_RESET: skipped_no_compose_file workspace=$WORKSPACE_ROOT task=${TASK_ID:-n/a} configured=${CLAUDE_RUNTIME_COMPOSE_FILES_CONFIGURED:-none}"
  [ "$REQUIRE_COMPOSE" = 1 ] && { echo "ERROR: compose file not found" >&2; exit 4; }
  exit 0
fi
command -v docker >/dev/null 2>&1 || { echo "ERROR: docker command not found" >&2; exit 4; }
ALLOCATOR_ROOT="$ORCHESTRATOR_ROOT"
ALLOCATOR_SCRIPT="$ALLOCATOR_ROOT/.claude/bin/allocate_slice_ports.py"
if [ ! -f "$ALLOCATOR_SCRIPT" ]; then
  ALLOCATOR_ROOT="$WORKSPACE_ROOT"
  ALLOCATOR_SCRIPT="$WORKSPACE_ROOT/.claude/bin/allocate_slice_ports.py"
fi
ENV_FILE="$ALLOCATOR_ROOT/orchestrator-state/dev-ports/$PROJECT.env"
python3 -B -S "$ALLOCATOR_SCRIPT" --root "$ALLOCATOR_ROOT" --task "$TASK_ID" --env-file "$ENV_FILE" >/dev/null
# shellcheck disable=SC1090
source "$ENV_FILE"
export CLAUDE_PORT_ENV_FILE="$ENV_FILE"
compose_args=(docker compose -p "$PROJECT")
for f in "${COMPOSE_FILES[@]}"; do compose_args+=(-f "$f"); done
printf 'DOCKER_HARD_RESET: project=%s compose=%s task=%s workspace=%s ports_env=%s\n' "$PROJECT" "${COMPOSE_FILES[*]}" "$TASK_ID" "$WORKSPACE_ROOT" "${CLAUDE_PORT_ENV_FILE:-none}"
(
  cd "$WORKSPACE_ROOT"
  "${compose_args[@]}" down -v --remove-orphans
  if [ "$DETACH" = 1 ]; then "${compose_args[@]}" up -d --build; else "${compose_args[@]}" up --build; fi
)
