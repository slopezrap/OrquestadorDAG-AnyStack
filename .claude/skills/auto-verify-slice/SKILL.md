---
name: auto-verify-slice
description: "Auto-verifies a low-risk DAG slice with deterministic commands, then leaves it ready for manual /closer."
argument-hint: "<TASK_ID>"
user-invocable: true
disable-model-invocation: false
---

# /auto-verify-slice

Argumentos recibidos: `$ARGUMENTS`.

Este skill es el punto de entrada moderno equivalente a `.claude/commands/auto-verify-slice.md`.

1. Lee `.claude/commands/auto-verify-slice.md` antes de actuar.
2. Trata ese fichero de comando como procedimiento autoritativo y fuente única de la coreografía.
3. Aplica `$ARGUMENTS` exactamente como lo haría el comando original.
4. No dupliques, reduzcas ni reinterpretes gates, hooks, trailers, worktrees, Git workflow, verify mode ni reglas de cierre.
5. Si este skill y el comando original parecen contradecirse, sigue `.claude/commands/auto-verify-slice.md` y reporta el drift como bloqueo mecánico.

No invoques este skill desde el modelo de forma autónoma. Sólo ejecútalo cuando el usuario lo llame explícitamente como `/auto-verify-slice`.
