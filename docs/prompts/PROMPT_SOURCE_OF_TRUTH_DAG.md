# PROMPT MAESTRO — Source of Truth DAG para large-without-base

Usa este prompt con ChatGPT para generar el source-of-truth completo de `docs/source-of-truth/` a partir de `docs/templates/large-without-base/`. El objetivo es que el orquestador pueda construir una aplicación real desde cero en modo DAG: producto completo, journeys reales, UX exhaustiva, lógica de aplicación, lógica central especializada, reglas de dominio, permisos, estados, errores, datos, integraciones, auditoría, verificación real y slices trazables.

Este prompt está preparado para el perfil **large-without-base**. No está pensado para una salida mínima ni resumida. Aunque el repositorio conserva otros perfiles (`docs/templates/minimal` y `docs/templates/large-with-base`) para otros usos, en esta ejecución debes trabajar como si el producto naciera desde cero usando **solo** `docs/templates/large-without-base`.

## 0. Objetivo de salida

Entrega siempre un contrato completo, no un diff parcial ni una guía resumida. Estos son los 5 source-of-truth docs que debe consumir el orquestador.

No generes schemas, golden app, doctor reports ni artefactos de `orchestrator-state/`. Entrega exactamente 5 documentos en `docs/source-of-truth/`:

1. `docs/source-of-truth/instrucciones.md`
2. `docs/source-of-truth/<APP>_TECHNICAL_GUIDE.md`
3. `docs/source-of-truth/<APP>_IMPLEMENTATION_CHECKLIST.md`
4. `docs/source-of-truth/STACK_PROFILE.yaml`
5. `docs/source-of-truth/UX_CONTRACT.md`

Los documentos deben estar suficientemente detallados para que el orquestador pueda ejecutar la construcción sin tener que inventar producto, lógica, endpoints, datos, estados ni verificación. El objetivo operativo para `large-without-base` es que el conjunto de los 5 documentos supere **15.000 líneas útiles** cuando la aplicación sea grande/modular. No rellenes con ruido, lorem ipsum ni texto decorativo: aumenta el detalle con contratos, matrices, casos borde, filas de registry, flujos, estados, errores, datos, endpoints, verificación, UX y trazabilidad real.

Si el usuario entrega una idea incompleta, no reduzcas la salida. Expande con criterio de producto, declara supuestos explícitos, crea módulos coherentes y deja el source-of-truth completo. No dejes TODOs.

## 1. Perfil fijo: large-without-base

Usa **large-without-base** cuando la aplicación empieza desde cero y debe construirse con un contrato completo. Este prompt asume ese caso.

Debes leer y rellenar estos templates:

1. `docs/templates/large-without-base/instrucciones.template.md`
2. `docs/templates/large-without-base/PROJECT_TECHNICAL_GUIDE.template.md`
3. `docs/templates/large-without-base/PROJECT_IMPLEMENTATION_CHECKLIST.template.md`
4. `docs/templates/large-without-base/STACK_PROFILE.template.yaml`
5. `docs/templates/large-without-base/UX_CONTRACT.template.md`

Los perfiles `docs/templates/minimal` y `docs/templates/large-with-base` existen en el repositorio, pero no los uses para esta generación. No generes una versión pequeña. No heredes baseline. No copies rutas, endpoints, tablas, pantallas ni journeys de `docs/product-baseline/` salvo que el usuario diga explícitamente que hay un producto existente que debe heredarse.

Para una app nueva:

- usa `Product increment=v1` o el nombre de release inicial;
- usa `Build state=planned` para todo lo que debe construirse;
- no uses `Build state=done` salvo que el usuario proporcione una base existente real y pida conservarla;
- no generes `v0` heredado;
- no reduzcas el alcance por comodidad;
- no conviertas el proyecto en un ejemplo mínimo.

## 2. Qué significa rellenar bien

Rellenar bien no es escribir mucho texto narrativo. Rellenar bien significa que cada parte importante de la aplicación queda expresada como contrato trazable.

Debes poder reconstruir esta cadena desde cualquier slice productiva:

```text
Journey -> Application Logic -> Core Logic -> Domain Rules
        -> Permissions -> State -> Errors -> Data -> Integrations -> UI -> Audit -> Verify
```

Y también esta cadena técnica:

```text
Slice -> Pantalla/Ruta -> Endpoint/Job/Event -> Servicio -> Tabla/Dato -> Side effect -> Test/Verify -> Evidencia
```

Si alguna parte no aplica, declara `—` o `NO APLICA` con razón concreta. No uses `NO APLICA` para evitar pensar.


Además de la cadena lógica, debes generar un **Architecture Blueprint overlay** inspirado en arc42. arc42 no sustituye a la lógica de producto: complementa la cadena con arquitectura, restricciones, calidad, contexto, runtime, despliegue, decisiones y riesgos. Usa IDs `A42-*` y referencia esos IDs en la columna `Architecture refs` del registry.

```text
Architecture Blueprint (A42-*)
  -> Context/Constraints/Quality/Solution/Building Blocks/Runtime/Deployment/Risks
  -> Journey -> Application Logic -> Core Logic -> Domain Rules
          -> Permissions -> State -> Errors -> Data -> Integrations -> UI -> Audit -> Verify
```

