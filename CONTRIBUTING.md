# Contribute to Ragwell agent tools

Use uv 0.12.17 and Python 3.11 or newer. The initial development interpreter is
3.12.14; CI qualifies the supported 3.11–3.14 range. The package consumes the
published Ragwell SDK and never requires backend source or a database.

```sh
uv sync --locked --python 3.12
uv run --locked --no-sync ruff format --check .
uv run --locked --no-sync ruff check .
uv run --locked --no-sync mypy
uv run --locked --no-sync pytest
uv run --locked --no-sync python scripts/check_documents.py
uv build --no-sources
uv run --locked --no-sync python scripts/qualify_artifact.py
```

Tests use synthetic responses, in-process MCP and real stdio subprocesses talking
to a loopback HTTP fixture. They make no model/provider requests. Installed-wheel
qualification runs outside the source checkout and reruns the same suite. The
`uv pip install` step needs the public package cache/index; ordinary test execution
needs no external network.

Live beta and real agent tests are opt-in and remain separate evidence. Read
[qualification](docs/project/qualification.md) before preparing their synthetic
projects and credentials. Never commit a credential or paste raw protocol output
from a customer session into an issue.

Changes to tool input/output schemas, evidence/citation behavior, error handling,
or SDK/protocol versions need corresponding meaningful tests and compatibility
notes. Guides and templates must agree with the exact qualified host surface.
Preserve a single canonical skill; do not create a separate retrieval implementation
for each host. Public releases and marketplace submission require a separate
release decision after the relevant gates pass.
