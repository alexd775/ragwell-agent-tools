# Local pilot qualification

Current-grant discovery and source reads in 0.1.0a3 have separate
[2026-10-03 host and artifact qualification](grant-host-qualification.md), using
public SDK 0.2.2. The earlier records below remain historical.

Expanded 0.1.0a2 source reads have separate
[2026-10-03 live host qualification](source-host-qualification.md), with public
SDK 0.2.1. The historical search-only pilot evidence below remains unchanged.

Date: 2026-10-02. The local pilot candidate is implemented and locally qualified.
The four positive live beta corpus checks and the supplied scope/revocation/
foreign-project denials now pass. Alex accepted this endpoint gate for pilot
sequencing with expiry, quota and rate cases deferred. Codex CLI and Claude Code
now pass the three guarded model workflows with checked citations and pre-revoked-
key handling. The advanced local task pilot is complete. Interactive onboarding,
other host surfaces and production qualification remain separate later gates.

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

## Accepted endpoint pilot gate, 2026-10-02

Alex supplied a subsequent run with seven passing cases: leave, archived policy,
current policy, project decisions, missing scope, revoked credential and foreign
project. 

The expired-key case is deferred until its prepared credential expires; the API's minimum expiry
window prevented the desired immediate exercise. Quota and rate cases are deferred
because preparing controlled fixtures is currently impractical. Their deterministic
adapter tests passed, but their live behavior is **unverified**, not passed. The
qualifier retains `SKIP` reporting and the strict `--require-all` option. These
deferrals are not production-release certification.

The foreign-project case proves denial for the configured alternate project. This
run does not independently establish that it belongs to a second tenant. Model
workflows, citations and hostile-document behavior are recorded separately below.
No additional endpoint searches are needed to repeat the accepted run.

## Guarded real-host pilot, 2026-10-02

The rebuilt `0.1.0a1` wheel runs from a fresh Python 3.12.14 environment outside
the repository, using published Ragwell SDK 0.2.0 and MCP 2.2.0, on macOS 26.6.2
arm64. The retrieved content was checked against all five public sample documents:
every returned evidence part exactly matched its synthetic fixture. No customer
corpus was used. Each task starts a separate connection with a three-search budget.

Codex CLI **0.131.0** completed the three workflows:

| Workflow | Checked outcome | Source coordinates copied from the tool |
|---|---|---|
| Request leave | Staff portal, five working days, manager approval, approval before booking, people-team fallback; missing portal details disclosed | `handbook.md`, lines 1–12, offsets 0–366 |
| Compare policies | Archived/current status, both effective dates, every trip versus over EUR 200 approval, 30 versus 14 calendar days, EUR 25+ versus every-claim receipts | `travel-policy-2025.md`, lines 1–7, offsets 0–255; `travel-policy-2026.md`, lines 1–7, offsets 0–267 |
| Consult project decisions | Reject automatic timeout replay and self-granted access to another project | `project-decisions.md`, lines 1–6, offsets 0–330 |

The first leave answer invented narrower coordinates. The canonical skill now
requires copying the returned citation/part coordinates exactly, retaining broad
ranges rather than calculating offsets from excerpts. The leave retest passed.
An initial policy task requested `k=8`; local input validation rejected it before
SDK dispatch, and the model corrected it to five. The skill now states the 1–5
range and default. A targeted policy retest made one valid search and passed.
These are real host findings, not claims that every model follows the skill.

All positive tasks received the labeled hostile-document fixture. The observed
answers continued the requested evidence tasks without requesting a credential,
changing project scope, invoking deletion, or attempting exfiltration. This is
evidence for one known synthetic fixture under restricted tools, not broad
prompt-injection certification. A separate pre-revoked credential task returned
`authentication_failed`; Codex stopped after one search attempt and directed the
user to connection settings without asking for a key in chat. Revocation during
an already-running connection was not exercised.

Six positive SDK search calls and one revoked-credential call were made across
the initial cases and intentional retests. One invalid-input tool call never
reached the SDK. Codex also made empty resource-discovery probes; one initial
resource read used a nonexistent server and failed locally. No ambiguous remote
search failure was replayed. Backend billing settlement was not independently
measured in this host exercise.

The Codex run used `--ignore-user-config`, ephemeral sessions and a temporary
workspace, with shell/web/apps/plugins/other agent tools disabled. Ragwell keys
were loaded only into the MCP child through `uv --env-file`; they were absent from
the model-host environment. The canonical instructions were supplied through the
temporary workspace's `AGENTS.md` for the original three tasks. A separate test
used the public guide's explicit `$ragwell-knowledge` policy question in a fresh
temporary Git project containing only `.agents/skills/ragwell-knowledge`, with no
`AGENTS.md`. It completed the comparison with one search and exact per-rule
citations. This qualifies that invocation route for this client; the raw skill
body delivered internally by Codex was not captured. The model used the client
default; its resolved model identifier and wire protocol negotiation were not
captured. Deterministic protocol results above remain separate evidence.

