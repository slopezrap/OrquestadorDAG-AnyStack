Actúa como arquitecto principal de producto, AI engineer senior, product analyst, technical lead y orquestador DAG.

Voy a darte varios materiales de entrada:

1. Un ZIP "xxxxxxx.zip" con HTML/CSS/JS o prototipo estático de la aplicación.
   - Este ZIP representa cómo deberían quedar visualmente las pantallas.
   - Debes inspeccionar todas las rutas, pantallas, formularios, componentes, textos, navegación, estados visuales, modales, tablas, botones, dashboards, menús, cards, layouts y cualquier comportamiento implícito.
   - El HTML/prototipo es la fuente principal para UX, UI, rutas, pantallas, componentes y estructura visual.

2. Un blueprint de la aplicación: "xxxxxxx.md"
   - Este blueprint representa la intención funcional, reglas, módulos, entidades, algoritmo, lógica de producto, roles, permisos, integraciones, datos y comportamiento esperado.
   - El blueprint es la fuente principal para producto, dominio, lógica de aplicación, lógica central, reglas, permisos, estados, errores, datos, integraciones y verificación.

3. El prompt maestro:
   - `docs/prompts/PROMPT_SOURCE_OF_TRUTH_DAG.md`
   - Debes usarlo como guía metodológica principal para saber cómo rellenar correctamente los documentos source-of-truth.
   - No lo resumas. Aplícalo.

4. Los cinco templates del perfil:
   - `docs/templates/large-without-base/instrucciones.template.md`
   - `docs/templates/large-without-base/PROJECT_TECHNICAL_GUIDE.template.md`
   - `docs/templates/large-without-base/PROJECT_IMPLEMENTATION_CHECKLIST.template.md`
   - `docs/templates/large-without-base/STACK_PROFILE.template.yaml`
   - `docs/templates/large-without-base/UX_CONTRACT.template.md`

Tu objetivo es generar los 5 documentos source-of-truth finales para que después un orquestador DAG pueda construir la aplicación completa.

No estás construyendo la app todavía.
No debes escribir código de la app.
No debes entregar un resumen.
No debes entregar una explicación externa.
Debes entregar los cinco documentos completos, rellenados con máximo detalle, usando el ZIP HTML/prototipo y el blueprint como base real de la aplicación.

Los documentos finales deben ser:

1. `instrucciones.md`
2. `<APP_NAME>_TECHNICAL_GUIDE.md`
3. `<APP_NAME>_IMPLEMENTATION_CHECKLIST.md`
4. `STACK_PROFILE.yaml`
5. `UX_CONTRACT.md`

Sustituye `<APP_NAME>` por el nombre real de la aplicación inferido del blueprint. Si el blueprint no contiene un nombre claro, define uno razonable y úsalo de forma consistente.

Usa exclusivamente el perfil `large-without-base`.
No generes una versión minimal.
No generes una versión resumida.
No uses placeholders vacíos.
No dejes `TBD`, `TODO`, `pendiente`, `por definir`, `etc.`, `...`, ni campos genéricos sin concretar.
No inventes funcionalidades fuera del blueprint salvo que sean necesarias para cerrar coherentemente flujos, errores, estados o verificación; si haces una inferencia, márcala en una sección de decisiones asumidas.

El objetivo es que los cinco documentos sean muy detallados. Para una aplicación grande o modular, apunta a más de 15.000 líneas útiles entre los cinco documentos. No sacrifiques detalle por brevedad.

======================================================================
PRIORIDAD DE FUENTES
======================================================================

Usa esta prioridad cuando haya conflicto entre documentos:

1. Blueprint:
   - manda para lógica funcional, producto, reglas, entidades, permisos, estados, datos, algoritmo, integraciones y alcance.
2. ZIP HTML/prototipo:
   - manda para pantallas, layout, navegación, componentes, copy visible, UX, rutas visuales, formularios, estados UI y comportamiento visible.
3. Prompt maestro `PROMPT_SOURCE_OF_TRUTH_DAG.md`:
   - manda para método, estructura, calidad, cobertura DAG, registry, verificación y forma de rellenar los documentos.
