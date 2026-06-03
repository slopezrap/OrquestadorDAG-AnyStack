# Dev loop and verification

Project: backend server, client runtime (dev server, emulator, simulator, or equivalent per TECHNICAL_GUIDE), and database MUST be up before any implementation work.

## Pre-conditions

- Backend server running; `curl localhost:{port}/health` → 200.
- Client runtime running (dev server, emulator, simulator, or equivalent per TECHNICAL_GUIDE); verify availability using the method defined in TECHNICAL_GUIDE.
- Database: migrations applied, seed loaded.
- Ports, commands and health endpoints come from the TECHNICAL_GUIDE — never hardcoded.

If any server is down, restart before continuing work.

## Per-slice verification

After completing a slice the developer runs:

- Backend lint → zero issues.
- Backend tests → all green.
- Client/frontend lint → zero issues.
- Client/frontend tests → all green.
- Visual check using the method defined in TECHNICAL_GUIDE (browser, emulator, simulator, device, etc.).

A slice is not ✅ until:

- Backend endpoint verified (curl or API test).
- Client UI verified visually using the method defined in TECHNICAL_GUIDE (browser, emulator, device, etc.).
- All tests green on both sides.
- Logs correct under both `ENABLE_VERBOSE_LOGGING` values.
- PROGRESS.md updated.
- Handoff written.

If a slice cannot be verified in localhost, split it.

## Visual check (mandatory)

1. Launch the app using the method defined in TECHNICAL_GUIDE (browser URL, emulator, simulator, physical device, etc.).
2. Navigate to the new page/feature.
3. Verify professional design: design tokens, spacing, typography, alignment.
4. Verify the motor: click → data flows → backend responds → UI updates.
5. Document what you saw in PROGRESS.md.

If design is off → fix before moving on. If the motor is off → fix before moving on.

The full human visual verification is performed automatically inside `/next-slice` once validator/tester are green, using the `/verify-slice` contract: hard reset, real/provided data, web/browser MCP reproduction for web or Dart/Flutter MCP simulator/emulator/device reproduction for Flutter mobile, live watch of runtime logs and validation table. `/verify-slice` remains the recovery command and is resilient to `/clear` — it rebuilds context from disk (PROGRESS.md, runtime-state.json, registry.json, handoff, TECHNICAL_GUIDE) if the auto-verify was interrupted or the user wants to re-run it before manual `/closer`.

## Production-real verification contract

- Verifica siempre con datos reales/proporcionados del `Verification Data Contract`; no cierres con stubs, lorem ipsum, payloads inventados ni texto pegado manualmente en lugar del flujo real del producto.
- El verify humano debe reproducir la slice como un usuario real: navegar, tocar botones/controles afectados, comprobar estados enabled/disabled/loading/empty/error/permission/success, confirmar persistencia front -> back -> DB/worker y validar `Domain rule refs` con datos reales.
- Si hay Docker Compose, usa aislamiento por slice con `docker compose -p <compose_project>` y puertos host por slice (`CLAUDE_FRONTEND_PORT`, `CLAUDE_BACKEND_PORT`, etc.); el helper canónico es `./scripts/check-runtime-logs.sh --task <TASK_ID> --mode hard-reset`, que asigna puertos libres y reconstruye desde el worktree activo.
- Antes de `/closer`, ejecuta `./scripts/check-runtime-logs.sh --task <TASK_ID> --mode check --strict --json` y adjunta `runtime-log-check.json` al evidence. Logs browser/front/back/DB/worker/Docker/Rancher deben quedar limpios.
- Si el producto usa Rancher/Kubernetes/worker/colas, declara los comandos de logs en `STACK_PROFILE.yaml` y exige logs del worker Rancher limpios; si no aplica, escribe `not_applicable:<razón>` en el handoff, no lo dejes vacío.
- Si la slice procesa PDFs/documentos/entradas LLM, sube o referencia el artefacto real, registra ruta/hash en `LLM_INPUT_ARTIFACTS`/`DATA_SOURCE_FILES`, ejecuta el pipeline real y verifica `LLM_DOCUMENT_EXTRACTION`; nunca inventes la extracción.
