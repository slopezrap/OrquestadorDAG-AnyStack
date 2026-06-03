---
name: closer
description: "Cierre manual de una slice ya verificada. Sólo corre después de /next-slice auto-verify o /verify-slice con VERIFY_OUTCOME=verified; genera report, baseline sync, commit, workflow Git y cleanup."
argument-hint: "<TASK_ID>|--task <TASK_ID>  (o terminal con CLAUDE_ACTIVE_TASK_ID exportado)"
user-invocable: true
disable-model-invocation: false
---

# /closer

Argumentos recibidos: `$ARGUMENTS`.

Este skill es el punto de entrada moderno equivalente a `.claude/commands/closer.md`.

1. Lee `.claude/commands/closer.md` antes de actuar.
2. Trata ese fichero de comando como procedimiento autoritativo y fuente única de la coreografía.
3. Aplica `$ARGUMENTS` exactamente como lo haría el comando original.
4. No dupliques, reduzcas ni reinterpretes gates, hooks, trailers, worktrees, Git workflow, verify mode ni reglas de cierre.
5. Si este skill y el comando original parecen contradecirse, sigue `.claude/commands/closer.md` y reporta el drift como bloqueo mecánico.

No invoques este skill desde el modelo de forma autónoma. Sólo ejecútalo cuando el usuario lo llame explícitamente como `/closer`.
