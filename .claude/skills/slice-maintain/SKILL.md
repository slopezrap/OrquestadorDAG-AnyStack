---
name: slice-maintain
description: "Mantenimiento entre slices. Subcomandos — `clean` (limpieza conservadora), `compact` (PROGRESS.md/memory global) y `compact-agent-memory` (memorias vivas de agentes con snapshot íntegro). Dry-run manual por defecto; next-wave auto-compacta memorias >250 líneas."
argument-hint: "clean [--apply]  |  compact [--apply] [--keep N] [--threshold-days D]  |  compact-agent-memory [--apply] [--agent NAME|--all] [--threshold-lines N]"
user-invocable: true
disable-model-invocation: false
---

# /slice-maintain

Argumentos recibidos: `$ARGUMENTS`.

Este skill es el punto de entrada moderno equivalente a `.claude/commands/slice-maintain.md`.

1. Lee `.claude/commands/slice-maintain.md` antes de actuar.
2. Trata ese fichero de comando como procedimiento autoritativo y fuente única de la coreografía.
3. Aplica `$ARGUMENTS` exactamente como lo haría el comando original.
4. No dupliques, reduzcas ni reinterpretes gates, hooks, trailers, worktrees, Git workflow, verify mode ni reglas de cierre.
5. Si este skill y el comando original parecen contradecirse, sigue `.claude/commands/slice-maintain.md` y reporta el drift como bloqueo mecánico.

No invoques este skill desde el modelo de forma autónoma. Sólo ejecútalo cuando el usuario lo llame explícitamente como `/slice-maintain`.
