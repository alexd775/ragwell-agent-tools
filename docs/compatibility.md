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
| Codex desktop/cloud | Planned qualification | Local CLI configuration is not evidence for other surfaces |
| ChatGPT Work | Hosted OAuth planned | Local API-key adapter cannot supply its remote authentication |
| Claude desktop/web and other providers | Unverified | Research/qualify each exact account, surface, transport and installation route |

Tool discovery does not authenticate a key. Fixed search-only advertising is
deliberate until machine capabilities discovery exists. Keys must carry current
`retrieval:search` grants for the configured project.

The package has not been published to PyPI or submitted to an agent directory.
An installable source artifact, public listing and qualified account/workspace
connection are separate milestones. Requalify host guides when behavior changes.

CI is configured for Linux on Python 3.11–3.14 and macOS/Windows on 3.12.