Las secciones arc42 que debes cubrir son:

| A42 ID | arc42 section | Qué debes rellenar |
|---|---|---|
| A42-01 | Introduction and Goals | objetivos de arquitectura, stakeholders, drivers y quality goals top |
| A42-02 | Constraints | restricciones técnicas, organizativas, legales, UX, datos y stack |
| A42-03 | Context and Scope | límites del sistema, sistemas externos, APIs vecinas, actores externos |
| A42-04 | Solution Strategy | estrategia arquitectónica principal y trade-offs |
| A42-05 | Building Block View | módulos, capas, componentes, ownership y boundaries |
| A42-06 | Runtime View | escenarios dinámicos, secuencias, jobs, eventos y flujos críticos |
| A42-07 | Deployment View | entornos, runtime, contenedores, workers, DB, cloud/local, puertos |
| A42-08 | Crosscutting Concepts | auth, seguridad, errores, logging, idempotencia, caching, i18n, observabilidad |
| A42-09 | Architecture Decisions | ADRs reales, alternativas, consecuencias y estado |
| A42-10 | Quality Requirements | performance, seguridad, mantenibilidad, usabilidad, resiliencia, escenarios medibles |
| A42-11 | Risks and Technical Debt | riesgos, deuda aceptada, mitigaciones y follow-ups |
| A42-12 | Glossary | glosario técnico y dominio para evitar ambigüedad |

No copies texto genérico de arc42. Rellena cada `A42-*` con decisiones concretas de esta aplicación.

## 3. Método de trabajo obligatorio

Trabaja en tres pasadas.

### Pasada 1 — Inventario conceptual

Antes de escribir los cinco documentos, construye mentalmente el mapa de la app:

- actores y roles;
- permisos;
- módulos;
- journeys reales;
- pantallas/rutas;
- casos de uso internos;
- lógica central o algoritmo;
- reglas de dominio;
- entidades y datos;
- estados y transiciones;
- errores y recuperación;
- integraciones y side effects;
- eventos de auditoría;
- verificaciones necesarias;
- datos reales/proporcionados para verificar;
- architecture blueprint `A42-*`;
- riesgos y slices.

No entregues esta pasada como documento separado salvo que el usuario lo pida. Úsala para rellenar bien los cinco documentos.

### Pasada 2 — Generación completa

Genera los 5 documentos completos. Mantén los títulos y estructuras de los templates, reemplaza todos los placeholders `{{...}}` y amplía cada sección con contenido real.

No escribas secciones vacías. No uses frases como `pendiente`, `por definir`, `TBD`, `TODO`, `etc.`, `y demás` o `similar` como sustituto de requisitos.

### Pasada 3 — Revisión quirúrgica

Después de generar los documentos, revísalos como si fueras el `validator` del orquestador:

- busca IDs declarados pero no referenciados;
- busca IDs referenciados pero no declarados;
- busca journeys sin endpoint o sin pantalla;
- busca pantallas sin estados UI;
- busca endpoints sin consumidor;
- busca tablas mencionadas solo en un documento;
- busca slices sin `Depends on`;
- busca slices sin `Write set`;
- busca slices sin `Verify mínimo` real;
- busca `Verify mode=auto` mal usado;
- busca duplicidades de secciones, IDs o tablas contradictorias;
- busca lógica central sin evaluación;
- busca errores sin recovery;
- busca integraciones sin idempotencia;
- busca permisos sin condición de allow/deny;
- busca estados sin transición prohibida;
- busca auditabilidad ausente en lógica crítica.

Si detectas un fallo, no lo menciones como nota final: corrígelo insertando el cambio en los documentos. La entrega final debe ser la versión corregida.

## 4. Reglas generales de los templates

Los templates son contratos, no sugerencias decorativas.

- Reemplaza todos los placeholders `{{...}}` con contenido real.
- Mantén los nombres de columnas requeridas exactamente.
- Las líneas `>>> MODELO`, ejemplos y tablas de ejemplo explican el formato; no copies ejemplos como requisitos reales.
- Las secciones marcadas como `CABLEADO`, `OBLIGATORIO`, `no negociable` o `cero tolerancia` deben cumplirse literalmente.
- No añadas columnas dentro de tablas canónicas salvo que el template lo permita.
- Si necesitas contexto adicional, crea una sección narrativa con IDs y enlázala al registry.
- Todo elemento creado en un documento debe tener wire en los otros documentos.
- Las secciones append-only de runtime, si existen, deben quedar vacías al generar docs iniciales.
- El orquestador rellena runtime/follow-ups después; ChatGPT no debe simular estado runtime.
- `NO APLICA` debe incluir razón.
- `internal/no-front` solo es válido para endpoints internos, jobs, webhooks o tareas sin pantalla directa.

## 5. Contratos lógicos genéricos

No reduzcas la app a pantallas y endpoints. Declara la lógica que el orquestador debe poder rastrear.

Usa estas familias de IDs:

