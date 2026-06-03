# UX_CONTRACT — {{APP_NAME}}

## Screen/Journey Lane Redactor Contract

- No modeles la app como `backend/API primero`, luego `frontend`, y `UX polish` al final. Esa separación rompe la pantalla aunque los tests pasen.
- Cada pantalla importante debe nacer de una **screen/journey lane**: contrato de pantalla + contrato API/datos + implementación conectada + estados UX obligatorios + verificación del journey.
- Las slices de API/backend pueden existir separadas sólo si son foundation real o contrato técnico que alimenta una pantalla/journey nombrado en `Journey refs`.
- Criterio de cierre de pantalla: datos reales/proporcionados conectados front -> back -> DB, estados `loading`, `empty`, `error_network`, `error_validation`, `permission_denied` cuando aplique, `success`, navegación/next action, responsive básico y accesibilidad básica.
- Granularidad: crea tantas slices como hagan falta para cerrar cada pantalla/journey lane verificable de punta a punta. No hagas una slice por botón/componente pequeño; tampoco cierres una pantalla sólo porque compila.
- Defectos dentro de la pantalla actual van por `validator/tester -> debugger -> retest`. Sólo crea FU si falta trabajo nuevo fuera de scope: pantalla, endpoint, tabla, journey, contrato de datos reales o decisión humana no declarada.

> Perfil large-with-base: app grande sobre base existente; este contrato debe distinguir pantallas existentes, pantallas modificadas y pantallas nuevas sin romper el baseline.
> Este documento no sustituye a `instrucciones.md` ni al `TECHNICAL_GUIDE`: conecta la experiencia visible con `J-*`, `AL-*`, `CORE-*`, `DR-*`, `AUTH-*`, `STATE-*`, `ERR-*`, `INT-*`, `DATA-*`, `OBS-*` y `EVAL-*`.

---


## 0. UX architecture blueprint alignment (`A42-*`)

El UX también debe respetar el blueprint arc42: contexto de uso, restricciones, escenarios runtime, quality scenarios y riesgos. No basta con que la pantalla sea bonita; debe demostrar las decisiones arquitectónicas visibles.

| A42 ref | UX implication | Screens/journeys affected | Visible proof | Verify evidence |
|---|---|---|---|---|
| A42-03 | límites del sistema y sistemas externos visibles | {{screens_or_journeys}} | {{external_boundary_copy_or_state}} | {{evidence}} |
| A42-06 | runtime scenario crítico que el usuario dispara o observa | {{screens_or_journeys}} | {{runtime_visible_state}} | {{evidence}} |
| A42-08 | concepto transversal visible: auth, error handling, i18n, accessibility, audit notice | {{screens_or_journeys}} | {{visible_behavior}} | {{evidence}} |
| A42-10 | quality scenario visible: rendimiento, usabilidad, accesibilidad, resiliencia | {{screens_or_journeys}} | {{measurable_ui_outcome}} | {{evidence}} |
| A42-11 | riesgo/deuda que afecta UX o verificación | {{screens_or_journeys}} | {{mitigation_or_disclaimer}} | {{evidence}} |

Cada pantalla que cierre un escenario `A42-*` debe tener la misma referencia en el Coverage Registry (`Architecture refs`) y en su verify mínimo.

## 1. UX purpose

Describe la experiencia del producto en lenguaje de usuario y negocio. No describas sólo componentes: explica qué logra el usuario, qué información necesita, qué decisiones toma y qué evidencia visible confirma que el sistema funcionó.

| Item | Definición |
|---|---|
| Primary product promise | {{primary_product_promise}} |
| Main user outcome | {{main_user_outcome}} |
| Critical visible proof | {{what_user_must_see_to_trust_result}} |
| Real/provided data dependency | {{real_or_provided_data_needed_for_visual_verification}} |
| Surfaces | web / mobile / admin / public / embedded / none según `STACK_PROFILE.yaml` |

---

## 2. Personas, roles and permissions in UX

