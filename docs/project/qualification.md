# Local pilot qualification

Date: 2026-10-02. The local pilot candidate is implemented and locally qualified.
No live beta or model-driven host task is certified by this document; the first
delivery outcome remains active until those gates pass.

## Verified local results

- uv 0.12.17 locked install; Ragwell SDK 0.2.0, MCP/mcp-types 2.2.0.
- Formatting, lint and strict type checking passed. The canonical skill passed
  the bundled skill validator; guide links and host-template syntax passed.
- **74 tests passed** in the development environment on Python 3.12.14/macOS arm64.
  Coverage includes strict input and scope-override rejection, preserved multipart
  coordinates, Unicode/full-result output bounds, API-error redaction, no search
  replay, quota/rate/credential fixture failures, local budgets, busy/cancellation/
  deadline behavior, protocol schemas, subprocess shutdown, live-qualifier
  preflight guards, tolerance of fields added by later SDK releases, and
  value-free opt-in diagnostics. The source credential is omitted from settings
  representations.
- Wheel and source distribution built independently. Clean wheel installation
  outside the checkout passed **74 tests per interpreter** on Python 3.11.16,
  3.12.14, 3.13.11 and 3.14.0, all on macOS arm64. The console entry point and
  installed import origin were verified. There is no backend/SDK source dependency.
- Both stdio connection modes are tested: legacy handshake `2025-11-25` and modern
  automatic discovery `2026-07-28`. The **11-case** stdio gate, including the
  diagnostics-file case, passed on Python 3.12.14.
- Gitleaks scanned a snapshot of tracked/non-ignored public source with fully
  redacted output and found zero secrets. Trivy recognized `uv.lock` and reported
  zero HIGH/CRITICAL runtime dependency findings. Source-mounted scanners ran
  without network; advisory download had no source mount. Development dependencies
  were excluded by this invocation. Both scans predate the diagnostics change;
  the lockfile is unchanged, but new source has not been rescanned. Python
  dependency-license inventory and a release SBOM remain publication work;
  loose-file scanning is not that inventory.

These results qualify the local adapter/package boundary. Host task/citation/
injection evaluation, genuine tenant/credential-lifecycle beta checks and remote
CI remain unrun. No artifact has been published, no existing agent configuration
was changed, and no live project/key was created by this implementation.

## Deterministic and artifact gates

Run the commands in [CONTRIBUTING.md](../../CONTRIBUTING.md). Tests include
in-process MCP plus subprocess stdio/SDK HTTP against a synthetic loopback peer.
The peer simulates denials and usage errors; it does not establish that a live
backend enforces tenant separation or credential lifecycle.

Installed qualification must build a wheel, install into a fresh environment, copy
tests into an unrelated temporary directory, and execute them there. Assert the
imported package lives in that environment, not a source checkout. Do not install
editable SDK/backend dependencies or set a source `PYTHONPATH`.

## Live endpoint gate

An operator prepares a synthetic beta project containing the example documents,
an allowed search key, a genuinely foreign project, and separate missing-scope,
expired, revoked, quota-limited and rate-limited credentials. Preparation remains
outside this repository; the qualifier never uses database access or creates keys.

Supply `RAGWELL_BASE_URL`, `RAGWELL_PROJECT_ID`, `RAGWELL_API_KEY` and the optional
case variables documented by `scripts/qualify_endpoint.py --help` through the
process environment. Then run:

```sh
uv run --locked --no-sync python scripts/qualify_endpoint.py --require-all
```

The positive corpus checks make four metered searches. The negative cases each
make one intentional search attempt; usage/provider work may occur if a fixture
was prepared incorrectly. No call is automatically replayed. The output records
case labels and sanitized adapter codes, never prompts, content or credentials.
Missing cases are skipped in exploratory mode and fail `--require-all` before
making any request. This gate does not replace backend security/integration tests.

Timeout, cancellation, oversized output and no-replay behavior are deterministic
adapter gates. Reproduce relevant live failures through a deliberately prepared
test environment before advertising broader service reliability; do not claim a
tiny arbitrary deadline proves live cancellation/refund behavior.

## Real agent tasks

For Codex CLI and Claude Code, use a clean installed artifact and each public
setup guide. Record client/OS/package/SDK/protocol versions, installation route,
the three example workflows, sources checked, unsupported claims, usage and any
repeated calls. Observe the hostile document exercise and revocation. A model's
failure to follow the skill is distinct from server authority enforcement.

Do not change a user's global agent configuration or disclose existing secrets to
perform qualification. Use isolated test configuration or an explicitly selected
user session. Ordinary-user onboarding is a later hosted-stage gate; this local
terminal pilot cannot satisfy it.
