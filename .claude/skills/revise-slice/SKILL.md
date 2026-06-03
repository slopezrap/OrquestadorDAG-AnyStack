---
name: revise-slice
description: "Reabre una slice concreta ya implementada para corregir issues sin inventar una slice nueva. Mantiene TASK_ID, memoria, DAG, journeys y cableado; luego revalida, ejecuta verify-slice y deja el cierre correctivo para /closer manual."
argument-hint: "<TASK_ID> \\\"motivo o hallazgo\\\""
user-invocable: true
disable-model-invocation: false
---

# /revise-slice

Argumentos recibidos: `$ARGUMENTS`.

Este skill es el punto de entrada moderno equivalente a `.claude/commands/revise-slice.md`.

1. Lee `.claude/commands/revise-slice.md` antes de actuar.
2. Trata ese fichero de comando como procedimiento autoritativo y fuente única de la coreografía.
3. Aplica `$ARGUMENTS` exactamente como lo haría el comando original.
4. No dupliques, reduzcas ni reinterpretes gates, hooks, trailers, worktrees, Git workflow, verify mode ni reglas de cierre.
5. Si este skill y el comando original parecen contradecirse, sigue `.claude/commands/revise-slice.md` y reporta el drift como bloqueo mecánico.

No invoques este skill desde el modelo de forma autónoma. Sólo ejecútalo cuando el usuario lo llame explícitamente como `/revise-slice`.
