---
name: next-slice
description: "Arranca una slice DAG: plan aprobado, implementación, validator ‖ tester, y si todo va bien continúa automáticamente con la verificación humana-real de /verify-slice. No cierra; deja la slice lista para /closer manual."
argument-hint: "<TASK_ID>  (o terminal con CLAUDE_ACTIVE_TASK_ID ya exportado)"
user-invocable: true
disable-model-invocation: false
---

# /next-slice

Argumentos recibidos: `$ARGUMENTS`.

Este skill es el punto de entrada moderno equivalente a `.claude/commands/next-slice.md`.

1. Lee `.claude/commands/next-slice.md` antes de actuar.
2. Trata ese fichero de comando como procedimiento autoritativo y fuente única de la coreografía.
3. Aplica `$ARGUMENTS` exactamente como lo haría el comando original.
4. No dupliques, reduzcas ni reinterpretes gates, hooks, trailers, worktrees, Git workflow, verify mode ni reglas de cierre.
5. Si este skill y el comando original parecen contradecirse, sigue `.claude/commands/next-slice.md` y reporta el drift como bloqueo mecánico.

No invoques este skill desde el modelo de forma autónoma. Sólo ejecútalo cuando el usuario lo llame explícitamente como `/next-slice`.