| Persona | Role/Auth refs | Goal | Critical journeys | Data required | Permission-sensitive UI |
|---|---|---|---|---|---|
| {{persona}} | AUTH-001 | {{goal}} | J-001, J-002 | DATA-001 | {{hidden_or_disabled_actions}} |

Checklist de permisos visibles:

- [ ] Cada acción primaria visible tiene `AUTH-*` asociado.
- [ ] Cada pantalla privada define estado `permission_denied`.
- [ ] La UI no filtra datos de otros usuarios/tenants aunque el backend bloquee.
- [ ] Si una acción requiere aprobación humana, doble confirmación o aceptación de riesgo, queda visible aquí y en `AL-*`/`STATE-*`.

---

## 3. Information architecture and navigation map

Describe la navegación antes de entrar en pantallas sueltas. Para apps móviles, incluye tabs, stacks, deep links y back behavior. Para web, incluye rutas, breadcrumbs, sidebars y estados de sesión.

| Area | Route/root | Contains screens | Entry points | Exit/next actions | Related journeys |
|---|---|---|---|---|---|
| {{area_name}} | {{/route}} | {{ScreenA, ScreenB}} | {{nav/sidebar/deeplink}} | {{next_action}} | J-001 |

### 3.1 Navigation rules

| NAV ID | Condition | User location | Expected navigation | Forbidden navigation | Related refs |
|---|---|---|---|---|---|
| NAV-001 | usuario autenticado | {{/route}} | puede avanzar a {{/next}} | no puede abrir recursos ajenos | J-001, AUTH-001 |
| NAV-002 | sesión expirada | cualquier privada | redirige a login/reauth preservando intención segura | no muestra datos privados | AUTH-001, ERR-001 |

---

## 4. Journey-to-screen matrix

Cada `J-*` debe tener pantallas, datos, endpoints, estados y verificación visual. No dejes journeys sólo narrativos.

| Journey ID | User goal | Screens in order | Primary actions | API/data touched | UI states required | Success proof | Verify evidence |
|---|---|---|---|---|---|---|---|
| J-001 | {{goal}} | {{/start}} -> {{/detail}} | {{action_1}}, {{action_2}} | Endpoint + DATA refs | loading, empty, error_network, error_validation, permission_denied, success | {{visible_result}} | screenshot/video/logs/DB row |

Rules:

- [ ] Un journey debe tener al menos una pantalla real; si es headless/API-only, explica por qué y cómo se verifica.
- [ ] Un journey que modifica datos debe mostrar estado final visible y evidencia persistida.
- [ ] Un journey que usa `CORE-*` debe mostrar o registrar salida, explicación, versión/parámetros o evidencia suficiente para auditarlo.
- [ ] Si faltan datos reales/proporcionados para ejecutar el journey, no inventes datos: declara `DATA-*`, seed/import y bloqueo de verificación.

---

## 5. Screen inventory

| Route | Screen/Page | Surface | Primary journey refs | AL refs | CORE refs | Required UI states | Real data contract | Verify method |
|---|---|---|---|---|---|---|---|---|
| {{/route}} | {{PageName}} | web/mobile/admin | J-001 | AL-001 | CORE-001 / — | loading, empty, error_network, error_validation, permission_denied, success | DATA-001 rows / external files / account | browser/mobile MCP + DB/log evidence |

For each screen, ChatGPT must fill a subsection using this shape:

### 5.x {{Screen/Page name}} — {{/route}}

- **Purpose:** {{why_this_screen_exists}}
- **Primary user:** {{persona}}
- **Entry points:** {{nav/deeplink/redirect}}
- **Exit/next actions:** {{next_action_after_success}}
- **Journeys:** J-...
- **Application logic:** AL-...
- **Core logic:** CORE-... or `—`
- **Domain rules:** DR-...
- **Permissions:** AUTH-...
- **State:** STATE-...
- **Failures:** ERR-...
- **Data:** DATA-...
- **Integrations:** INT-... or `—`
- **Observability:** OBS-...
- **Evaluation:** EVAL-... if CORE-* is involved
- **Visual verification:** exact MCP/browser/mobile action and expected evidence.

---

## 6. UI Logic Contract

