---
name: verify-journey
description: "Gate humano end-to-end por journey (no por slice). Se lanza cuando todos los slices de un journey están cerrados y antes de arrancar la siguiente unidad bloqueada. Hard reset + datos reales/proporcionados globales del journey + reproducción del flujo completo como usuario real (multi-pantalla). Resiliente a /clear."
argument-hint: "<JOURNEY_ID>  (ej: J101). Sin argumento = lee runtime-state.pending_journey_verifications[0]"
user-invocable: true
disable-model-invocation: false
---

# /verify-journey

Argumentos recibidos: `$ARGUMENTS`.

Este skill es el punto de entrada moderno equivalente a `.claude/commands/verify-journey.md`.

1. Lee `.claude/commands/verify-journey.md` antes de actuar.
2. Trata ese fichero de comando como procedimiento autoritativo y fuente única de la coreografía.
3. Aplica `$ARGUMENTS` exactamente como lo haría el comando original.
4. No dupliques, reduzcas ni reinterpretes gates, hooks, trailers, worktrees, Git workflow, verify mode ni reglas de cierre.
5. Si este skill y el comando original parecen contradecirse, sigue `.claude/commands/verify-journey.md` y reporta el drift como bloqueo mecánico.

No invoques este skill desde el modelo de forma autónoma. Sólo ejecútalo cuando el usuario lo llame explícitamente como `/verify-journey`.
