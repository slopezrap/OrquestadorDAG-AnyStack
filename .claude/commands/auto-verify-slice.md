---
description: Auto-verifies a low-risk DAG slice with deterministic commands, then leaves it ready for manual /closer.
argument-hint: "<TASK_ID>"
---

# /auto-verify-slice

Uso exclusivo para slices con `Risk level=low` y `Verify mode=auto`. No reemplaza `/verify-slice` para UI, journeys, auth, endpoints mutantes, datos personales, pagos ni cualquier slice `medium|high|critical`.

1. Ejecuta `./scripts/auto-verify-slice.sh <TASK_ID>`.
2. Si `VERIFY_OUTCOME=verified`, lee el handoff, confirma `verified_pending_close` y pide al usuario ejecutar `/closer <TASK_ID>`. Si el task pack declara `Domain rule refs`, exige evidencia determinista o `DOMAIN_RULES_VERIFIED` para esas reglas antes de dejar la slice lista para cierre. No spawnees `closer` desde este comando.
3. Si falla, spawnea `debugger`, vuelve a `validator ‖ tester` y repite el verify que corresponda.

El helper solo escribe en `orchestrator-state/tasks/handoffs/<TASK_ID>.md` y `orchestrator-state/tasks/evidence/<TASK_ID>/`.