`UI-*` no sustituye a `J-*`. El Journey describe el recorrido; `UI-*` describe cómo responde cada pantalla ante condiciones concretas.

| UI ID | Route/Screen | Condition | Behavior | Message/copy | User action available | Related refs |
|---|---|---|---|---|---|---|
| UI-001 | {{/route}} / {{PageName}} | first load | show skeleton/loading with accessible label | {{loading_copy}} | none or cancel | J-001, AL-001 |
| UI-002 | {{/route}} / {{PageName}} | no persisted rows | show empty state with next action | {{empty_copy}} | create/import/request data | J-001, DATA-001 |
| UI-003 | {{/route}} / {{PageName}} | validation error | show inline field errors and preserve safe input | {{validation_copy}} | fix and retry | ERR-001, DR-001 |
| UI-004 | {{/route}} / {{PageName}} | permission denied | hide private data and explain access state | {{permission_copy}} | request access / switch account | AUTH-001, ERR-002 |
| UI-005 | {{/route}} / {{PageName}} | success | show persisted result and next action | {{success_copy}} | continue/download/share/review | STATE-001, OBS-001 |

Minimum UI states per user-visible screen:

- `loading`: visible while data/action is pending.
- `empty`: visible when no data exists, with a safe next action.
- `error_network`: visible when transport/integration fails.
- `error_validation`: visible when user input violates `DR-*` or schema.
- `permission_denied`: visible when `AUTH-*` denies access.
- `success`: visible when the intended state/data has changed.

---

## 7. Forms, validation and copy contract

| Form ID | Route/Screen | Fields | Validation refs | Submit action | Success behavior | Failure behavior |
|---|---|---|---|---|---|---|
| FORM-001 | {{/route}} | {{field_list}} | DR-001, ERR-001 | AL-001 endpoint/action | show UI-005 | show UI-003/UI-004 |

For every form:

- [ ] Required fields have label, help text, validation and error copy.
- [ ] Dangerous or irreversible actions have confirmation when applicable.
- [ ] Submit is disabled only for deterministic reasons the user can understand.
- [ ] After success, the screen shows the persisted result, not just a toast.
- [ ] Retry behavior is defined for network/integration errors.

---

## 8. Data visibility and real/provided data contract

| Data view ID | Screen | Data refs | Source | Must be real/provided? | Empty state | Stale/degraded state | Evidence |
|---|---|---|---|---|---|---|---|
| DATA-VIEW-001 | {{PageName}} | DATA-001 | DB/API/external/import | yes | UI-002 | UI-006 / ERR-003 | screenshot + DB row/log |

Rules:

- Do not use fake decorative data to close a slice.
- If synthetic data is acceptable for a non-sensitive fixture, mark it explicitly and explain why.
- If the product relies on documents/files/accounts/external data, describe the provided-data import or manual setup path.
- Every visible table/list/card must say which endpoint/data contract feeds it.

---

## 9. Screen-to-endpoint/data/state matrix

| Screen | Reads | Writes | Endpoints/actions | DB/data refs | State refs | Error refs | Observability refs |
|---|---|---|---|---|---|---|---|
| {{PageName}} | DATA-001 | DATA-001 | GET/POST {{/api/path}} | DATA-001 | STATE-001 | ERR-001, ERR-002 | OBS-001 |

This matrix must reconcile with `TECHNICAL_GUIDE §6.1/§6.2/§10.3` and with the Coverage Registry.

---

## 10. Interaction model

For each route, specify:

- Primary action.
- Secondary actions.
- Disabled states.
- Confirmation dialogs.
- Optimistic updates, if any.
- Rollback behavior, if any.
- Next action after success.
- Browser/mobile back behavior.
- Deep link behavior.
- Refresh/reload behavior.
- Offline/degraded behavior when applicable.

| Interaction ID | Screen | Trigger | Immediate UI response | Backend/data effect | Final UI state | Related refs |
|---|---|---|---|---|---|---|
| IX-001 | {{PageName}} | click/tap submit | loading + disable duplicate submit | AL-001 | success/validation error | UI-001, UI-003, UI-005 |

---

## 11. Visual design and component inventory

