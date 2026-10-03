# Compatibility and qualification

The first implementation targets Python 3.11–3.14, `ragwell` 0.2.x and the pinned
MCP Python SDK 2.2.0. The initial local interpreter is Python 3.12.14 on macOS arm64.
Actual gate results and remaining work are recorded in
[qualification](project/qualification.md). `uv tool install` resolves the newest
compatible `ragwell` 0.2.x rather than `uv.lock`; result fields added by such a
release are omitted until deliberately projected, so searches keep working.

| Surface | Status | What the evidence establishes |
|---|---|---|
| Adapter and SDK HTTP contract | Local deterministic gates passed | Validation, result bounds, provenance, cancellation/admission and deliberate failures against synthetic peers |
| MCP in-process and stdio | Local protocol gates passed | Discovery/search, clean shutdown, legacy and modern connection modes; no model task evaluation |
| Clean installed wheel | Passed on macOS arm64, Python 3.11–3.14 | 74 tests per clean environment outside source/backend checkouts |
| Component-score schema repair | Passed on macOS arm64, Python 3.12.14 | 79 source/installed-wheel tests; both stdio modes accept unavailable scores |
| Live beta endpoint pilot | Accepted by Alex after seven passing cases | Four corpus checks plus scope/revoked/foreign-project denials; live expiry/quota/rate deferred, second-tenant ownership unconfirmed |
| Codex CLI 0.131.0 | Three guarded real tasks, explicit project-skill invocation and pre-revoked-key handling passed | Installed wheel on macOS 26.6.2 arm64; exact citations after skill repair; one known hostile fixture ignored; interactive onboarding unverified |
| Claude Code 2.1.148 / claude-opus-5-5 | Three guarded real tasks, native project-skill loading and pre-revoked-key handling passed | Same installed wheel/OS; exact citations and known hostile fixture handling; one initial API-unavailable call stopped without replay, fresh QA task subsequently passed; interactive onboarding unverified |
| Source reads: Codex CLI 0.131.0 and Claude Code 2.1.287 / claude-opus-5-5 | Seven guarded tasks passed with 0.1.0a2 / public SDK 0.2.1 | Exact issued identities, fixture slices, citations and native skill invocation; [dated evidence](project/source-host-qualification.md); static visibility, other surfaces and onboarding still unqualified |
| Current-grant discovery and source reads | 0.1.0a3 / public SDK 0.2.2: 131 source and installed tests, six hosted CI jobs, four live unmetered grant cases and seven guarded Codex/Claude tasks passed | [Dated evidence](project/grant-host-qualification.md); two original searches timed out at the API embedding stage and stopped without replay; fresh leave tasks passed; broader reliability and onboarding remain unqualified |
| Codex desktop/cloud | Planned qualification | Local CLI configuration is not evidence for other surfaces |
| ChatGPT web / Personal custom-MCP plugin | Invited hosted beta: linking, guarded source-based tasks and disconnect/reconnect passed, 2026-10-03 | [Dated evidence](project/hosted-chatgpt-qualification.md); Medium effort, model version uncaptured; one initial embedding timeout stopped without replay; operator-assisted setup only |
| ChatGPT Work / managed workspaces | Unqualified | Personal plugin QA does not establish workspace eligibility or administrator setup |
| Claude desktop/web and other providers | Unverified | Research/qualify each exact account, surface, transport and installation route |

Candidate 0.1.0a3 uses published SDK 0.2.2 for authenticated current-grant
discovery and an unmetered `--check`, with its own dated qualification above.
Earlier 0.1.0a1/a2 records remain historical. Keys must carry current
`retrieval:search` grants for the configured project. Source expansion additionally
requires `document:read` and the updated generation/source identity contract.
Earlier search-only evidence applies to 0.1.0a1; the source-read record separately
qualifies 0.1.0a2. Neither is relabeled as current-candidate evidence.

The package has not been published to PyPI or submitted to an agent directory.
An installable source artifact, public listing and qualified account/workspace
connection are separate milestones. Requalify host guides when behavior changes.

CI is configured for Linux on Python 3.11–3.14 and macOS/Windows on 3.12.
