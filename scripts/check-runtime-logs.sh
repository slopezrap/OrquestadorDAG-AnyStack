#!/usr/bin/env bash
# macOS GUI-launched Claude Code may have a minimal PATH and miss Docker Desktop/Homebrew.
export PATH="/Applications/Docker.app/Contents/Resources/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
# Capture runtime logs and scan them for production-blocking errors before /closer.
# Docker Compose stacks are isolated per TASK_ID via the resolved compose project name and per-slice host ports.
# Host ports are also allocated per slice before compose/log commands run.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ORCHESTRATOR_ROOT="${CLAUDE_ORCHESTRATOR_ROOT:-$ROOT_DIR}"
TASK_ID="${CLAUDE_ACTIVE_TASK_ID:-}"
EVIDENCE_DIR=""
STRICT=0
JSON=0
TAIL_LINES="1200"
MODE="check"
usage(){ cat <<'USAGE'
Usage: scripts/check-runtime-logs.sh --task <TASK_ID> [--mode check|hard-reset|all] [--evidence-dir <dir>] [--strict] [--json] [--tail <n>]

Modes:
  hard-reset  Run a per-slice Docker Compose reset when compose exists, or a configured hard-reset command.
  check       Capture logs and scan them for production-blocking errors.
  all         Hard reset first, then capture/scan logs.
USAGE
}
while [ "$#" -gt 0 ]; do
  case "$1" in
    --task|--task-id) TASK_ID="${2:?}"; shift 2 ;;
    --mode) MODE="${2:?}"; shift 2 ;;
    --evidence-dir) EVIDENCE_DIR="${2:?}"; shift 2 ;;
    --strict) STRICT=1; shift ;;
    --json) JSON=1; shift ;;
    --tail) TAIL_LINES="${2:?}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown flag $1" >&2; usage >&2; exit 2 ;;
  esac
done
[ -n "$TASK_ID" ] || { echo "ERROR: --task <TASK_ID> required" >&2; exit 2; }
case "$MODE" in check|hard-reset|all) ;; *) echo "ERROR: --mode must be check, hard-reset or all" >&2; exit 2 ;; esac
[[ "$TAIL_LINES" =~ ^[0-9]+$ ]] || { echo "ERROR: --tail must be numeric" >&2; exit 2; }
profile_get(){ local key="$1" default="${2:-}"; python3 -B -S "$ORCHESTRATOR_ROOT/.claude/bin/stack_profile.py" --root "$ORCHESTRATOR_ROOT" --get "$key" --default "$default" 2>/dev/null | sed -e 's/^"//' -e 's/"$//' || printf '%s' "$default"; }
is_none_value(){ local v; v="$(printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]' | xargs)"; [ -z "$v" ] || [ "$v" = "none" ] || [ "$v" = "null" ] || [ "$v" = "[]" ] || [ "$v" = "auto" ] || [ "$v" = "false" ]; }
render_runtime_template(){ local text="$1"; text="${text//\{\{ task_slug \}\}/$TASK_SLUG}"; text="${text//\{\{task_slug\}\}/$TASK_SLUG}"; text="${text//\{task_slug\}/$TASK_SLUG}"; text="${text//\$\{TASK_SLUG\}/$TASK_SLUG}"; text="${text//\$TASK_SLUG/$TASK_SLUG}"; text="${text//\{\{ task_id \}\}/$TASK_ID}"; text="${text//\{\{task_id\}\}/$TASK_ID}"; text="${text//\{task_id\}/$TASK_ID}"; text="${text//\$\{TASK_ID\}/$TASK_ID}"; text="${text//\$TASK_ID/$TASK_ID}"; printf '%s' "$text"; }
run_cmd_to_file(){ local label="$1" cmd="$2" outfile="$3"; cmd="$(render_runtime_template "$cmd")"; { printf 'COMMAND: %s\n' "$cmd"; printf 'TASK_ID: %s\n' "$TASK_ID"; printf 'COMPOSE_PROJECT_NAME: %s\n' "$COMPOSE_PROJECT_NAME"; printf -- '--- output ---\n'; } > "$outfile"; if bash -lc "$cmd" >> "$outfile" 2>&1; then printf 'COMMAND_EXIT: 0\n' >> "$outfile"; else local rc=$?; printf 'COMMAND_EXIT: %s\n' "$rc" >> "$outfile"; printf 'WARN: %s command exited %s; scanner/strict mode will decide.\n' "$label" "$rc" >&2; fi; }
eval "$(python3 -B -S "$ORCHESTRATOR_ROOT/.claude/bin/runtime_context.py" --root "$ORCHESTRATOR_ROOT" --workspace-root "$ROOT_DIR" --task "$TASK_ID" --print-env)"
export CLAUDE_ACTIVE_TASK_ID="$TASK_ID" TASK_ID TASK_SLUG TAIL_LINES
[ -n "$EVIDENCE_DIR" ] || EVIDENCE_DIR="$ROOT_DIR/orchestrator-state/tasks/evidence/$TASK_ID/runtime-logs"
mkdir -p "$EVIDENCE_DIR"; export EVIDENCE_DIR
if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ROOT_DIR/.env"
  set +a