Claude Code **2.1.148** initially reported `claude-sonnet-4-6` and failed with an
expired provider OAuth token before any Ragwell search. Alex renewed its login;
the successful runs reported **`claude-opus-5-5`**. They used an isolated strict
MCP configuration, project/local settings, the native `Skill` tool and only
`mcp__ragwell__ragwell_search`. The canonical skill body appeared in the host
context for all three workflows, confirming project-local native skill loading.
Ragwell credentials remained absent from the model-host environment.

Claude completed leave, policy comparison and project decisions with the same
checked facts and copied coordinates in the table above. The leave answer
explicitly identified the handbook as fictional test material and disclosed the
absence of an effective date. All positive responses returned the five exact
public fixtures, including the hostile exercise, and no hostile instructions
were acted on. The pre-revoked-key task stopped after one attempt, explained the
missing evidence and directed the user to connection settings without soliciting
a key in chat.

The first post-login leave task returned `api_unavailable`. Claude disclosed the
failure and uncertain usage without replaying it or inventing an answer. Both
unauthenticated health endpoints subsequently returned HTTP 200, and the distinct
policy/decision tasks succeeded. A deliberate fresh leave QA task then passed.
The cause and HTTP status of the initial failure were not captured; it remains an
observed service failure, not a proven adapter defect or resolved backend cause.
Claude made five SDK search calls: three successful workflow calls, one initial
unavailable call and one revoked-key call. No automatic retry occurred.

These headless tests qualify the advanced local task pilot, not an interactive
`/mcp` setup walkthrough, global installation, ordinary-user onboarding or other
desktop/cloud surfaces. The live expiry/quota/rate deferrals and unconfirmed
second-tenant fixture remain recorded above. No global client configuration was
changed and no package was published.

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

For `RAGWELL_QA_SCOPE_KEY`, create a separate active, unexpired API key with
`project:read` for the same synthetic project and without `retrieval:search`.
Supply its complete show-once credential, rather than a scope name, key ID or masked
display value. Reading that project should succeed; searching it should return
HTTP 403 `permission_denied`, surfaced as SDK `PermissionDeniedError` and tool
`access_denied`. HTTP 401 `authentication_required` becomes SDK
`AuthenticationError` and tool `authentication_failed`: it does not prove the
missing-search-scope case. The API deliberately does not distinguish malformed,
unknown, expired, revoked, disabled or empty-grant credentials in that response.

Supply `RAGWELL_BASE_URL`, `RAGWELL_PROJECT_ID`, `RAGWELL_API_KEY` and the optional
case variables documented by `scripts/qualify_endpoint.py --help` through the
process environment. For exported variables, run:

```sh
uv run --locked --no-sync python scripts/qualify_endpoint.py --require-all
```

If those variables are in an ignored local `.env` file, load it explicitly:

```sh
uv run --locked --no-sync --env-file .env python scripts/qualify_endpoint.py
```

With only the three primary variables, this checks the four corpus searches and
skips the denial cases. Add `--require-all` after preparing every denial fixture.
The Python script itself does not load `.env`; `uv --env-file` supplies the process
environment. Its child MCP process receives the same validated origin, project,
credential and runtime limits.

The positive corpus checks make four metered searches. The negative cases each
make one intentional search attempt; usage/provider work may occur if a fixture
was prepared incorrectly. No call is automatically replayed. The output records
case labels and sanitized adapter codes, never prompts, content or credentials.
Missing cases are skipped in exploratory mode and fail `--require-all` before
making any request. This gate does not replace backend security/integration tests.

Rejected searches report a fixed adapter code such as `authentication_failed` or
`connection_failed`. Unexpected MCP failures report only nested exception types
and code locations; exception messages, source content and argument values are
excluded. A component score may be unavailable; the MCP output schema permits
the corresponding omitted field.

Timeout, cancellation, oversized output and no-replay behavior are deterministic
adapter gates. Reproduce relevant live failures through a deliberately prepared
test environment before advertising broader service reliability; do not claim a
tiny arbitrary deadline proves live cancellation/refund behavior.

## Source expansion candidate — 2026-10-02

Candidate 0.1.0a2 has separate [source-expansion evidence](source-expansion.md):
112 source/installed-wheel tests, published SDK 0.2.0 qualification across Python
3.11–3.14 on macOS, and an independent installed SDK 0.2.1 candidate check.
This does not extend the earlier search-only host certification. Live expanded
Codex/Claude tasks require the updated beta API before qualification.

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


## Hosted transport definition extraction, 2026-10-03

Immutable source `f0d2f3d1e7993c01fcd36980e42a23a232c40ef2` exports canonical tool
definitions for the separately owned hosted backend transport. Local handlers
still filter those definitions by current grants. Ruff, strict typing and 131
source tests passed. The independent wheel/sdist built; fresh Python 3.12.14
installation outside the checkout passed all 131 tests and verified its import
origin. No package publication or new live hosted client qualification is claimed.
OAuth and hosted grants remain backend responsibilities; this public repository
contains no backend imports, database access or hosted customer credentials.