```text
A42-*      Architecture Blueprint / arc42 overlay
DR-*       Domain Logic / reglas de dominio
AL-*       Application Logic / casos de uso internos
CORE-*     Core Logic / algoritmo, motor central o lógica especializada
J-*        Journey / recorrido real de usuario
AUTH-*     Permission Logic / permisos y acceso
STATE-*    State Logic / estados y transiciones
ERR-*      Failure Logic / errores y recuperación
INT-*      Integration Logic / integraciones y side effects
UI-*       UI Logic / comportamiento de pantalla
DATA-*     Data Logic / ciclo de vida de datos
OBS-*      Observability Logic / auditoría y trazabilidad
EVAL-*     Evaluation Logic / evaluación determinista
```

No son adornos. Son el mapa para que el orquestador no improvise.

## 6. Architecture Blueprint — `A42-*`

La Architecture Blueprint cubre lo que suele perderse cuando solo se piensa en pantallas y endpoints: contexto, límites, restricciones, estrategia, módulos, runtime, despliegue, decisiones, calidad, riesgos y glosario. Está inspirada en arc42 y debe quedar repartida en los 5 documentos sin crear un sexto source-of-truth.

Cada `A42-*` debe incluir:

- ID;
- sección arc42;
- contenido concreto para esta app;
- drivers y restricciones;
- decisiones tomadas;
- alternativas descartadas si aplica;
- módulos/slices afectados;
- `AL-*`, `CORE-*`, `DR-*`, `AUTH-*`, `STATE-*`, `ERR-*`, `DATA-*`, `INT-*`, `UI-*`, `OBS-*` o `EVAL-*` relacionados;
- riesgo si se ignora;
- verificación o evidencia;
- ADR asociado si hay decisión no trivial.

Reglas:

- `A42-04` Solution Strategy debe explicar por qué esta arquitectura sirve para construir la aplicación.
- `A42-05` Building Block View debe mapearse a módulos, carpetas, servicios o componentes reales.
- `A42-06` Runtime View debe explicar flujos dinámicos críticos, no solo arquitectura estática.
- `A42-07` Deployment View debe coincidir con `STACK_PROFILE.yaml`.
- `A42-08` Crosscutting Concepts debe enlazar con `AUTH-*`, `ERR-*`, `OBS-*`, seguridad, idempotencia y logging.
- `A42-10` Quality Requirements debe tener escenarios medibles y enlazar con `EVAL-*`.
- `A42-11` Risks and Technical Debt debe producir slices de hardening o follow-ups si el riesgo no queda cerrado.
- Cada slice que implemente o verifique una pieza arquitectónica debe rellenar `Architecture refs`.

## 6. Domain Logic — `DR-*`

La Domain Logic contiene reglas de negocio que no pueden romperse aunque cambie la UI, el backend, el job o la integración.

Cada `DR-*` debe explicar:

- ID;
- nombre;
- regla exacta;
- entidades afectadas;
- condición de aplicación;
- ejemplos válidos;
- ejemplos prohibidos;
- error esperado cuando se viola;
- dónde debe aplicarse: UI, API, servicio, DB, job, integración;
- cómo se verifica;
- slices que la implementan o la validan.

Una buena `DR-*` es verificable. No escribas reglas vagas como `el usuario debe tener buena experiencia`.

Ejemplo de forma, no de contenido obligatorio:

```text
DR-001: Una operación no puede confirmarse si el dato base está obsoleto.
Aplica a: cálculo, endpoint de confirmación, UI de resumen, auditoría.
Violación: si data_timestamp excede el umbral definido por CORE-001.
Verify: fixture con dato stale debe bloquear operación y registrar OBS-003.
```

## 7. Application Logic — `AL-*`

La Application Logic describe casos de uso internos. Un journey dice qué hace el usuario; una `AL-*` dice qué hace el sistema para que eso ocurra correctamente.

Cada `AL-*` debe incluir:

- ID;
- nombre;
- objetivo;
- trigger;
- actor/rol;
- preconditions;
- permission refs `AUTH-*`;
- steps internos numerados;
- core refs `CORE-*` usados;
- domain refs `DR-*` aplicadas;
- state refs `STATE-*` modificados;
- data refs `DATA-*` afectados;
- integration refs `INT-*` disparadas;
- failure refs `ERR-*` esperadas;
- observability refs `OBS-*` obligatorias;
- outputs;
- postconditions;
- idempotencia si hay efectos externos o reintentos;
- verify mínimo;
- slices relacionadas.

No escribas una `AL-*` como una frase de producto. Debe parecer un caso de uso ejecutable.

Una buena `AL-*` permite a un developer implementar el flujo sin adivinar el orden de operaciones.

## 8. Core Logic — `CORE-*`

`CORE-*` es la lógica central especializada del producto. Es genérica: puede ser un algoritmo de bolsa, un motor de precios, ranking de papers, matching, recomendación, cálculo de rutas, scoring, motor de reservas, clasificador, optimizador, workflow de aprobación o cualquier lógica que haga única a la app.

No hagas categorías específicas por dominio. Usa `CORE-*` y describe el motor con detalle.

Cada `CORE-*` debe incluir:

- ID;
- nombre;
- propósito;
- entrada/input;
- salida/output;
- parámetros;
- datasets/fixtures necesarios;
- preconditions;
- pseudocódigo o pasos deterministas;
- reglas `DR-*` aplicadas;
- casos borde;
- errores `ERR-*`;
- datos `DATA-*` leídos/escritos;
- estado `STATE-*` afectado;
- auditabilidad `OBS-*`;
- evaluación `EVAL-*`;
- versionado si el algoritmo cambia;
- reproducibilidad;
- performance/latencia si importa;
- slices que lo implementan.

