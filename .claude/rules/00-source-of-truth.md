# Source-of-truth rule

The project is governed by the canonical source-of-truth set in `docs/source-of-truth/`:

- `instrucciones.md` — goals, scope, Domain Logic Contract (`DR-*` rules), Journey Coverage Matrix and authority order.
- `*_IMPLEMENTATION_CHECKLIST.md` — phases, steps, Coverage Registry, DAG fields, risk, verify mode and `Domain rule refs` traceability.
- `*_TECHNICAL_GUIDE.md` — architecture, contracts, endpoints, DB, Domain Rules Implementation Matrix, ADRs and verification data contract.
- `STACK_PROFILE.yaml` — framework/language, module roots, commands, design-token enforcer and Git workflow.
- `UX_CONTRACT.md` — personas, screen inventory, required UI states and UX verification rules.

If any source-of-truth file is missing, duplicated, stale or contradictory, stop and repair the contract first.

Rules:

- These source files are the only authority. Everything under `orchestrator-state/memory/` and `orchestrator-state/tasks/` is a derived execution artifact.
- If official docs and these docs disagree: stop coding, write the discrepancy to `orchestrator-state/memory/official-doc-notes/`, reconcile, and only then continue.
- Full-read of source-of-truth is done on bootstrap and on explicit `planner` extraction. Daily work reads PROGRESS.md + task-pack instead.
- Domain logic is not a sixth source-of-truth file: it lives canonically as `Domain Logic Contract` inside `instrucciones.md`, is implemented through the `Domain Rules Implementation Matrix` in the TECHNICAL_GUIDE, and is linked per slice through `Domain rule refs` in the checklist.

## Secciones obligatorias

Dos secciones tienen home semántico fijo dentro de los documentos source-of-truth y no pueden vivir en otro sitio (ni en `orchestrator-state/memory/`, que es derivado/efímero):

### Domain Logic Contract → `instrucciones.md`

- Sección dedicada dentro de `instrucciones.md` con glosario, entidades, reglas `DR-*`, máquinas de estado y casos límite de dominio.
- Cada regla estable de negocio debe tener un ID canónico `DR-001`, `DR-002`, etc. No uses reglas anónimas si afectan validación, permisos, cálculos, lifecycle o errores de producto.
- El `TECHNICAL_GUIDE` debe mapear esas reglas en `Domain Rules Implementation Matrix`: endpoint/use case, constraint DB si aplica, error code, UX y test/fixture.
- El `CHECKLIST` debe referenciar las reglas por slice mediante `Domain rule refs`; bootstrap las copia a registry, work-items y task-packs.
- Si una slice toca dominio pero no declara reglas `DR-*`, bloquea o crea follow-up de source-of-truth antes de implementar.

### User journeys → `instrucciones.md`

- Sección dedicada dentro de `instrucciones.md` (sugerencia: subsección bajo Alcance / Scope, p. ej. `### 3.4 Recorridos del usuario`).
- Declara todos los recorridos reales necesarios para cubrir el producto; no hay tope artificial de journeys. Cada journey debe existir porque aporta cobertura funcional verificable. Un journey de un solo paso suele ser una feature, no un journey, salvo que el dominio lo justifique explícitamente.
- Cada journey usa **identificadores compartidos con el resto de docs**: nombres de ruta del router declarado del `TECHNICAL_GUIDE` y nombres de pantalla del `CHECKLIST`. Ejemplo: `user → /login → tap "Continue with Google" → callback OAuth → /home`.
- Owner: producto. Cambia cuando cambia el alcance, no cuando cambia la implementación.

### Architectural Decision Records (ADR) → `*_TECHNICAL_GUIDE.md`

- Sección al final del doc (sugerencia: `## Architectural Decision Records (ADR)`), append-only.
- Umbral para crear un ADR: elección **no obvia** donde alternativas se consideraron de verdad. Convenciones de estilo, defaults triviales o reglas ya cubiertas en `01-non-negotiables.md` no necesitan ADR.
- Formato canónico de cada entrada (8–15 líneas):
  - **Fecha** — `YYYY-MM-DD`.
  - **Contexto** — 1 frase: el problema o la fuerza que dispara la decisión.
  - **Decisión** — 1–2 frases: qué se elige.
  - **Alternativas descartadas** — 1 línea por alternativa con el motivo del rechazo. Sin esto el ADR no aporta valor.
  - **Consecuencias** — los tradeoffs que se aceptan.
- Cuando un ADR queda obsoleto **no se borra**: se marca `SUPERSEDED por ADR-N (YYYY-MM-DD)` y se añade el nuevo bloque al final. El log es lineal y append-only para preservar el porqué histórico.
