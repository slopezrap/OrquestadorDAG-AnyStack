#!/usr/bin/env bash
# macOS GUI-launched Claude Code may have a minimal PATH and miss Docker Desktop/Homebrew.
export PATH="/Applications/Docker.app/Contents/Resources/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
# scripts/dev-restart.sh
#
# Stack-agnostic dev environment manager. The contract (consumed by
# /next-slice and /verify-slice) is fixed regardless of stack:
#
#   --task <TASK_ID>  optional slice id. Exports CLAUDE_ACTIVE_TASK_ID,
#            CLAUDE_COMPOSE_PROJECT_NAME=<task-id-lowercase> and per-slice
#            CLAUDE_*_PORT variables. Docker Compose profiles isolate by slice
#            with docker compose -p AND unique host ports.
#   --soft   (default) start only what is down; never restart what is healthy.
#            Auto-soft exit ≤1s when everything is up.
#   --check  report status only; never start/stop/migrate anything.
#            Exit 0 if everything is up, 1 otherwise.
#   --reset  hard reset: stop everything, drop DB to base + migrate + reseed,
#            restart back + front. Destructive — only when explicitly requested.
#
# How it works
# ------------
# This script is a generic dispatcher. The stack-specific commands (how to
# start the backend, how to start the frontend, how to probe health, how to
# reset the DB) live in `scripts/dev-restart.profile.sh`, which this script
# sources. The profile shipped in the orchestrator ZIP is neutral because no default app is bundled. A generated app must replace scripts/dev-restart.profile.sh with stack-specific commands derived from STACK_PROFILE.yaml; never edit this dispatcher for stack changes.
#
# Profile contract (each function returns 0 on success / non-zero on fail):
#   back_health        → quick health probe, exit 0 if up
#   back_start         → start backend (background), echo PID to BACK_PID_FILE
#   back_url           → human-readable URL for the status table
#   front_health       → quick health probe, exit 0 if up
#   front_start        → start frontend (background), echo PID to FRONT_PID_FILE
#   front_url          → human-readable URL for the status table
#   db_health          → 0 if DB reachable, 1 if down, 2 if unknown (back down)
#   db_reset           → migrate down + up + seed real/provided data (only called by --reset)
# Optional profile hooks used by verify-slice/log checks:
#   runtime_logs_collect <TASK_ID> <OUTPUT_DIR>  → save front/back/db/worker logs.
#   rancher_worker_logs <TASK_ID> <OUTPUT_DIR>   → save Rancher worker logs when the app has one.
# Docker Compose profiles should use docker compose -p "${CLAUDE_COMPOSE_PROJECT_NAME}"
# for every up/down/logs command. Isolation is by slice TASK_ID, not by worktree path.
# If the app publishes host ports, compose/dev commands must use allocated vars
# such as ${CLAUDE_FRONTEND_PORT}, ${CLAUDE_BACKEND_PORT}, ${CLAUDE_DB_PORT}.
# The allocator checks occupied/reserved ports before assigning a slice.
#
# The profile may read .env (auto-sourced before the profile is loaded) and
# may use any helpers it wants; it MUST set BACK_PID_FILE / FRONT_PID_FILE
# (or accept the defaults below).
#
# Logs default to:
#   orchestrator-state/dev-logs/back.log    backend stdout+stderr
#   orchestrator-state/dev-logs/front.log   frontend stdout+stderr
#   orchestrator-state/dev-logs/back.pid    backend PID
#   orchestrator-state/dev-logs/front.pid   frontend PID

set -euo pipefail

# --- Paths and helpers ------------------------------------------------------

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ORCHESTRATOR_ROOT="${CLAUDE_ORCHESTRATOR_ROOT:-$ROOT_DIR}"
LOG_DIR="${ROOT_DIR}/orchestrator-state/dev-logs"
mkdir -p "${LOG_DIR}"

BACK_LOG="${LOG_DIR}/back.log"
FRONT_LOG="${LOG_DIR}/front.log"
BACK_PID_FILE="${LOG_DIR}/back.pid"
FRONT_PID_FILE="${LOG_DIR}/front.pid"

export ROOT_DIR ORCHESTRATOR_ROOT LOG_DIR BACK_LOG FRONT_LOG BACK_PID_FILE FRONT_PID_FILE

