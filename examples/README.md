# Examples

`examples/` contains framework fixtures, not product templates that users must fill.

## Golden contract fixture

`golden-real-app/` is the checked-in reference implementation of the Orquestador AnyStack golden contract. It uses Python stdlib + SQLite so CI can run it without npm, Flutter, Docker, databases or cloud credentials.

Esta golden app no fija el stack de los productos reales y no cambia el contrato de entrada: ChatGPT sigue produciendo exactamente cinco documentos source-of-truth para cada producto.

That implementation choice is intentionally boring; the contract is stack-agnostic. A Flutter frontend with a Python API, React + Node, SwiftUI + Go, or any other stack is valid when its five source-of-truth documents and `STACK_PROFILE.yaml` can prove the same invariants:

```text
real/provided input data
real UI controls or product actions
real persistence / side effects
Domain rule refs verified with DR-* evidence
runtime logs scanned and clean
no stubs, invented fixtures or fake document/LLM extraction
```

Run the fixture with:

```bash
./scripts/run-golden-e2e.sh --json
```