4. Templates `large-without-base`:
   - mandan para la estructura final de cada documento.

Si detectas contradicciones entre blueprint y HTML/prototipo:
- No ignores la contradicción.
- Crea una sección llamada `Discrepancy Resolution Log`.
- Indica:
  - qué dice el blueprint;
  - qué muestra el HTML/prototipo;
  - qué decisión tomas;
  - qué documento/sección queda afectado;
  - qué slice o follow-up lo cubre si aplica.
- Prioriza blueprint para comportamiento y HTML para representación visual.

======================================================================
CADENA LÓGICA OBLIGATORIA
======================================================================

Toda la aplicación debe quedar explicada y trazada con esta cadena:

Journey -> Application Logic -> Core Logic -> Domain Rules
        -> Permissions -> State -> Errors -> Data -> Integrations -> UI -> Audit -> Verify

Debes rellenar cada capa con IDs claros, consistentes y trazables.

Usa esta taxonomía:

- `J-*`:
  Journeys de usuario. Explican qué hace el usuario y qué ve.

- `AL-*`:
  Application Logic. Explica qué hace internamente la aplicación para completar un caso de uso.

- `CORE-*`:
  Core Logic. Explica la lógica central especializada del producto: algoritmo, motor de decisión, motor de precios, recomendador, ranking, matching, scoring, workflow central, cálculo principal o cualquier lógica crítica de negocio.

- `DR-*`:
  Domain Rules. Reglas de dominio o negocio que nunca deben romperse.

- `AUTH-*`:
  Permission / Access Logic. Quién puede hacer qué, sobre qué recurso y en qué condiciones.

- `STATE-*`:
  State / Lifecycle Logic. Estados válidos, transiciones permitidas, transiciones prohibidas y efectos de cada transición.

- `ERR-*`:
  Failure / Recovery Logic. Qué pasa cuando algo falla, cómo se recupera, qué estado queda, qué mensaje ve el usuario y cómo se verifica.

- `DATA-*`:
  Data Lifecycle Logic. Qué datos existen, cómo nacen, cómo cambian, qué campos son mutables/inmutables, cómo se borran, qué se audita y qué retención tienen.

- `INT-*`:
  Integration / Side Effect Logic. APIs externas, emails, pagos, notificaciones, jobs, webhooks, colas, sistemas externos, idempotencia y política de fallo.

- `UI-*`:
  UI Logic. Comportamiento de pantallas, componentes, formularios, loading, empty, error, permission denied, success, disabled/enabled states y copy visible.

- `OBS-*`:
  Observability / Audit Logic. Qué eventos se registran, con qué campos, para qué sirven y dónde se verifican.

- `EVAL-*`:
  Evaluation Logic. Cómo se evalúa de forma determinista que una lógica, algoritmo, flujo, integración o journey funciona correctamente.

No basta con declarar IDs.
Cada ID debe estar explicado y debe aparecer referenciado donde corresponda.

======================================================================
CÓMO DEBES USAR EL ZIP HTML/PROTOTIPO
======================================================================

Primero inspecciona mentalmente la estructura del ZIP.

Extrae del prototipo:

1. Pantallas detectadas.
2. Rutas o URLs implícitas.
3. Layout global.
4. Navegación principal.
5. Navegación secundaria.
6. Formularios.
7. Tablas.
8. Cards.
9. Dashboards.
10. Modales.
11. Drawers.
12. Menús.
13. Estados visuales.
14. Botones primarios/secundarios.
15. Mensajes de error.
16. Empty states.
17. Loading states.
18. Success states.
19. Permission/locked states.
20. Componentes reutilizables.
21. Textos visibles.
22. Datos que se muestran en pantalla.
23. Acciones que parecen disponibles.
24. Diferencias entre roles, si se ven.
25. Diferencias responsive/mobile, si se ven.

Convierte eso en:

- `J-*` dentro de journeys.
- `UI-*` dentro de UX logic.
- Screen inventory.
- Route contract.
- Journey-to-screen matrix.
- Screen-to-endpoint matrix.
- Screen-to-data matrix.
- Screen-to-state matrix.
- Screen-to-error matrix.
- Visual verification requirements.

