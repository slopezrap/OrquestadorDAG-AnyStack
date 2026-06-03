# Docs layout

- `templates/`: tres perfiles (`minimal`, `large-without-base`, `large-with-base`), cada uno con cinco templates.
- `prompts/`: prompt maestro para generar los cinco source-of-truth acumulativos en modo DAG explícito.
- `guides/`: guía de generación con ChatGPT y cheat sheet operativa.
- `product-baseline/`: baseline construido opcional (`docs/product-baseline/`) + `BASELINE_MANIFEST.json`. Solo se usa cuando eliges `large-with-base`.
- `source-of-truth/`: los cinco documentos vivos de la app actual. En un checkout nuevo puede estar vacío hasta que generes la app desde templates. Cuando existe, es acumulativo: baseline real + v1 + v2 + ... + vN.
- `reports/`: auditorías, validaciones y reportes de fixes.

Contrato activo esperado en `docs/source-of-truth/`:

```text
instrucciones.md
<APP>_TECHNICAL_GUIDE.md
<APP>_IMPLEMENTATION_CHECKLIST.md
STACK_PROFILE.yaml
UX_CONTRACT.md
```

El checklist debe tener `Canonical Coverage Registry` con estas columnas mínimas. Las columnas `* refs` conectan cada slice con la lógica funcional y técnica declarada en los cinco source-of-truth:

```text
Slice ID | Tipo | Target | Step | Product increment | Build state | Risk level | Verify mode | Depends on | Conflict group | Write set | Journey refs | Pantalla/Ruta | Endpoint | Tablas DB | Origen-Instr | Origen-TechGuide | Acceptance mínimo | Verify mínimo | Domain rule refs | Architecture refs | Application logic refs | Core logic refs | Permission refs | State refs | Failure refs | Integration refs | UI refs | Data refs | Observability refs | Evaluation refs
```

`Product increment` y `Build state` permiten construir productos grandes por versiones: filas ya construidas quedan `done`; filas nuevas de v1/v2/vN quedan `planned`. El DAG runtime canónico vive en `orchestrator-state/tasks/registry.json` (`tasks[]` + `task_dag.source_digest`); `task-dag.json/md` y `execution-graph.json` son vistas derivadas verificadas por `check-task-dag --strict`.

## Perfiles de templates

```text
docs/templates/minimal/             app pequeña sin existing baseline, AnyStack, alcance acotado sin topes artificiales
docs/templates/large-without-base/  producto grande desde cero, AnyStack
docs/templates/large-with-base/     evolución de un baseline existente, stack real declarado en STACK_PROFILE.yaml
```

Cada perfil contiene exactamente:

```text
instrucciones.template.md
PROJECT_TECHNICAL_GUIDE.template.md
PROJECT_IMPLEMENTATION_CHECKLIST.template.md
UX_CONTRACT.template.md
STACK_PROFILE.template.yaml
```

`large-with-base` hereda `docs/product-baseline/` y mantiene compatibilidad con el stack real declarado en su STACK_PROFILE.yaml. No lo conviertas a otro stack por costumbre. Para apps nuevas grandes usa `large-without-base`.

## Comandos de validación

```bash
python3 -B -S .claude/bin/bootstrap_source_of_truth.py --validate-only
python3 -B -S .claude/bin/bootstrap_source_of_truth.py --refresh
./scripts/check-task-dag.sh --strict
./scripts/check-journey-matrix.sh --strict
./scripts/check-wiring-contract.sh --strict --require-new-template-columns
./scripts/generate-api-contracts.sh --validate-only
```

## Dónde escribe el bootstrap

```text
orchestrator-state/memory/PROGRESS.md
orchestrator-state/memory/task-dag.json|md
orchestrator-state/memory/execution-graph.json
orchestrator-state/memory/stack-profile.json
orchestrator-state/tasks/registry.json
orchestrator-state/tasks/runtime-state.json
orchestrator-state/tasks/phases/*.yaml
orchestrator-state/tasks/work-items/*.yaml
orchestrator-state/tasks/task-packs/*.md
orchestrator-state/tasks/api-contracts/*
orchestrator-state/memory/domain-logic-contract.md
orchestrator-state/memory/domain-rule-index.json
```

No edites `registry.json`, `runtime-state.json`, `task-dag.json` ni `task-dag.md` a mano. Son derivados por bootstrap y scripts con locks.

## Journeys y frontier gate

En DAG-only, los journeys pendientes solo difieren tasks que referencian esos journey IDs. No hay otro modo de journey gate.

## Follow-ups formales

Si durante ejecución aparece trabajo real nuevo, usa `./scripts/register-followup-task.sh propose|promote|waive|list`. Las promociones escriben una sección `Runtime Follow-up Coverage Registry` en el checklist para que futuros bootstrap no pierdan la task.

## Framework validators and examples

These files are framework internals, not extra product source-of-truth documents:

Estos ficheros no son source-of-truth de producto y no fija el stack ninguna implementación de ejemplo.

```text
.claude/schemas/                  JSON schemas for generated runtime artifacts
scripts/validate-orchestrator-schemas.sh
scripts/orchestrator-doctor.sh
examples/golden-real-app/          dependency-free reference implementation of the AnyStack golden contract
scripts/run-golden-e2e.sh
```

ChatGPT still fills only the five files in `docs/source-of-truth/`. The golden app exists to test the framework itself: its Python/SQLite implementation is intentionally small, but the contract it proves is stack-agnostic and portable to Flutter, React, Node, Python, Java, Go or any stack declared in `STACK_PROFILE.yaml`.
