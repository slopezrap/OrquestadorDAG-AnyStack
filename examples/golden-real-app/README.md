# Golden Real App

This folder is a dependency-free reference implementation of the Orquestador AnyStack golden contract.

It is **not** a required stack, not a generated product, and not a sixth source-of-truth. Plainly: this is not a required stack. The current implementation uses Python stdlib + SQLite only so the framework can validate itself in CI without extra services.

Esta fixture no es una plantilla de stack para apps de producción; úsala solo como ejemplo de contrato verificable.

## What the fixture proves

`verify_golden_app.py` starts a real HTTP server, loads a provided JSON fixture, exercises visible controls, persists to SQLite, checks domain rules and scans runtime logs.

The required invariants are stack-agnostic:

| Invariant | Python fixture | Equivalent in another stack |
|---|---|---|
| Real/provided data | `fixtures/real_user_payload.json` | Seed file, sandbox account, uploaded PDF, real API fixture |
| Real product action | HTTP form + API calls | Playwright, Flutter integration test, mobile simulator, CLI workflow |
| Real persistence | SQLite row | Postgres/MySQL/Mongo/Firebase/S3/queue side effect |
| Domain rules | `DR-001`, `DR-002` | Same `Domain rule refs` from the five docs |
| Runtime logs | JSON log scanned by `check_runtime_logs.py` | Docker, Rancher/Kubernetes, worker, browser console, app logs |
| No stubs | No fake payloads or mocks | Same policy in every stack |

## How to port the golden contract

For React + Node, Flutter + Python, SwiftUI + Go, Java/Spring, Django, Laravel or any other stack, keep the same five-doc shape and replace only implementation commands in `STACK_PROFILE.yaml`:

```yaml
frontend:
  test_cmd: "<real UI/e2e command>"
backend:
  test_cmd: "<real backend/integration command>"
verification:
  real_data_policy: real_or_provided_only
  docker:
    compose_project_template: "{task_slug}"
    hard_reset_cmd: "<optional real hard reset>"
    logs_cmd: "<optional real logs command>"
  rancher:
    enabled: false
    worker_logs_required: false
    worker_logs_cmd: none
observability:
  log_check_cmd: "./scripts/check-runtime-logs.sh --task <TASK_ID> --mode check --strict --json"
```

The orquestador remains AnyStack because the runtime reads the five source-of-truth documents and `STACK_PROFILE.yaml`; it does not assume Python, Node, Flutter or React internally.