No ignores pantallas aunque parezcan estáticas.
Si una pantalla aparece en HTML, debe estar representada en `UX_CONTRACT.md` y, si requiere backend/datos, en el checklist.

======================================================================
CÓMO DEBES USAR EL BLUEPRINT
======================================================================

Extrae del blueprint:

1. Objetivo de la aplicación.
2. Problema que resuelve.
3. Usuarios y roles.
4. Módulos funcionales.
5. Entidades principales.
6. Reglas de dominio.
7. Casos de uso.
8. Lógica central o algoritmo.
9. Datos de entrada.
10. Datos de salida.
11. Estados.
12. Permisos.
13. Errores esperados.
14. Integraciones.
15. Jobs/workers.
16. Notificaciones.
17. Auditoría.
18. Seguridad.
19. Requisitos no funcionales.
20. Criterios de aceptación.
21. Criterios de verificación.
22. Cualquier restricción explícita.
23. Cualquier cosa que NO debe hacerse.

Convierte eso en:

- `DR-*`
- `AL-*`
- `CORE-*`
- `AUTH-*`
- `STATE-*`
- `ERR-*`
- `DATA-*`
- `INT-*`
- `OBS-*`
- `EVAL-*`
- slices del DAG
- endpoints
- tablas DB
- workers/jobs
- test/verify commands
- acceptance criteria

Si el blueprint incluye un algoritmo, motor de decisión, fórmula, sistema de scoring, modelo, estrategia, lógica numérica, lógica de recomendación, lógica de matching o proceso central, debes modelarlo como `CORE-*`.

Cada `CORE-*` debe incluir como mínimo:

- propósito;
- trigger;
- inputs;
- preconditions;
- parámetros;
- algoritmo o pasos;
- outputs;
- reglas `DR-*` aplicadas;
- permisos `AUTH-*` relevantes;
- estados `STATE-*` afectados;
- errores `ERR-*`;
- datos `DATA-*`;
- integraciones `INT-*`, si aplica;
- auditoría `OBS-*`;
- evaluación `EVAL-*`;
- slices que lo implementan;
- evidencia esperada.

======================================================================
FASE 1 — INVENTARIO CONCEPTUAL COMPLETO
======================================================================

Antes de generar los cinco documentos finales, realiza internamente un inventario completo.

El inventario debe cubrir:

1. Producto:
   - nombre;
   - objetivo;
   - alcance;
   - no alcance;
   - usuarios;
   - roles;
   - superficies: web, móvil, admin, API, workers, etc.

2. UX desde el HTML:
   - pantallas;
   - rutas;
   - componentes;
   - navegación;
   - formularios;
   - estados visuales;
   - acciones de usuario.

3. Blueprint funcional:
   - módulos;
   - entidades;
   - flujos;
   - reglas;
   - integraciones;
   - algoritmo/lógica central;
   - datos;
   - restricciones.

4. IDs lógicos:
   - `J-*`
   - `AL-*`
   - `CORE-*`
   - `DR-*`
   - `AUTH-*`
   - `STATE-*`
   - `ERR-*`
   - `DATA-*`
   - `INT-*`
   - `UI-*`
   - `OBS-*`
   - `EVAL-*`

5. Arquitectura:
   - frontend;
   - backend;
   - base de datos;
   - workers;
   - integraciones;
   - autenticación;
   - autorización;
   - observabilidad;
   - verificación.

6. DAG:
   - fases;
   - slices;
   - dependencias;
   - conflict groups;
   - write sets;
   - verify mode;
   - risk level;
   - acceptance mínimo;
   - verify mínimo.

Esta fase debe servirte para no olvidarte de nada.
No hace falta entregar el inventario separado si entregas directamente los documentos finales completos, pero sí debes usarlo.

======================================================================
FASE 2 — GENERACIÓN DE LOS CINCO DOCUMENTOS
======================================================================

Genera los cinco documentos finales completos.

Respeta la estructura de los templates `large-without-base`.

No cambies el propósito de los documentos.
No mezcles todos los documentos en uno.
No omitas secciones porque parezcan largas.
No dejes placeholders.

======================================================================
DOCUMENTO 1 — instrucciones.md
======================================================================

