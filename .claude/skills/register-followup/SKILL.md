---
name: register-followup
description: "Convierte hallazgos reales de validator/tester/verify en una propuesta formal y, con aprobación humana, en una task DAG + YAML + source-of-truth amendment."
argument-hint: "propose|promote|waive|list ..."
user-invocable: true
disable-model-invocation: false
---

# /register-followup

Argumentos recibidos: `$ARGUMENTS`.

Este skill es el punto de entrada moderno equivalente a `.claude/commands/register-followup.md`.

1. Lee `.claude/commands/register-followup.md` antes de actuar.
2. Trata ese fichero de comando como procedimiento autoritativo y fuente única de la coreografía.
3. Aplica `$ARGUMENTS` exactamente como lo haría el comando original.
4. No dupliques, reduzcas ni reinterpretes gates, hooks, trailers, worktrees, Git workflow, verify mode ni reglas de cierre.
5. Si este skill y el comando original parecen contradecirse, sigue `.claude/commands/register-followup.md` y reporta el drift como bloqueo mecánico.

No invoques este skill desde el modelo de forma autónoma. Sólo ejecútalo cuando el usuario lo llame explícitamente como `/register-followup`.
