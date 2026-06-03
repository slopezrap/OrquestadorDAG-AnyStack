from __future__ import annotations

import sys
import unittest
from pathlib import Path

_BIN = Path(__file__).resolve().parent.parent
if str(_BIN) not in sys.path:
    sys.path.insert(0, str(_BIN))

import bootstrap_source_of_truth as boot  # noqa: E402


class DomainLogicContractTests(unittest.TestCase):
    def test_coverage_registry_parses_domain_rule_refs(self):
        checklist = """# APP Implementation Checklist

## Canonical Coverage Registry

| Slice ID | Tipo | Target | Step | Product increment | Build state | Risk level | Verify mode | Depends on | Conflict group | Write set | Journey refs | Pantalla/Ruta | Endpoint | Tablas DB | Origen-Instr | Origen-TechGuide | Acceptance mínimo | Verify mínimo | Domain rule refs | Architecture refs | Application logic refs | Core logic refs | Permission refs | State refs | Failure refs | Integration refs | UI refs | Data refs | Observability refs | Evaluation refs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P01-S01-T001 | api | create order | Step 1.1 | v1 | planned | medium | human | — | api:orders | api/orders/** | J101 | /orders/new | POST /api/orders | orders | §3#orders | §6#orders | creates order | pytest orders | DR-001, DR-002 | A42-04,A42-05 | AL-001 | CORE-001 | AUTH-001 | STATE-001 | ERR-001 | INT-001 | UI-001 | DATA-001 | OBS-001 | EVAL-001 |
"""
        tasks = boot.parse_coverage_registry(checklist)
        self.assertEqual(tasks[0]["domain_rule_refs"], ["DR-001", "DR-002"])
        self.assertEqual(tasks[0]["domain_rule_refs_raw"], "DR-001, DR-002")
        self.assertEqual(tasks[0]["architecture_refs"], ["A42-04", "A42-05"])
        self.assertEqual(tasks[0]["application_logic_refs"], ["AL-001"])
        self.assertEqual(tasks[0]["core_logic_refs"], ["CORE-001"])
        self.assertEqual(tasks[0]["permission_refs"], ["AUTH-001"])
        self.assertEqual(tasks[0]["state_refs"], ["STATE-001"])
        self.assertEqual(tasks[0]["failure_refs"], ["ERR-001"])


if __name__ == "__main__":
    unittest.main()