Si la aplicación no tiene algoritmo numérico, igualmente debe haber `CORE-*` para su motor central. Ejemplos:

- motor de pricing;
- motor de permisos avanzado;
- motor de matching;
- motor de generación de informes;
- ranking de contenidos;
- workflow de aprobación;
- scoring de riesgo;
- reglas de asignación;
- pipeline documental;
- lógica de recomendaciones;
- consolidación de datos.

Solo usa `CORE-001: NO APLICA` si el producto realmente no tiene ninguna lógica central especializada. En una app grande, casi siempre hay alguna.

## 9. Journey — `J-*`

Un journey es un recorrido real end-to-end o multi-superficie desde el punto de vista de un usuario o actor.

No llames journey a:

- un tab;
- una pantalla aislada;
- un componente;
- un endpoint interno;
- un state handler;
- una subtarea técnica.

Cada `J-*` debe incluir:

- ID;
- actor/persona;
- objetivo;
- preconditions;
- pantallas/rutas;
- acciones del usuario;
- endpoints/jobs/eventos implicados;
- datos leídos/escritos;
- state transitions;
- errores visibles;
- UI states;
- application logic refs `AL-*`;
- core logic refs `CORE-*` si el journey toca lógica central;
- domain refs `DR-*`;
- permission refs `AUTH-*`;
- verify mínimo;
- slices implicadas.

Cada journey debe poder verificarse con datos reales/proporcionados.

## 10. Permission Logic — `AUTH-*`

`AUTH-*` define quién puede hacer qué, sobre qué recurso y bajo qué condición.

Cada `AUTH-*` debe incluir:

- ID;
- actor/rol;
- recurso;
- acción;
- condición `allowed when`;
- condición `denied when`;
- error esperado;
- UI behavior cuando se deniega;
- endpoint/service enforcement;
- datos necesarios para evaluar permiso;
- verify mínimo;
- slices relacionadas.

No mezcles permisos con preferencias UI. Permiso significa autorización real.

Ejemplos de cosas que deben estar cubiertas:

- usuario ve solo sus datos;
- admin ve datos de su organización;
- actor no puede aprobar su propia solicitud si aplica;
- usuario no puede ejecutar una acción irreversible sin aceptación;
- credenciales o secretos nunca se exponen;
- modo lectura vs modo escritura;
- permisos para jobs/webhooks internos.

## 11. State Logic — `STATE-*`

`STATE-*` describe estados válidos, transiciones permitidas, transiciones prohibidas y eventos que cambian estado.

Cada `STATE-*` debe incluir:

- ID;
- entidad o proceso;
- lista de estados;
- estado inicial;
- estados terminales;
- transiciones permitidas;
- transiciones prohibidas;
- evento/acción que dispara cada transición;
- permission refs necesarios;
- domain refs que la protegen;
- errores cuando una transición se deniega;
- audit events;
- verify mínimo.

No basta con listar estados. Debes explicar cómo se cambia de uno a otro y qué está prohibido.

## 12. Failure / Recovery Logic — `ERR-*`

`ERR-*` define qué pasa cuando algo sale mal. No construyas solo el camino feliz.

Cada `ERR-*` debe incluir:

- ID;
- escenario;
- causa típica;
- comportamiento esperado;
- mensaje visible si aplica;
- status code si aplica;
- state change;
- data rollback o compensación;
- retry policy;
- idempotency key si aplica;
- observability refs;
- verification.

Cubre, cuando aplique:

- permisos denegados;
- datos vacíos;
- validación fallida;
- red caída;
- integración externa caída;
- timeout;
- duplicados;
- reintento;
- datos obsoletos;
- estado inválido;
- conflicto de concurrencia;
- parcial failure;
- pérdida de conexión en móvil;
- sesión expirada;
- input malformado;
- no hay datos para verificar;
- fallo de job/worker.

## 13. Data Logic — `DATA-*`

`DATA-*` explica el ciclo de vida de los datos. No se limita a tablas.

Cada `DATA-*` debe incluir:

- ID;
- entidad/dato;
- owner;
- creación;
- campos mutables;
- campos inmutables;
- validaciones;
- relaciones;
- borrado físico/lógico;
- retención;
- privacidad;
- auditoría;
- índices o constraints relevantes;
- seeds/fixtures de verificación;
- slices que lo crean o modifican.

Una tabla DB dice cómo se guarda algo. `DATA-*` dice qué significa y cómo vive.

## 14. Integration / Side Effect Logic — `INT-*`

`INT-*` describe sistemas externos o side effects internos.

Cada `INT-*` debe incluir:

- ID;
- trigger;
- sistema externo o interno;
- acción;
- payload mínimo;
- respuesta esperada;
- idempotency key;
- retry policy;
- timeout;
- failure behavior;
- datos persistidos;
- evento auditado;
- verify mínimo.

Cubre, cuando aplique:

