# Golden Real App — UX Contract


## 0. UX architecture blueprint alignment

| A42 ref | UX implication | Screens/journeys affected | Visible proof | Verify evidence |
|---|---|---|---|---|
| A42-03 | El límite visible es la pantalla Home contra API local | Home / J01,J02 | route `/` y endpoint markers | verify_golden_app.py |
| A42-06 | Runtime crítico create/list/approve ocurre desde controles reales | Home / J01,J02 | Create real record, Refresh list | run-golden-e2e |
| A42-10 | La UX debe demostrar datos reales/proporcionados y validación | Home / J01,J02 | persisted item + DOMAIN_VALIDATION_FAILED | JSON result |

## Screen Inventory

| Screen | Route | Journey refs | Primary controls | Required states | UI refs | Evidence |
|---|---|---|---|---|---|---|
| Home | / | J01,J02 | Create real record, Refresh list | loading, empty, error_validation, success | UI-001,UI-002,UI-003 | HTML fetched by verify_golden_app.py |

## Journey-to-screen Matrix

| Journey | Screen | User actions | Endpoint/data | Expected result | Verify |
|---|---|---|---|---|---|
| J01 | Home | submit provided title/owner and refresh list | POST /api/v1/items, GET /api/v1/items | persisted item visible through product path | EVAL-001,EVAL-003 |
| J02 | Home | approve existing item | PATCH /api/v1/items/{id}, GET /api/v1/items/{id} | status approved persisted | EVAL-002 |

## UI Logic Contract

| UI ID | Screen | Condition | Behavior | User-facing/control evidence | Related refs |
|---|---|---|---|---|---|
| UI-001 | Home | page loaded | show form with Create real record button and provided-value fields | `Create real record` button present | J01,AL-001,CORE-001 |
| UI-002 | Home | user wants persisted data | show Refresh list control with `/api/v1/items` endpoint marker | `Refresh list` button present | J01,J02,AL-003,CORE-003 |
| UI-003 | Home/API path | validation or state transition occurs | surface success through persisted item or validation via real API response | DOMAIN_VALIDATION_FAILED for invalid create; approved status for valid patch | J01,J02,ERR-001,STATE-001 |

## Human Control Contract

All primary controls must be present and functional during verification. The verifier must exercise the visible control contract as a human operator would: load the page, identify the create control, identify the refresh control, submit provided data, observe persisted results, and confirm validation errors are visible or returned through the real product path.

## Required UX States

| State | Golden expectation |
|---|---|
| loading | API request is reachable and health endpoint is ready before interaction. |
| empty | Initial item list can be empty without crashing. |
| error_validation | Missing title/owner returns DOMAIN_VALIDATION_FAILED. |
| success | Created and approved item remains persisted in SQLite. |

## Accessibility And Evidence

The page must expose real controls with stable labels. Verification must record the real data fixture path, UI controls checked, domain rules verified, and clean runtime logs.