Debe contener, con máximo detalle:

1. Visión del producto.
2. Objetivo.
3. Alcance.
4. No alcance.
5. Actores.
6. Roles.
7. Superficies de aplicación.
8. Módulos funcionales.
9. Entidades principales.
10. Glosario funcional.
11. Decisiones asumidas.
12. Discrepancy Resolution Log, si hay conflictos entre blueprint y HTML.
13. `DR-*` Domain Logic Contract.
14. `AL-*` Application Logic Contract.
15. `CORE-*` Core Logic Contract.
16. `AUTH-*` Permission / Access Logic Contract.
17. `STATE-*` State / Lifecycle Logic Contract.
18. `ERR-*` Failure / Recovery Logic Contract.
19. `DATA-*` Data Lifecycle Logic Contract.
20. `INT-*` Integration / Side Effect Logic Contract.
21. `OBS-*` Observability / Audit Contract.
22. `EVAL-*` Evaluation Logic Contract.
23. Reglas de calidad.
24. Reglas de seguridad.
25. Reglas de verificación.
26. Criterios de cierre.

Cada contrato debe tener tablas y explicación.
Cada ID debe ser único.
Cada ID debe tener descripción suficiente para que otro agente pueda implementarlo sin inventar.

======================================================================
DOCUMENTO 2 — <APP_NAME>_TECHNICAL_GUIDE.md
======================================================================

Debe contener, con máximo detalle:

1. Arquitectura técnica general.
2. Stack propuesto.
3. Estructura de repositorio recomendada.
4. Módulos frontend.
5. Módulos backend.
6. Servicios de aplicación.
7. Servicios de dominio.
8. Implementación de `AL-*`.
9. Implementación de `CORE-*`.
10. Implementación de `DR-*`.
11. Implementación de `AUTH-*`.
12. Implementación de `STATE-*`.
13. Implementación de `ERR-*`.
14. Implementación de `DATA-*`.
15. Implementación de `INT-*`.
16. Implementación de `OBS-*`.
17. Implementación de `EVAL-*`.
18. Endpoints.
19. Contratos API.
20. Tablas DB.
21. Migraciones.
22. Transacciones.
23. Idempotencia.
24. Jobs/workers.
25. Webhooks.
26. Seguridad.
27. Configuración.
28. Observabilidad.
29. Logging.
30. Testing.
31. Verification Data Contract `VDATA-*`.
32. Comandos de verificación.
33. Evidencia esperada.
34. Riesgos técnicos.
35. Estrategia de implementación por fases.

Cada endpoint debe indicar:
- método;
- ruta;
- propósito;
- request;
- response;
- errores;
- permisos;
- `AL-*`;
- `CORE-*`, si aplica;
- `DR-*`;
- `STATE-*`;
- `ERR-*`;
- tablas DB;
- verify mínimo.

Cada tabla DB debe indicar:
- campos;
- tipo conceptual;
- propósito;
- claves;
- índices;
- relaciones;
- campos auditables;
- lifecycle `DATA-*`.

Cada `CORE-*` debe mapearse a:
- servicios;
- funciones;
- módulos;
- pruebas;
- fixtures;
- evidencia.

======================================================================
DOCUMENTO 3 — <APP_NAME>_IMPLEMENTATION_CHECKLIST.md
======================================================================

Este documento debe contener el DAG completo.

Debe incluir un `Canonical Coverage Registry` muy detallado.

Cada fila/slice debe tener como mínimo estas columnas:

- `Slice ID`
- `Tipo`
- `Target`
- `Step`
- `Product increment`
- `Build state`
- `Risk level`
- `Verify mode`
- `Depends on`
- `Conflict group`
- `Write set`
- `Journey refs`
- `Pantalla/Ruta`
- `Endpoint`
- `Tablas DB`
- `Origen-Instr`
- `Origen-TechGuide`
- `Acceptance mínimo`
- `Verify mínimo`
- `Domain rule refs`
- `Application logic refs`
- `Core logic refs`
- `Permission refs`
- `State refs`
- `Failure refs`
- `Integration refs`
- `UI refs`
- `Data refs`
- `Observability refs`
- `Evaluation refs`