fi
ALLOCATOR_ROOT="$ORCHESTRATOR_ROOT"
ALLOCATOR_SCRIPT="$ALLOCATOR_ROOT/.claude/bin/allocate_slice_ports.py"
if [ ! -f "$ALLOCATOR_SCRIPT" ]; then
  ALLOCATOR_ROOT="$ROOT_DIR"
  ALLOCATOR_SCRIPT="$ROOT_DIR/.claude/bin/allocate_slice_ports.py"
fi
PORT_ENV_FILE="$ALLOCATOR_ROOT/orchestrator-state/dev-ports/$COMPOSE_PROJECT_NAME.env"
python3 -B -S "$ALLOCATOR_SCRIPT" --root "$ALLOCATOR_ROOT" --task "$TASK_ID" --env-file "$PORT_ENV_FILE" >/dev/null
# shellcheck disable=SC1090
source "$PORT_ENV_FILE"
export CLAUDE_PORT_ENV_FILE="$PORT_ENV_FILE"
PROFILE="$ROOT_DIR/scripts/dev-restart.profile.sh"
if [ -f "$PROFILE" ]; then
  # shellcheck disable=SC1090
  source "$PROFILE"
fi
if [ "$MODE" = hard-reset ] || [ "$MODE" = all ]; then
  HARD_RESET_CMD="$(profile_get verification.docker.hard_reset_cmd auto)"
  if ! is_none_value "$HARD_RESET_CMD"; then run_cmd_to_file "verification.docker.hard_reset_cmd" "$HARD_RESET_CMD" "$EVIDENCE_DIR/hard-reset.log"; elif [ "${CLAUDE_COMPOSE_FILE_EXISTS:-no}" = "yes" ]; then bash "$ROOT_DIR/scripts/docker-hard-reset.sh" --task "$TASK_ID" --project "$CLAUDE_COMPOSE_PROJECT_NAME"; else echo "DOCKER_HARD_RESET: skipped_no_compose_file configured=${CLAUDE_RUNTIME_COMPOSE_FILES_CONFIGURED:-none}"; [ "$STRICT" = 1 ] && [ "${CLAUDE_RUNTIME_COMPOSE_FILES_EXPLICIT:-no}" = "yes" ] && { echo "ERROR: strict hard-reset requires configured compose file or command" >&2; exit 4; }; fi
  [ "$MODE" = hard-reset ] && exit 0
fi
if [ "${CLAUDE_COMPOSE_FILE_EXISTS:-no}" = "yes" ] && command -v docker >/dev/null 2>&1; then
  compose_args=(docker compose -p "$COMPOSE_PROJECT_NAME")
  OLD_IFS="$IFS"; IFS=':'; for item in $CLAUDE_RUNTIME_COMPOSE_FILES; do [ -n "$item" ] && compose_args+=(-f "$item"); done; IFS="$OLD_IFS"
  (cd "$ROOT_DIR" && "${compose_args[@]}" logs --no-color --tail "$TAIL_LINES") > "$EVIDENCE_DIR/docker-compose.log" 2>&1 || true
fi
if declare -F runtime_logs_collect >/dev/null 2>&1; then runtime_logs_collect "$TASK_ID" "$EVIDENCE_DIR"; elif compgen -G "$ROOT_DIR/orchestrator-state/dev-logs/*.log" >/dev/null; then cp "$ROOT_DIR"/orchestrator-state/dev-logs/*.log "$EVIDENCE_DIR"/ 2>/dev/null || true; fi
if declare -F rancher_worker_logs >/dev/null 2>&1; then rancher_worker_logs "$TASK_ID" "$EVIDENCE_DIR"; fi
YAML_LOG_CMD="$(profile_get observability.log_check_cmd none)"; is_none_value "$YAML_LOG_CMD" && YAML_LOG_CMD="$(profile_get verification.docker.logs_cmd none)"; ! is_none_value "$YAML_LOG_CMD" && run_cmd_to_file "observability.log_check_cmd" "$YAML_LOG_CMD" "$EVIDENCE_DIR/stack-profile-runtime.log"
YAML_RANCHER_CMD="$(profile_get observability.rancher_worker_logs_cmd none)"; is_none_value "$YAML_RANCHER_CMD" && YAML_RANCHER_CMD="$(profile_get verification.rancher.worker_logs_cmd none)"; ! is_none_value "$YAML_RANCHER_CMD" && run_cmd_to_file "observability.rancher_worker_logs_cmd" "$YAML_RANCHER_CMD" "$EVIDENCE_DIR/rancher-worker.log"
args=("$ROOT_DIR/.claude/bin/check_runtime_logs.py" --task "$TASK_ID" --log-dir "$EVIDENCE_DIR" --tail "$TAIL_LINES")
[ "$STRICT" = 1 ] && args+=(--strict)
[ "$JSON" = 1 ] && args+=(--json)
outfile="$EVIDENCE_DIR/runtime-log-check.json"; [ "$JSON" = 1 ] || outfile="$EVIDENCE_DIR/runtime-log-check.txt"
set +e
python3 -B -S "${args[@]}" > "$outfile"
rc=$?
set -e
cat "$outfile"
exit "$rc"
