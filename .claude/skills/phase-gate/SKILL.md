---
name: phase-gate
description: "Verifica mecánicamente que una phase está cerrada antes de avanzar: tasks done, journeys verificados, reports/evidence y git opcional."
argument-hint: "[PHASE_ID] [--require-git-clean]"
user-invocable: true
disable-model-invocation: false
---

# /phase-gate

Argumentos recibidos: `$ARGUMENTS`.

Este skill es el punto de entrada moderno equivalente a `.claude/commands/phase-gate.md`.

1. Lee `.claude/commands/phase-gate.md` antes de actuar.
2. Trata ese fichero de comando como procedimiento autoritativo y fuente única de la coreografía.
3. Aplica `$ARGUMENTS` exactamente como lo haría el comando original.
4. No dupliques, reduzcas ni reinterpretes gates, hooks, trailers, worktrees, Git workflow, verify mode ni reglas de cierre.
5. Si este skill y el comando original parecen contradecirse, sigue `.claude/commands/phase-gate.md` y reporta el drift como bloqueo mecánico.

No invoques este skill desde el modelo de forma autónoma. Sólo ejecútalo cuando el usuario lo llame explícitamente como `/phase-gate`.