Reglas obligatorias del checklist:

1. `Depends on` es obligatorio.
   - Usa `—` solo para raíces reales.
   - No dejes la celda vacía.
   - No omitas dependencias por brevedad.

2. `Write set` es obligatorio.
   - Debe indicar rutas, módulos, carpetas, tablas o recursos que la slice puede tocar.

3. `Conflict group` es obligatorio.
   - Debe permitir detectar slices que no deben ejecutarse en paralelo.

4. `Verify mínimo` debe ser real.
   - No vale “comprobar que funciona”.
   - Debe indicar comando, navegación, datos, endpoint, DB, log, screenshot o evidencia concreta.

5. Cada slice visible debe referenciar `J-*` y `UI-*`.

6. Cada slice backend debe referenciar `AL-*`.

7. Cada slice que toque lógica central debe referenciar `CORE-*` y `EVAL-*`.

8. Cada slice que toque reglas debe referenciar `DR-*`.

9. Cada slice con permisos debe referenciar `AUTH-*`.

10. Cada slice con estados debe referenciar `STATE-*`.

11. Cada slice con errores o casos borde debe referenciar `ERR-*`.

12. Cada slice con datos persistidos debe referenciar `DATA-*`.

13. Cada slice con integración externa o side effect debe referenciar `INT-*`.

14. Cada slice crítica o core debe referenciar `OBS-*`.

15. No debe haber IDs referenciados que no estén definidos en los otros documentos.

16. No debe haber IDs definidos que nunca se implementen o verifiquen, salvo que estén marcados explícitamente como out-of-scope.

Además del registry, incluye:
- fases;
- waves;
- dependencias principales;
- estrategia de paralelización;
- riesgos;
- gates;
- phase gates;
- criterios de cierre;
- coverage matrix.

======================================================================
DOCUMENTO 4 — STACK_PROFILE.yaml
======================================================================

Debe ser YAML válido.

Debe declarar con detalle:

1. Nombre de la app.
2. Tipo de producto.
3. Superficies:
   - web;
   - mobile;
   - admin;
   - API;
   - workers;
   - jobs;
   - integraciones.

4. Frontend:
   - framework;
   - rutas;
   - visual check;
   - browser/mobile MCP requerido;
   - build/test commands.

5. Backend:
   - framework;
   - endpoints;
   - workers;
   - jobs;
   - test commands.

6. Database:
   - engine;
   - migration tool;
   - reset/seed commands;
   - tables expected.

7. Core logic:
   - required;
   - description;
   - deterministic/probabilistic/hybrid;
   - requires external data;
   - requires scheduled jobs;
   - requires reproducible tests;
   - requires auditability;
   - expected refs.

8. Logic contracts:
   - require_application_logic_refs;
   - require_core_logic_refs;
   - require_permission_refs;
   - require_state_refs;
   - require_failure_refs;
   - require_integration_refs_when_applicable;
   - require_ui_refs_for_visible_slices;
   - require_data_refs_when_persistent;
   - require_observability_refs_for_sensitive_or_core_logic;
   - require_evaluation_refs_for_core_logic.

9. Verification data:
   - seed/reset commands;
   - fixture policy;
   - real/provided data policy;
   - cleanup commands;
   - evidence expected.

10. Integrations:
   - external APIs;
   - auth providers;
   - payment providers;
   - email;
   - push notifications;
   - data providers;
   - broker/API/etc. si aplica.

11. Runtime:
   - docker;
   - compose;
   - ports;
   - logs;
   - Rancher/workers si aplica.

12. Git workflow.
13. Verification commands.
14. Observability.
15. Security.
16. Constraints.

No dejes YAML inválido.
No uses comentarios como sustituto de valores reales.
Usa strings claros cuando haya incertidumbre justificada.

======================================================================
DOCUMENTO 5 — UX_CONTRACT.md
======================================================================

Debe usar el ZIP HTML/prototipo como fuente principal.

Debe contener, con máximo detalle:

