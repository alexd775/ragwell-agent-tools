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
uv run --locked --no-sync python scripts/build_sample_pack.py --check
uv build --no-sources
uv run --locked --no-sync python scripts/check_public_artifacts.py
uv run --locked --no-sync python scripts/qualify_artifact.py
```

Tests use synthetic responses, in-process MCP and real stdio subprocesses talking
to a loopback HTTP fixture. They make no model/provider requests. Installed-wheel
qualification runs outside the source checkout and reruns the same suite. The
`uv pip install` step needs the public package cache/index; ordinary test execution
needs no external network.

Live beta and real agent tests are opt-in; use the
[compatibility summary](docs/compatibility.md) for the recorded scope and
`scripts/qualify_endpoint.py --help` for synthetic fixture configuration. Never
commit a credential or paste raw customer protocol output into an issue. Internal
planning and detailed QA records belong only in the ignored root `private/`
directory; no private files are needed to build, test or contribute.

Archive checks reject private material in both the wheel and source distribution.
If `dist/` contains older artifacts, pass the exact `--wheel` and `--sdist` paths
to `scripts/check_public_artifacts.py`, and `--wheel` to the installed qualifier.

Changes to tool input/output schemas, evidence/citation behavior, error handling,
or SDK/protocol versions need corresponding meaningful tests and compatibility
notes. Guides and templates must agree with the exact qualified host surface.
Preserve a single canonical skill; do not create a separate retrieval implementation
for each host. Public releases and marketplace submission require a separate
release decision after the relevant gates pass.