Do not prescribe brand-specific visuals unless the product request provides them. Define reusable components and their states.

| Component | Used on screens | Props/data | States | Accessibility notes | Related refs |
|---|---|---|---|---|---|
| {{ComponentName}} | {{PageName}} | {{props}} | default/loading/error/disabled/success | label/focus/contrast | UI-001 |

Required component-level thinking:

- [ ] Tables/lists have empty, loading and error rows.
- [ ] Cards show timestamps/source when data freshness matters.
- [ ] Status badges map to `STATE-*` exactly.
- [ ] Buttons map to `AL-*` or navigation, never ambiguous side effects.
- [ ] Sensitive data is masked or hidden according to `AUTH-*`.

---

## 12. Mobile/responsive/platform behavior

| Surface | Layout rules | Navigation model | Input model | Visual verification | Platform-specific risks |
|---|---|---|---|---|---|
| web | {{breakpoints}} | browser routes | keyboard/mouse/touch | browser MCP | responsive overflow |
| mobile | {{mobile_layout}} | tabs/stack/deeplink | touch/keyboard | simulator/emulator/device MCP | gestures, permissions, offline |
| admin | {{admin_layout}} | sidebar/table/detail | keyboard-heavy | browser MCP | dense data, permission leakage |

If a surface does not apply, mark it `not_applicable:<reason>` instead of leaving blank.

---

## 13. Accessibility and inclusive UX minimum

| Area | Requirement | Verification |
|---|---|---|
| Keyboard/focus | all primary actions reachable and focus visible | manual/browser check |
| Labels | inputs/buttons have accessible names | automated/manual check |
| Errors | validation errors announced and visible near fields | manual check |
| Contrast/tokens | design token enforcer or visual review | token check |
| Motion/loading | loading does not trap user indefinitely | verify loading/error paths |
| Responsive | no horizontal overflow on target widths | browser/mobile check |

---

## 14. Verification rules

State which flows require real/provided persisted data. If data is missing, record that the user/team must provide it before verification; do not invent unprovided data loads.

| Verify ID | Journey/screen | Data required | Tooling | Evidence expected | Blocking condition |
|---|---|---|---|---|---|
| UXVERIFY-001 | J-001 / {{PageName}} | DATA-001 | browser/mobile MCP + logs + DB check | screenshot/video + row/log refs | missing real/provided data |

Minimum verification evidence for visible slices:

- [ ] Route/screen loaded through real app runtime.
- [ ] Real/provided data shown or explicit blocked state if missing.
- [ ] Primary action executed.
- [ ] Backend/API/log/DB evidence checked when the screen writes data.
- [ ] All mandatory UI states either exercised or justified as `not_applicable:<reason>`.
- [ ] No console/runtime/log errors relevant to the slice.

---

## 15. UX final self-review before delivery

Before delivering the filled `UX_CONTRACT.md`, ChatGPT must perform this review and fix the document in-place:

- [ ] Every `J-*` has screens in the Journey-to-screen matrix.
- [ ] Every user-visible screen has `UI-*` entries for loading, empty, network error, validation error, permission denied and success, or a justified `not_applicable:<reason>`.
- [ ] Every primary action maps to `AL-*` and to an endpoint/action in the Technical Guide.
- [ ] Every visible specialized/core result maps to `CORE-*` and `EVAL-*` when applicable.
- [ ] Every permission-sensitive element maps to `AUTH-*`.
- [ ] Every state badge/status maps to `STATE-*`.
- [ ] Every error copy maps to `ERR-*`.
- [ ] Every list/table/card maps to `DATA-*`.
- [ ] Every external status/action maps to `INT-*` when applicable.
- [ ] Every sensitive or core action maps to `OBS-*`.
- [ ] Every route in this document appears in `TECHNICAL_GUIDE §6.1` and in at least one slice of the Coverage Registry.
- [ ] No screen closes with fake/decorative data.
- [ ] No placeholder like `{{...}}`, `TBD`, `pendiente`, `rellenar`, `etc.` remains in the filled document unless it is an explicit source-of-truth decision with owner.