log()   { printf '==> %s\n' "$1"; }
warn()  { printf 'WARN: %s\n' "$1" >&2; }
fail()  { printf 'ERROR: %s\n' "$1" >&2; exit 1; }
info()  { printf '     %s\n' "$1"; }
export -f log warn fail info

# --- Args -------------------------------------------------------------------

MODE="--soft"
TASK_ID="${CLAUDE_ACTIVE_TASK_ID:-}"
while [ "$#" -gt 0 ]; do
  case "${1:-}" in
    --soft|--check|--reset) MODE="$1"; shift ;;
    --task) [ "${2:-}" ] || fail "--task requires a TASK_ID"; TASK_ID="$2"; shift 2 ;;
    -h|--help) sed -n '1,75p' "$0"; exit 0 ;;
    "") shift ;;
    *) fail "Unknown flag: $1 (expected --soft | --check | --reset | --task <TASK_ID>)" ;;
  esac
done

resolve_runtime_context() {
  [ -n "${TASK_ID:-}" ] || return 0
  local runtime_root="$ORCHESTRATOR_ROOT"
  local runtime_script="${runtime_root}/.claude/bin/runtime_context.py"
  if [ ! -f "$runtime_script" ]; then
    runtime_root="$ROOT_DIR"
    runtime_script="${ROOT_DIR}/.claude/bin/runtime_context.py"
  fi
  eval "$(python3 -B -S "$runtime_script" --root "$runtime_root" --workspace-root "$ROOT_DIR" --task "$TASK_ID" --print-env)"
}
[ -n "$TASK_ID" ] && export CLAUDE_ACTIVE_TASK_ID="$TASK_ID"
if [ -n "$TASK_ID" ]; then
  resolve_runtime_context
