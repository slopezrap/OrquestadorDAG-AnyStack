---
name: next-wave
description: "Lista la wave DAG actual: tasks ready independientes, deps, posibles conflictos y comandos para abrir terminales paralelos. No implementa ni spawnea agentes."
argument-hint: "[opcional: phase id o límite N; sin argumento = earliest incomplete phase]"
user-invocable: true
disable-model-invocation: false
---

# /next-wave

Argumentos recibidos: `$ARGUMENTS`.

Este skill es el punto de entrada moderno equivalente a `.claude/commands/next-wave.md`.

1. Lee `.claude/commands/next-wave.md` antes de actuar.
2. Trata ese fichero de comando como procedimiento autoritativo y fuente única de la coreografía.
3. Aplica `$ARGUMENTS` exactamente como lo haría el comando original.
4. No dupliques, reduzcas ni reinterpretes gates, hooks, trailers, worktrees, Git workflow, verify mode ni reglas de cierre.
5. Si este skill y el comando original parecen contradecirse, sigue `.claude/commands/next-wave.md` y reporta el drift como bloqueo mecánico.

No invoques este skill desde el modelo de forma autónoma. Sólo ejecútalo cuando el usuario lo llame explícitamente como `/next-wave`.
