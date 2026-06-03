from __future__ import annotations

from pathlib import Path


def _write_three_docs(root: Path, endpoint_consumer: str = "ContractUploadPage / J101") -> None:
    sot = root / "docs" / "source-of-truth"
    sot.mkdir(parents=True, exist_ok=True)
    (sot / "instrucciones.md").write_text(
        """# Instrucciones

## Domain Logic Contract

| Rule ID | Regla | Tipo | Aplica a | Fuente/razón | Error esperado | Verificación |
|---|---|---|---|---|---|---|
| DR-001 | Solo contratos con archivo válido pueden analizarse | invariant | POST /api/v1/contracts/upload | upload real | 400 DOMAIN_VALIDATION_FAILED | API + verify-slice |
| DR-002 | El usuario solo puede ver sus contratos | authorization | ContractUploadPage / contracts | seguridad | 403 DOMAIN_FORBIDDEN | fixture sandbox |

## Application Logic Contract

| AL ID | Caso de uso | Trigger | Actor | Preconditions | Pasos internos | Outputs | Refs |
|---|---|---|---|---|---|---|---|
| AL-001 | Ejecutar flujo principal | acción del usuario | usuario autorizado | datos válidos | validar; aplicar DR; persistir/leer; responder | resultado consistente | DR-001, CORE-001, AUTH-001, STATE-001, ERR-001 |

## Core Logic Contract

| Core ID | Nombre | Propósito | Inputs | Parámetros | Algoritmo / pasos | Outputs | Verificación mínima |
|---|---|---|---|---|---|---|---|
| CORE-001 | Lógica central del recurso | normalizar y validar el dato central | payload + estado | reglas declaradas | normalizar; validar; emitir DTO | DTO válido | fixture determinista |

## Permission Logic Contract

| Auth ID | Actor | Resource | Action | Allowed when | Denied when | Error |
|---|---|---|---|---|---|---|
| AUTH-001 | usuario | recurso principal | read/write | sesión válida y ownership correcto | sesión ausente u owner incorrecto | 401/403 |

## State Logic Contract

| State ID | Entity / process | Estados válidos | Transiciones válidas | Transiciones prohibidas | Verificación |
|---|---|---|---|---|---|
| STATE-001 | recurso principal | draft, active, archived | draft->active, active->archived | archived->draft | fixture de transición |

## Failure Logic Contract

| Error ID | Scenario | Expected behavior | User message | State change | Retry? | Applies to |
|---|---|---|---|---|---|---|
| ERR-001 | datos inválidos o no permitidos | rechazar sin filtrar datos | No disponible | none | no | AL-001 |

## Data and Observability Logic

| ID | Tipo | Qué queda definido | Evidencia | Applies to |
|---|---|---|---|---|
| DATA-001 | data lifecycle | creación/lectura del recurso principal | fila o DTO persistido | AL-001 |
| OBS-001 | audit/trace | evento con actor/request id | log/audit event | AL-001 |
| EVAL-001 | evaluation | resultado determinista esperado | test fixture | CORE-001 |

## 3.7 Journey Coverage Matrix

| ID | Milestone | Pantallas | Acciones | Endpoints | Tablas DB | Estado cliente | Slices | Verificación |
|----|-----------|-----------|----------|-----------|-----------|----------------|--------|--------------|
| J101 | M1 | ContractUploadPage → AnalysisResultsPage | upload, see analysis | `POST /api/v1/contracts/upload` | `contracts` | ContractUploadProvider | `P02-S02-T001`, `P03-S01-T001` | `/verify-journey J101` |
""",
        encoding="utf-8",
    )
    (sot / "APP_TECHNICAL_GUIDE.md").write_text(
        f"""# Technical Guide

## 6. Interfaces

### 6.1 Rutas Flutter nuevas

| Ruta | Page | Auth | Journey refs | Endpoints consumidos | Estado cliente/provider | Estados UI obligatorios | Next action | Slice ID | Descripción |
|------|------|------|--------------|----------------------|-------------------------|------------------------|-------------|----------|-------------|
| /contracts/upload | ContractUploadPage | Sí | J101 | POST /api/v1/contracts/upload | ContractUploadProvider | loading, error_network, success | /contracts/1/analysis | P03-S01-T001 | Upload |

### 6.2 Endpoints API nuevos

| Method | Path | Request | Response | Auth | Errors | Consumidor front/journey | Tablas/side effects | Slice ID |
|--------|------|---------|----------|------|--------|--------------------------|---------------------|----------|
| POST | /api/v1/contracts/upload | multipart file | {{data: {{contract_id}}}} | Sí | 400, 401 | {endpoint_consumer} | contracts | P02-S02-T001 | DR-001,DR-002 |

### 6.3 Domain Rules Implementation Matrix

| Rule ID | Enforced in | Endpoint | DB constraint | Service/use case | Front UX | Test/fixture | Slice ID |
|---|---|---|---|---|---|---|---|
| DR-001 | backend + frontend | POST /api/v1/contracts/upload | file required | UploadContractUseCase | error_validation | contract PDF fixture | P02-S02-T001 |
| DR-002 | backend + db | POST /api/v1/contracts/upload | owner_id required | ContractOwnershipPolicy | permission_denied | other-user fixture | P03-S01-T001 |

### 6.5 Verification Data Contract

| Flow/Journey | Persona/Rol | Datos reales/proporcionados requeridos | Carga de datos reales/proporcionados permitida | Reset/Cleanup | Slices/Journeys |
|---|---|---|---|---|---|
| J101 | usuario QA contrato | usuario confirmado + PDF de contrato sandbox con cláusulas realistas | load_provided_contract_upload_data.sql | reset_hard + truncate contracts | P02-S02-T001, P03-S01-T001 / J101 |

## 10. Persistencia

### 10.3 Schema

contracts table
""",
        encoding="utf-8",
    )
    (sot / "APP_IMPLEMENTATION_CHECKLIST.md").write_text(
        """# Phase 0 — Bootstrap

## Canonical Coverage Registry

| Slice ID | Tipo | Target | Step | Product increment | Build state | Risk level | Verify mode | Depends on | Conflict group | Write set | Journey refs | Pantalla/Ruta | Endpoint | Tablas DB | Origen-Instr | Origen-TechGuide | Acceptance mínimo | Verify mínimo | Domain rule refs | Architecture refs | Application logic refs | Core logic refs | Permission refs | State refs | Failure refs | Integration refs | UI refs | Data refs | Observability refs | Evaluation refs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P02-S02-T001 | api | upload endpoint | Step 2.2 | v1 | planned | medium | human | — | api:contracts | api/src/**/contracts*.py; api/tests/**/contracts* | J101 | ContractUploadPage /contracts/upload | POST /api/v1/contracts/upload | contracts | §3.1 | §6.2 | endpoint works | curl | DR-001,DR-002 | AL-001 | CORE-001 | AUTH-001 | STATE-001 | ERR-001 | INT-001 | UI-001 | DATA-001 | OBS-001 | EVAL-001 |
| P03-S01-T001 | flutter | ContractUploadPage | Step 3.1 | v1 | planned | medium | human | P02-S02-T001 | front:contracts | app/lib/**/contracts*.dart; app/test/**/contracts* | J101 | ContractUploadPage /contracts/upload | POST /api/v1/contracts/upload | — | §3.2 | §6.1 | page works | flutter test | DR-001,DR-002 | AL-001 | CORE-001 | AUTH-001 | STATE-001 | ERR-001 | — | UI-001 | — | OBS-001 | EVAL-001 |

## Step 2.2 — API
- [ ] upload endpoint
""",
        encoding="utf-8",
    )