- APIs externas;
- webhooks;
- emails;
- push notifications;
- pagos;
- broker/proveedor de datos;
- OCR/document processing;
- colas;
- workers;
- cron jobs;
- almacenamiento externo;
- auth provider;
- analytics;
- exportaciones.

## 15. UI Logic — `UI-*`

`UI-*` describe el comportamiento de pantallas y componentes visibles. No sustituye a journeys.

Cada `UI-*` debe incluir:

- ID;
- pantalla/ruta;
- condición;
- comportamiento visible;
- mensaje/copy;
- acción disponible;
- acción deshabilitada;
- estados obligatorios;
- datos requeridos;
- permission refs;
- failure refs;
- verify visual.

Cubre al menos:

- loading;
- empty;
- error;
- permission denied;
- validation error;
- success;
- offline si móvil o PWA;
- stale data;
- disabled controls;
- confirmation dialogs;
- destructive action confirmation;
- role-based UI;
- estado después de refresh;
- estado tras volver atrás;
- deep links si aplica.

Cada pantalla productiva de `UX_CONTRACT.md` debe tener `UI-*` suficientes.

## 16. Observability / Audit Logic — `OBS-*`

`OBS-*` define qué debe quedar registrado para reconstruir qué ocurrió.

Cada `OBS-*` debe incluir:

- ID;
- evento;
- cuándo se emite;
- campos requeridos;
- campos prohibidos/sensibles;
- correlation ID;
- user/actor;
- entidad afectada;
- old/new value si aplica;
- retención;
- uso para soporte, seguridad, compliance o debugging;
- verify mínimo.

Cualquier `CORE-*`, acción irreversible, integración, cambio de estado crítico o permiso denegado sensible debe tener auditabilidad.

## 17. Evaluation Logic — `EVAL-*`

`EVAL-*` define cómo comprobar de forma reproducible que la lógica funciona.

Cada `EVAL-*` debe incluir:

- ID;
- objetivo;
- dataset/fixture;
- preparación;
- comando;
- métrica;
- resultado esperado;
- evidencia;
- cleanup;
- slices cubiertas;
- criterios de bloqueo.

Para lógica central `CORE-*`, siempre debe existir al menos un `EVAL-*` salvo que se justifique por qué no aplica.

Ejemplos de evaluación:

- fixture con resultado determinista;
- dataset pequeño proporcionado;
- golden case;
- test de error;
- test de idempotencia;
- test de estado prohibido;
- test de permisos;
- test de integración con stub controlado cuando externo real no esté disponible;
- test visual con datos reales/proporcionados;
- backtest/replay si aplica;
- comparación contra benchmark si aplica.

## 18. Cómo rellenar `instrucciones.md`

`instrucciones.md` es el contrato funcional de producto. Debe contener la verdad de negocio y producto.

Incluye con mucho detalle:

- visión del producto;
- alcance v1;
- no-alcance;
- actores y roles;
- módulos;
- glosario del dominio;
- assumptions;
- non-negotiables;
- Domain Logic `DR-*`;
- Application Logic `AL-*`;
- Core Logic `CORE-*`;
- Permission Logic `AUTH-*`;
- State Logic `STATE-*`;
- Failure Logic `ERR-*`;
- Data Logic `DATA-*`;
- Integration Logic `INT-*`;
- Observability `OBS-*`;
- Evaluation `EVAL-*`;
- acceptance global;
- verification principles.

Para cada contrato, crea tablas amplias y después desarrolla las entradas importantes con explicación narrativa. No pongas solo IDs.

## 19. Cómo rellenar `<APP>_TECHNICAL_GUIDE.md`

La guía técnica debe ser suficientemente concreta para que `planner`, `developer`, `validator` y `tester` no tengan que adivinar.

Incluye:

- stack real derivado del producto;
- library discovery;
- estructura de proyecto esperada;
- arquitectura;
- flujo de datos;
- mapping de `AL-*` y `CORE-*` a servicios/módulos;
- mapping de `DR-*` a validaciones;
- mapping de `AUTH-*` a guards/policies;
- mapping de `STATE-*` a entidades/state machines;
- mapping de `ERR-*` a handlers/recovery;
- mapping de `DATA-*` a modelos/tablas;
- mapping de `INT-*` a clientes/jobs/webhooks;
- mapping de `OBS-*` a logs/audit events;
- mapping de `EVAL-*` a tests/comandos;
- rutas/pantallas con endpoints consumidos;
- endpoints con request/response/auth/errors/consumer/tables/side effects/slice;
- modelos/tablas nuevos;
- navigation contract;
- verification data contract;
- comandos reales;
- constraints e invariants;
- ADRs cuando haya decisiones no triviales.

No escribas endpoints genéricos sin request/response. No escribas tablas sin campos. No escribas servicios sin responsabilidad clara.

## 20. Cómo rellenar `UX_CONTRACT.md`

`UX_CONTRACT.md` es la fuente única de UX.

Incluye:

- personas;
- journeys `J-*`;
- pantallas/rutas;
- navegación;
- screen logic `UI-*`;
- empty/loading/error/success states;
- permission-based UI;
- copy visible;
- confirmaciones;
- mobile-specific behavior si aplica;
- datos visuales requeridos;
- verificación visual;
- trazabilidad a slices;
- trazabilidad a endpoints;
- trazabilidad a `AL-*`, `CORE-*`, `DR-*`, `AUTH-*`, `STATE-*`, `ERR-*`.

