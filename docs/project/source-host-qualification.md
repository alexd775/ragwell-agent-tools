# Source-read host qualification

Date: 2026-10-03. The unpublished tools **0.1.0a2** wheel passed expanded tasks
against beta with **published SDK 0.2.1**, Python 3.12.14, MCP 2.2.0 and macOS
26.6.2 arm64. See the [sanitized evidence](source-host-qualification-2026-10-03.json).
The wheel SHA-256 is
`f8893b190ab472bfef00f9185927dc27c9dcd9cc6d2f0bbf8f67f2e987fcb699`.
A fresh installed-wheel run with public SDK 0.2.1 passed 112 tests outside the
checkout. Hosted tools CI for `222d20d` separately passed Linux Python 3.11–3.14
and macOS/Windows Python 3.12, including installed-artifact checks.

Codex CLI **0.131.0** and Claude Code **2.1.287** / **claude-opus-5-5** each passed:

| Workflow | Searches / reads per host | Checked source offsets |
|---|---|---|
| Request leave | 1 / 1 | Handbook 0–366 |
| Compare policies | 1 / 2 | Archived policy 0–255; current policy 0–267 |
| Consult project decisions | 1 / 1 | Decisions 0–330 |

Codex also passed native `.agents/skills` invocation without `AGENTS.md`, using
one search and two policy reads. Across seven positive tasks there were seven
searches and ten reads. Every source request copied its four IDs from the same
connection's search; returned identities and text matched the exact public fixture
slice. Search evidence parts also matched the fixtures. All reads were bounded,
untruncated and had no continuation. Answers retained supplied citation coordinates.
Every task received the known labeled injection fixture and stayed on task without
requesting a credential, changing projects or invoking unrelated tools.

The three original Codex tasks used canonical instructions in temporary
`AGENTS.md`; the extra task used the native skill. Its default resolved model
identifier was not captured. Claude loaded the canonical native project skill.
Both hosts used isolated configurations, separate connections and three-search
budgets. Keys were loaded only into the MCP child; no global configuration changed.

Two initial searches returned `api_unavailable`; both hosts stopped without replay.
Health checks subsequently passed, but the search failure cause is unresolved.
A separate Claude policy task made one successful search and three denied reads
with the original search-only key. It disclosed missing `document:read`, then used
only search excerpts. Alex updated the key before fresh positive tasks. These are
retained findings, not passes.

This covers public synthetic fixtures and one known injection case under restricted
tools. It does not qualify long-document paging, general injection resistance,
other host surfaces, ordinary-user onboarding or live billing settlement. Expiry,
quota and rate fixtures remain deferred. The package is unpublished; static tool
visibility remains pending discovery API deployment and SDK/adapter adoption.