def test_wiring_contract_accepts_filled_new_template(tmp_project):
    import check_wiring_contract

    _write_three_docs(tmp_project)
    result = check_wiring_contract.validate(tmp_project, require_new_template_columns=True)

    assert result["ok"], result
    assert result["counts"]["routes"] == 1
    assert result["counts"]["endpoints"] == 1
    assert result["counts"]["registry_rows"] == 2
    assert result["counts"]["journeys"] == 1
    assert result["counts"]["verification_data_contract"] == 1


def test_wiring_contract_requires_endpoint_consumer_when_requested(tmp_project):
    import check_wiring_contract

    _write_three_docs(tmp_project, endpoint_consumer="")
    result = check_wiring_contract.validate(tmp_project, require_new_template_columns=True)

    assert not result["ok"]
    assert any("missing Consumidor front/journey" in err for err in result["errors"])


def test_wiring_contract_requires_verification_data_contract_for_new_templates(tmp_project):
    import check_wiring_contract

    _write_three_docs(tmp_project)
    guide = tmp_project / "docs" / "source-of-truth" / "APP_TECHNICAL_GUIDE.md"
    text = guide.read_text(encoding="utf-8")
    start = text.index("### 6.5 Verification Data Contract")
    end = text.index("## 10. Persistencia")
    guide.write_text(text[:start] + text[end:], encoding="utf-8")

    result = check_wiring_contract.validate(tmp_project, require_new_template_columns=True)

    assert not result["ok"]
    assert any("Verification Data Contract" in err for err in result["errors"])


def test_wiring_contract_rejects_unknown_domain_rule_ref(tmp_project):
    import check_wiring_contract

    _write_three_docs(tmp_project)
    checklist = tmp_project / "docs" / "source-of-truth" / "APP_IMPLEMENTATION_CHECKLIST.md"
    checklist.write_text(checklist.read_text(encoding="utf-8").replace("DR-002", "DR-999"), encoding="utf-8")

    result = check_wiring_contract.validate(tmp_project, require_new_template_columns=True)

    assert not result["ok"]
    assert any("unknown Domain rule ref DR-999" in err for err in result["errors"])