Cada pantalla debe explicar qué se ve, qué puede hacer el usuario, qué pasa si no hay datos, qué pasa si hay error, qué pasa si no tiene permisos y cómo se verifica.

## 21. Cómo rellenar `STACK_PROFILE.yaml`

`STACK_PROFILE.yaml` es fuente única de stack. No escribas comandos, paths o frameworks por costumbre.

Incluye:

- frontend framework;
- backend framework;
- DB engine;
- package manager;
- test commands;
- dev commands;
- verification commands;
- docker/compose si aplica;
- runtime.port_defaults;
- runtime.port_env;
- design_tokens_enforcer;
- git_workflow;
- core_logic;
- logic_contracts;
- observability;
- verification;
- mobile/browser MCP si aplica.

No hardcodees `git push origin main` en documentos genéricos. `git_workflow` recomendado es `pr-flow` salvo caso explícito muy simple.

El valor público recomendado para tokens visuales es `design_tokens_v1`. Para stacks sin control visual todavía, usa `design_tokens_enforcer: none` de forma explícita.

## 22. Cómo rellenar `<APP>_IMPLEMENTATION_CHECKLIST.md`

El `Canonical Coverage Registry` es la fuente principal para el DAG. Debe ser completo, amplio y trazable.

Debe contener estas columnas exactamente:

| Slice ID | Tipo | Target | Step | Product increment | Build state | Risk level | Verify mode | Depends on | Conflict group | Write set | Journey refs | Pantalla/Ruta | Endpoint | Tablas DB | Origen-Instr | Origen-TechGuide | Acceptance mínimo | Verify mínimo | Domain rule refs | Architecture refs | Application logic refs | Core logic refs | Permission refs | State refs | Failure refs | Integration refs | UI refs | Data refs | Observability refs | Evaluation refs |

Reglas obligatorias:

- `Depends on` activa `explicit_dag`; no lo omitas.
- El resultado esperado de los checkers es `mode=explicit_dag`.
- `Risk level`: `low|medium|high|critical`.
- `Verify mode`: `auto` solo para low-risk que no cierran journey ni tocan lógica crítica.
- `human` para UI, auth, datos reales, journeys, integraciones, estado crítico y riesgo medio/alto.
- `Verify mínimo` debe contener comandos/evidencia reales.
- `Verify mínimo` no puede ser solo `auto` o `human`.
- `Conflict group` agrupa recursos lógicos compartidos.
- `Write set` declara patrones de ficheros esperados.
- `Journey refs` debe apuntar a IDs existentes en UX.
- Todas las columnas `* refs` deben apuntar a IDs declarados o quedar `—` con razón implícita por no aplicación.
- `Pantalla/Ruta`, `Endpoint` y `Tablas DB` no pueden contradecir la guía técnica.
- Cada fila debe tener acceptance y verify suficientes para cerrar una task en producción.

No hagas un registry corto. Una aplicación grande necesita muchas filas. Parte por pantalla, endpoint, servicio, lógica central, integration, migration, UI state, verify y hardening cuando corresponda.

## 23. Granularidad DAG

Diseña para paralelismo seguro, no para una lista secuencial enorme.

- Phase/lane: agrupa por milestone, pantalla/journey lane o módulo coherente.
- Step: agrupa tasks relacionadas por ownership, write set y verificación.
- No hay tope artificial de tasks.
- Si el producto necesita muchas tasks, decláralas todas.
- Cada task debe ser pequeña, verificable y con `Write set` concreto.
- Prefiere lanes por pantalla/journey, vertical slice o módulo técnico que alimente una pantalla nombrada.
- Evita mega-phases.
- Evita fan-in degenerado salvo integración final justificada.
- Evita ciclos.
- Un join se desbloquea solo cuando todos sus predecesores están `done`.
- Usa `Conflict group` y `Write set` para proteger router, theme, migrations, deps, state handlers, API clients, shared services y ficheros compartidos.

## 24. Journey, UX y contrato front -> back -> DB

Cada journey debe declarar:

- pantallas/rutas;
- acciones del usuario;
- endpoints;
- tablas;
- estado cliente/state handler;
- slices implicadas;
- verificación con datos reales/proporcionados;
- `AL-*`, `CORE-*`, `DR-*`, `AUTH-*`, `STATE-*`, `ERR-*`, `UI-*`, `DATA-*`, `OBS-*`, `EVAL-*` relevantes.

Cada pantalla productiva debe declarar:

- ruta/page;
- journey refs;
- endpoints consumidos;
- estado cliente/state handler;
- estados UI obligatorios;
- next action visible;
- permission behavior;
- error behavior;
- slice ID.

Cada endpoint productivo debe declarar:

- método/path;
- request;
- response;
- auth;
- errores;
- consumidor front/journey o justificación `internal/no-front`;
- tablas/side effects;
- audit events;
- slice ID.

Cada task productiva debe poder reconstruir esta cadena:

```text
Journey -> Pantalla/Ruta -> Endpoint -> Servicio/Core -> Tabla/Side effect -> Test/Verify
```

## 25. Library discovery

