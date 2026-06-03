# Golden Real App — Implementation Checklist

## Canonical Coverage Registry

| Slice ID | Tipo | Target | Step | Product increment | Build state | Risk level | Verify mode | Depends on | Conflict group | Write set | Journey refs | Pantalla/Ruta | Endpoint | Tablas DB | Origen-Instr | Origen-TechGuide | Acceptance mínimo | Verify mínimo | Domain rule refs | Architecture refs | Application logic refs | Core logic refs | Permission refs | State refs | Failure refs | Integration refs | UI refs | Data refs | Observability refs | Evaluation refs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P01-S01-T001 | app | Crear item real | Step 1.1 | formulario + POST + GET + SQLite persistidos | ready | medium | real-human | — | golden-app | examples/golden-real-app/app.py; examples/golden-real-app/verify_golden_app.py; examples/golden-real-app/fixtures/** | J01 | / | POST /api/v1/items, GET /api/v1/items | items | F1,F3,J01,DR-001,AL-001,CORE-001 | POST/GET contracts, Domain Matrix, Application/Core Matrix | crea item con fixture real, lo lista y rechaza title vacío | ./scripts/run-golden-e2e.sh --json | DR-001 | A42-01,A42-03,A42-04,A42-05,A42-06,A42-10 | AL-001, AL-003 | CORE-001, CORE-003 | AUTH-001 | STATE-001 | ERR-001 | INT-001 | UI-001, UI-002 | DATA-001 | OBS-001, OBS-003 | EVAL-001, EVAL-003 |
| P01-S01-T002 | app | Aprobar item real | Step 1.1 | PATCH + transición approved persistida | ready | medium | real-human | P01-S01-T001 | golden-app | examples/golden-real-app/app.py; examples/golden-real-app/verify_golden_app.py | J02 | / | PATCH /api/v1/items/{id}, GET /api/v1/items/{id} | items | F2,J02,DR-002,AL-002,CORE-002 | PATCH contract, Domain Matrix, State Matrix | actualiza item existente y persiste status approved | ./scripts/run-golden-e2e.sh --json | DR-002 | A42-04,A42-05,A42-06,A42-08,A42-10 | AL-002 | CORE-002 | AUTH-001 | STATE-001 | ERR-002, ERR-003 | INT-001 | UI-003 | DATA-001 | OBS-002, OBS-003 | EVAL-002 |

## Phase 1 — Golden real app verification lane

### Step 1.1 — Human CRUD + domain rules

- [ ] P01-S01-T001
- [ ] P01-S01-T002

## Runtime Follow-up Coverage Registry

> Append-only. The orquestador adds rows here if real verification discovers new work outside the current task scope.
