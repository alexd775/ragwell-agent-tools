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

Live deployed-API and real agent tests are opt-in; use the
[compatibility summary](docs/compatibility.md) for the recorded scope and
`scripts/qualify_endpoint.py --help` for synthetic fixture configuration. Never
commit a credential or paste raw customer protocol output into an issue. Internal
planning and detailed QA records belong only in the ignored root `private/`
directory; no private files are needed to build, test or contribute.

For an explicitly selected pre-publication SDK contract change, the installed
qualifier accepts `--sdk-wheel /absolute/path/to/ragwell-candidate.whl` alongside
the tools `--wheel`. This installs both built candidates into the clean test
environment. It does not establish public dependency availability; repin the
normal development lock after the compatible SDK is published, before release.

The independent CI security job and release workflow require Docker and Python
3.11 or later (the local `.venv` interpreter is selected when present), and run
`bash scripts/source-security.sh` against committed HEAD. Docker downloads public
advisory data without a source mount, then scans the public archive without
network access. The gate covers redacted secrets, dependency vulnerabilities and
licenses; it also records a CycloneDX SBOM and source commit in ignored
`.security-reports/`. Run the complete gate on the final commit before pushing.
The scan aliases every pinned runtime/development lock package into a scan-only
requirements inventory, since Trivy's development-dependency flag does not cover
Python locks. The release build also records actual
installed runtime/development license declarations through
`scripts/license_inventory.py`, retaining any missing declarations explicitly;
lockfiles alone do not contain every dependency's license metadata.

Package publication uses `.github/workflows/release.yml` with GitHub environment
`pypi` and PyPI Trusted Publishing for owner `alexd775`, repository
`ragwell-agent-tools`, workflow `release.yml`, project `ragwell-agent-tools`.
For the first publication, the account owner configures a
[pending Trusted Publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).
No repository API token is required. A `v` tag matching the package version on
`main` publishes the exact distributions after the independent security and
build/clean-install jobs succeed. A manual workflow dispatch builds and checks
the selected ref; publication still requires a tag ref. Release artifacts retain
the source commit and distribution hashes separately from uploadable packages.

Archive checks reject private material in both the wheel and source distribution.
If `dist/` contains older artifacts, pass the exact `--wheel` and `--sdist` paths
to `scripts/check_public_artifacts.py`, and `--wheel` to the installed qualifier.

Starter-pack Markdown uses canonical LF line endings inside the ZIP, including
when Git checks out CRLF on Windows. The drift check still rejects content edits.

Changes to tool input/output schemas, evidence/citation behavior, error handling,
or SDK/protocol versions need corresponding meaningful tests and compatibility
notes. Guides and templates must agree with the exact qualified host surface.
Preserve a single canonical skill; do not create a separate retrieval implementation
for each host. Public releases and marketplace submission require a separate
release decision after the relevant gates pass.