Antes de fijar slices, haz library discovery y arquitectura por áreas aplicables. Evalúa al menos seis áreas con criterio real entre estas, marcando `USAR`, `CUSTOM`, `NO APLICA` o `DEFERRED`:

- Frontend del stack declarado: forms y validación, iconografía, componentes UI extra, cache de imágenes, file pickers, chat/streaming AI, charts, animations, layouts responsive, codegen, deep links, date/time avanzado, maps, pagos, push, crash reporting, permissions nativos, almacenamiento offline.
- Backend: procesamiento de documentos/archivos proporcionados, procesamiento multimedia si aplica, HTTP a APIs externas, jobs/queues, email custom, scraping, validaciones específicas, extensiones cripto, observabilidad backend, storage no-proveedor declarado.
- BBDD: extensiones del motor DB declarado específicas como `pg_trgm`, `unaccent`, `pgcrypto`, `PostGIS`.
- AI/ML: structured outputs, constrained generation, prompt eval, reference retrieval metrics, token counting, loaders/chunkers específicos.
- Producto/operación: auditoría, métricas, billing, exportación de datos, permisos avanzados, administración, soporte.

Reglas:

- `<20 LOC` de código propio: `CUSTOM` gana.
- Una librería debe ahorrar al menos una slice o reducir riesgo material.
- Prioriza librerías con adopción real, mantenimiento reciente y documentación oficial suficiente.
- Para AI/ML, exige mantenimiento especialmente reciente y ejemplo compatible con el stack actual.
- Licencias MIT/BSD/Apache son preferentes. GPL/comercial requieren ADR.
- No infles dependencias. Si introduces una dependencia, justifica qué elimina o simplifica.
- No pinees versiones en `instrucciones.md`; el `official-docs-researcher` confirmará versión exacta en la slice de introducción.

Cada decisión `USAR` o `DEFERRED` debe aparecer también en el technical guide y tener una slice cuando se implemente.

## 26. Verification Data Contract y datos reales

Incluye en la guía técnica un contrato de datos de verificación.

Debe cubrir:

- flow/journey;
- persona/rol;
- datos reales/proporcionados requeridos;
- carga de datos permitida;
- seeds/fixtures;
- reset/cleanup;
- slices cubiertas;
- expected DB state;
- expected UI state;
- expected audit events;
- edge cases;
- comandos.

Regla de producción: no cierres verificación con lorem ipsum, mocks decorativos, payloads inventados no persistidos o inserts hechos por el mismo endpoint que se está probando.

Para edge cases (`empty`, `error_network`, `permission_denied`, payload inválido), usa datos reales/proporcionados o casos controlados explícitamente etiquetados. Si faltan datos, bloquea o registra follow-up, pero no inventes verificación falsa.

## 27. Auto-verify y verify humano

Puedes usar `Verify mode=auto` solo si se cumplen todas estas condiciones:

- `Risk level=low`;
- no cierra un journey;
- no toca auth;
- no toca pagos;
- no toca PII sensible;
- no toca permisos;
- no toca migraciones críticas;
- no toca datos destructivos;
- no toca core logic crítica;
- tiene comando determinista en `Verify mínimo`;
- produce handoff y evidence.

Usa `Verify mode=human` para:

- journeys;
- UX visible;
- auth;
- datos reales;
- integraciones críticas;
- core logic relevante;
- cambios de estado;
- errores/recovery;
- móvil;
- riesgo medio/alto.

## 28. Runtime esperado en Claude Code

Cada task se ejecuta aislada por terminal. El comando `/next-wave` imprimirá variables como:

```bash
export CLAUDE_ACTIVE_TASK_ID=<TASK_ID> CLAUDE_TASK_PACK=orchestrator-state/tasks/task-packs/<TASK_ID>.md
```

Los documentos que generes deben permitir que `claim_task.py` construya ese `CLAUDE_TASK_PACK` con:

- route;
- endpoint;
- tables;
- journey refs;
- domain refs;
- application logic refs;
- core logic refs;
- permission refs;
- state refs;
- failure refs;
- integration refs;
- UI refs;
- data refs;
- observability refs;
- evaluation refs;
- risk;
- verify mode;
- conflict groups;
- write set;
- comandos reales de verify.

## 29. Runtime logs, workers y comportamiento humano

Al rellenar `STACK_PROFILE.yaml`, incluye:

- `runtime.port_defaults`;
- `runtime.port_env`;
- `verification.docker.compose_file` si el compose real no está en raíz;
- comandos reales de hard reset;
- logs de Docker Compose;
- cleanup runtime;
- puertos por servicio;
- logs/cleanup de Rancher/Kubernetes/worker si existen.

El runtime de verify debe poder aislarse por slice con `docker compose -p <compose_project>`, evitar colisiones de puertos host con `CLAUDE_*_PORT`, reconstruirse desde el worktree activo y limpiarse al cerrar con:

```bash
scripts/cleanup-slice-runtime.sh --task <TASK_ID> --apply --strict
```

No uses prunes globales.

Toda slice productiva debe verificarse como lo haría un humano:

- botones reales;
- navegación real;
- estados UX;
- persistencia;
- reglas de dominio;
- permisos;
- errores;
- auditoría;
- datos reales/proporcionados.