else
  COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-${CLAUDE_COMPOSE_PROJECT_NAME:-$(basename "$ROOT_DIR" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_-]+/-/g; s/^-+//; s/-+$//')}}"
  CLAUDE_COMPOSE_PROJECT_NAME="$COMPOSE_PROJECT_NAME"
fi
export COMPOSE_PROJECT_NAME CLAUDE_COMPOSE_PROJECT_NAME

# --- Load .env --------------------------------------------------------------

if [ -f "${ROOT_DIR}/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  # shellcheck disable=SC1090
source "${ROOT_DIR}/.env"
  set +a
fi

# --- Allocate per-slice host ports ------------------------------------------

allocate_slice_ports() {
  [ -n "${TASK_ID:-}" ] || return 0
  local allocator_root="$ORCHESTRATOR_ROOT"
  local allocator_script="${allocator_root}/.claude/bin/allocate_slice_ports.py"
  if [ ! -f "$allocator_script" ]; then
    allocator_root="$ROOT_DIR"
    allocator_script="${ROOT_DIR}/.claude/bin/allocate_slice_ports.py"
  fi
  local env_file="${allocator_root}/orchestrator-state/dev-ports/${COMPOSE_PROJECT_NAME}.env"
  python3 -B -S "$allocator_script" --root "$allocator_root" --task "$TASK_ID" --env-file "$env_file" >/dev/null
  # shellcheck disable=SC1090
  # shellcheck disable=SC1090
source "$env_file"
  export CLAUDE_PORT_ENV_FILE="$env_file"
}
allocate_slice_ports

docker_compose() { docker compose -p "$COMPOSE_PROJECT_NAME" "$@"; }
export -f docker_compose

# --- Generic helpers (available to the profile) -----------------------------

pid_alive() {
  local pidfile="$1"
  [ -f "$pidfile" ] || return 1
  local pid
  pid="$(cat "$pidfile" 2>/dev/null || true)"
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}
export -f pid_alive

stop_pidfile() {
  local pidfile="$1" name="$2"
  if pid_alive "$pidfile"; then
    local pid
    pid="$(cat "$pidfile")"
    log "Stopping ${name} (pid ${pid})..."
    kill "$pid" 2>/dev/null || true
    sleep 1
    if kill -0 "$pid" 2>/dev/null; then
      warn "${name} did not exit; sending SIGKILL"
      kill -9 "$pid" 2>/dev/null || true
    fi
  fi
  rm -f "$pidfile"
}
export -f stop_pidfile

stop_orphan_on_port() {
  local port="$1" name="$2"
  local pid
  pid="$(lsof -ti :"$port" 2>/dev/null | head -1 || true)"
  if [ -n "$pid" ]; then
    warn "Orphan process on :${port} (pid ${pid}) — killing for ${name} reset"
    kill "$pid" 2>/dev/null || true
    sleep 1
    kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null || true
  fi
}
export -f stop_orphan_on_port

wait_for() {
  # wait_for <probe-fn-name> <timeout-seconds> <human-name>
  # Returns 0 as soon as the probe succeeds; 1 on timeout.
  local fn="$1" timeout="$2" name="$3"
  # `_` makes the loop counter explicitly unused (silences SC2034).
  for _ in $(seq 1 "$timeout"); do
    if "$fn" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  warn "${name} did not respond within ${timeout}s"
  return 1
}
export -f wait_for

# --- Load the stack profile -------------------------------------------------
#
# Resolution order:
#   1. ${ROOT_DIR}/scripts/dev-restart.profile.sh — the per-project profile.
#      A feature-app overrides the stack here. The template ships a neutral profile; generated apps replace it with real stack commands.
#   2. (no fallback) — if the profile is missing, abort with a clear error
#      so the project is forced to declare its stack explicitly.

PROFILE="${ROOT_DIR}/scripts/dev-restart.profile.sh"
if [ ! -f "${PROFILE}" ]; then
  fail "Missing ${PROFILE}. Each project must declare its stack profile.
       The template ships scripts/dev-restart.profile.sh — restore it from
       git or copy from your TECHNICAL_GUIDE example."
fi
# shellcheck disable=SC1090
source "${PROFILE}"

# Verify the profile defined the contract.
for required_fn in back_health back_start back_url front_health front_start front_url db_health db_reset; do
  if ! declare -F "${required_fn}" >/dev/null 2>&1; then
    fail "Profile ${PROFILE} did not define required function: ${required_fn}"
  fi
done

# --- Status reporter --------------------------------------------------------

print_status() {
  local back_state front_state db_state
  if back_health  >/dev/null 2>&1; then back_state="UP";   else back_state="DOWN"; fi
  if front_health >/dev/null 2>&1; then front_state="UP";  else front_state="DOWN"; fi
  case "$(db_health >/dev/null 2>&1; echo $?)" in
    0) db_state="UP" ;;
    2) db_state="UNKNOWN" ;;
    *) db_state="DOWN" ;;
  esac

  printf '\n'
  printf '  Service   URL                        Status\n'
  printf '  --------- -------------------------- -------\n'
  printf '  backend   %-26s %s\n' "$(back_url)"  "${back_state}"
  printf '  frontend  %-26s %s\n' "$(front_url)" "${front_state}"
  printf '  database  %-26s %s\n' "(via /ready)" "${db_state}"
  printf '\n'
  printf '  Logs: %s  %s\n' "${BACK_LOG}" "${FRONT_LOG}"
  printf '\n'
}

# --- Mode dispatch ----------------------------------------------------------

case "${MODE}" in
  --check)
    print_status
    if back_health >/dev/null 2>&1 && front_health >/dev/null 2>&1 && db_health >/dev/null 2>&1; then
      log "All services UP."
      exit 0
    fi
    log "One or more services DOWN."
    exit 1
    ;;

  --soft)
    BACK_OK=0; FRONT_OK=0
    back_health  >/dev/null 2>&1 && BACK_OK=1
    front_health >/dev/null 2>&1 && FRONT_OK=1
    if [ "${BACK_OK}" = 1 ] && [ "${FRONT_OK}" = 1 ]; then
      log "Soft: everything healthy. Nothing to do."
      print_status
      exit 0
    fi
    [ "${BACK_OK}"  = 0 ] && back_start
    [ "${FRONT_OK}" = 0 ] && front_start
    print_status
    ;;

  --reset)
    log "Hard reset requested."
    stop_pidfile      "${FRONT_PID_FILE}" "frontend"
    stop_pidfile      "${BACK_PID_FILE}"  "backend"
    db_reset
    back_start
    front_start
    print_status
    log "Reset complete."
    ;;
esac
