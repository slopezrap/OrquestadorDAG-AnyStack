---
name: promote-followup
description: "Promueve follow-ups propuestos a tasks DAG reales bajo control del main-orchestrator, con aprobación humana, locks, validación DAG y respeto de conflictos activos."
argument-hint: "<FOLLOWUP_ID>|--blocking|--all-proposed|--list"
user-invocable: true
disable-model-invocation: false
---

# /promote-followup

Argumentos recibidos: `$ARGUMENTS`.

Este skill es el punto de entrada moderno equivalente a `.claude/commands/promote-followup.md`.

1. Lee `.claude/commands/promote-followup.md` antes de actuar.
2. Trata ese fichero de comando como procedimiento autoritativo y fuente única de la coreografía.
3. Aplica `$ARGUMENTS` exactamente como lo haría el comando original.
4. No dupliques, reduzcas ni reinterpretes gates, hooks, trailers, worktrees, Git workflow, verify mode ni reglas de cierre.
5. Si este skill y el comando original parecen contradecirse, sigue `.claude/commands/promote-followup.md` y reporta el drift como bloqueo mecánico.

No invoques este skill desde el modelo de forma autónoma. Sólo ejecútalo cuando el usuario lo llame explícitamente como `/promote-followup`.