Si hay PDFs/documentos/LLM, usa archivos reales/proporcionados y registra ruta/hash. No inventes datos ni extracción.

## 30. Flutter mobile verify-slice

Si `STACK_PROFILE.yaml` declara `frontend.framework: flutter` y `frontend.visual_check: simulator|emulator|device`, `/verify-slice` debe usar siempre el Dart/Flutter MCP real:

```text
MCP_CLIENT: dart
```

También son válidos nombres equivalentes si el proyecto los declara explícitamente: `flutter` o `flutter-driver`.

Para Flutter web sigue siendo válido:

```text
MCP_BROWSER: chrome-devtools|claude-in-chrome|agent360-browser-mcp|browser-mcp
```

No cierres una slice mobile con verificación solo web. Configuración MCP recomendada:

```bash
claude mcp add --transport stdio dart -- dart mcp-server
```

## 31. Revisión documental antes de entregar

Haz dos revisiones completas.

### Revisión A — Producto y lógica

Comprueba:

- todos los actores tienen permisos;
- todos los journeys tienen pantallas;
- todos los journeys apuntan a `AL-*`;
- cada `AL-*` tiene steps internos;
- cada `AL-*` referencia `DR-*`, `AUTH-*`, `STATE-*`, `ERR-*`, `DATA-*`, `OBS-*` cuando aplica;
- cada lógica central tiene `CORE-*`;
- cada `CORE-*` tiene inputs, outputs, parámetros, algoritmo/pasos y evaluación;
- cada regla `DR-*` es verificable;
- cada permiso `AUTH-*` tiene allow y deny;
- cada estado `STATE-*` tiene transiciones permitidas y prohibidas;
- cada error `ERR-*` tiene recovery;
- cada integración `INT-*` tiene idempotencia/retry/failure;
- cada pantalla tiene `UI-*`;
- cada dato persistente tiene `DATA-*`;
- cada acción crítica tiene `OBS-*`;
- cada lógica core tiene `EVAL-*`.

### Revisión B — Scheduler y ejecución

Comprueba:

- phases pequeñas pero completas;
- slices no gigantes;
- `Depends on` explícito;
- `Conflict group` real;
- `Write set` concreto;
- `Risk level` correcto;
- `Verify mode` correcto;
- `Verify mínimo` real;
- sin ciclos;
- sin fan-in degenerado innecesario;
- sin endpoints sin consumidor;
- sin pantallas sin ruta;
- sin tablas huérfanas;
- sin IDs duplicados;
- sin columnas omitidas;
- sin `NO APLICA` abusivo.

Después verifica mentalmente que estos comandos pasarían:

```bash
python3 -B -S .claude/bin/bootstrap_source_of_truth.py --validate-only
python3 -B -S .claude/bin/bootstrap_source_of_truth.py --refresh
./scripts/check-task-dag.sh --strict
./scripts/check-journey-matrix.sh --strict
./scripts/check-wiring-contract.sh --strict --require-new-template-columns
```

## 32. Errores prohibidos

No entregues documentos que tengan:

- `Coverage Registry` sin `Depends on`;
- `Coverage Registry` sin las columnas nuevas de lógica;
- journeys de una sola pantalla inflados como journey end-to-end;
- application logic que sea solo descripción de UI;
- core logic ausente cuando hay algoritmo, motor, ranking, scoring, pricing, matching o workflow central;
- domain rules no verificables;
- permisos sin deny;
- estados sin transiciones prohibidas;
- errores sin recovery;
- integraciones sin idempotencia;
- UI sin empty/loading/error/success cuando aplique;
- auditabilidad ausente en acciones críticas;
- evaluation ausente para core logic;
- endpoints sin consumidor o sin justificación `internal/no-front`;
- pantallas sin route/page o sin estado UI;
- tablas mencionadas en un doc y ausentes en los otros;
- `Verify mode=auto` en slices de riesgo medio/alto o que cierran journey;
- `Verify mínimo=auto` o `Verify mínimo=human` como si fuera comando;
- mega-phase con decenas de tasks si puede partirse por pantalla/lane;
- existing baseline copiada a una app nueva;
- referencias a docs pequeños o salida mínima;
- TODOs;
- placeholders sin reemplazar.

## 33. Nota worktree

En proyectos `pr-flow`, `./scripts/next-wave.sh` imprime un bloque que crea/entra en el worktree `dev/<TASK_ID>` antes de lanzar Claude Code. Usa el bloque exacto que imprime. No lances `/next-slice` desde `main` para una task de PR.

## 34. Criterio final

La salida es correcta solo si un mantenedor puede responder, para cualquier slice:

```text
¿Qué journey cubre?
¿Qué caso de uso interno implementa?
¿Qué lógica core toca?
¿Qué reglas de dominio protege?
¿Qué permisos exige?
¿Qué estados cambia?
¿Qué errores maneja?
¿Qué datos crea/modifica/borra?
¿Qué integración dispara?
¿Qué UI cambia?
¿Qué auditoría deja?
¿Cómo se verifica con datos reales/proporcionados?
¿Qué evidencia queda?
```

Si no puedes responder alguna de esas preguntas desde los documentos, vuelve a la Pasada 3 y corrige antes de entregar.