1. UX overview.
2. Personas y roles.
3. Information architecture.
4. Navigation map.
5. Route contract.
6. Screen inventory.
7. Journey-to-screen matrix.
8. Screen-to-endpoint/data matrix.
9. Screen-to-state matrix.
10. Screen-to-error matrix.
11. `J-*` Journey Contract.
12. `UI-*` UI Logic Contract.
13. Component inventory.
14. Layout system.
15. Responsive behavior.
16. Mobile behavior, si aplica.
17. Form contract.
18. Validation messages.
19. Loading states.
20. Empty states.
21. Error states.
22. Permission denied states.
23. Success states.
24. Offline/degraded states.
25. Copy visible.
26. Accessibility.
27. Design tokens, si se infieren.
28. Visual verification checklist.
29. Screenshots/evidence expected.
30. UX self-review.

Cada pantalla debe tener:

- Screen ID;
- route;
- purpose;
- allowed roles;
- visible data;
- actions;
- primary CTA;
- secondary actions;
- loading state;
- empty state;
- error state;
- permission denied state;
- success state;
- related `J-*`;
- related `AL-*`;
- related `CORE-*`, si aplica;
- related `AUTH-*`;
- related `STATE-*`;
- related `ERR-*`;
- related `DATA-*`;
- related endpoints;
- verify mínimo visual.

No basta con listar pantallas.
Debes explicar cómo se comportan.

======================================================================
FASE 3 — REVISIÓN QUIRÚRGICA OBLIGATORIA
======================================================================

Después de generar los cinco documentos, revisa quirúrgicamente tu propio resultado antes de entregarlo.

Haz una segunda pasada completa.

Busca y corrige:

1. IDs duplicados.
2. IDs declarados pero nunca usados.
3. IDs usados pero no declarados.
4. `J-*` sin pantalla.
5. `J-*` sin slice.
6. `AL-*` sin slice.
7. `CORE-*` sin `EVAL-*`.
8. `CORE-*` sin inputs/outputs claros.
9. `CORE-*` sin verify determinista.
10. `DR-*` sin enforcement.
11. `AUTH-*` sin allow/deny.
12. `STATE-*` sin transiciones válidas.
13. `STATE-*` sin transiciones prohibidas.
14. `ERR-*` sin recovery.
15. `ERR-*` sin mensaje de usuario cuando aplica.
16. `DATA-*` sin lifecycle.
17. `INT-*` sin idempotencia o política de fallo.
18. `UI-*` sin pantalla.
19. Pantallas sin loading/empty/error/permission/success cuando aplique.
20. Endpoints sin consumidor.
21. Endpoints sin permisos.
22. Tablas DB sin uso.
23. Slices sin `Depends on`.
24. Slices sin `Conflict group`.
25. Slices sin `Write set`.
26. Slices sin `Verify mínimo`.
27. Slices con verify genérico.
28. Slices que mezclan demasiadas responsabilidades.
29. Dependencias circulares.
30. Fases imposibles de ejecutar.
31. Inconsistencias entre HTML/prototipo y blueprint.
32. Inconsistencias entre documentos.
33. Campos con `TBD`, `TODO`, `pendiente`, `por definir`, `...` o placeholders.
34. Duplicidad de secciones.
35. Secciones vacías.
36. Registry sin columnas requeridas.
37. Falta de datos de verificación.
38. Falta de auditoría en flujos sensibles.
39. Falta de trazabilidad desde UI hasta DB/API.
40. Falta de trazabilidad desde Core Logic hasta Verify.

Si encuentras un problema, no lo listes solamente: corrígelo en los documentos antes de entregar.

Incluye al final de cada documento una sección breve de self-review completada, indicando que la revisión fue aplicada.

======================================================================
FORMATO DE ENTREGA
======================================================================

Entrega los cinco documentos como archivos separados o como bloques separados con estos encabezados exactos:


# FILE: docs/source-of-truth/instrucciones.md
# FILE: docs/source-of-truth/<APP_NAME>_TECHNICAL_GUIDE.md
# FILE: docs/source-of-truth/<APP_NAME>_IMPLEMENTATION_CHECKLIST.md
# FILE: docs/source-of-truth/STACK_PROFILE.yaml
# FILE: docs/source-of-truth/UX_CONTRACT.md
