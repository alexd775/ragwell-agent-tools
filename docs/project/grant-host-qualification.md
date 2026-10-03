# Current-grant host qualification

Date: 2026-10-03. The unpublished **0.1.0a3** candidate uses public **Ragwell
SDK 0.2.2**, MCP 2.2.0 and Python 3.12.14 on macOS 26.6.2 arm64. Runtime revision
is `7908b9fb7b503f36203f82cfcbe8fdcae799381c`; guide revision is
`fec1dc403ff5d0a821a1bfeb946cbfbb8ad2b550`. Installed wheel SHA-256:
`924c9f78a7f6ad7e1ec25f67564885daa2c13db70a9e6255702aff9a8912c100`.
See [sanitized evidence](grant-host-qualification-2026-10-03.json).

## Adapter and installed artifact

Formatting, lint, strict typing and **131 source tests** passed. A fresh wheel
installation outside all checkouts passed **131 tests** with the public SDK.
Hosted CI passed all six jobs: Linux Python 3.11–3.14, macOS and Windows Python
3.12, each including installed-artifact qualification.
[Runtime CI](https://github.com/alexd775/ragwell-agent-tools/actions/runs/37115250782),
[guide CI](https://github.com/alexd775/ragwell-agent-tools/actions/runs/37115348943).

The new deterministic cases establish configured-project scope intersection,
withdrawn grants between listing and dispatch, failure without a cached snapshot
or broader fallback, issued-reference clearing, strict snapshot bounds and
duplicates, shared deadlines, and no metered dispatch after discovery denial.
Both stdio modes and the unmetered CLI check are exercised.

Four live discovery-only cases passed with **zero searches**: the allowed key
exposed both tools; a same-project key without search exposed neither; the
pre-revoked key failed authentication; an ungranted configured project exposed
neither tool. These do not establish a new live two-tenant fixture or live grant
withdrawal during a model session; those boundaries have separate API and
deterministic adapter tests.

## Real host tasks

Codex CLI **0.131.0** and Claude Code **2.1.287 / claude-opus-5-5** completed
leave, policy comparison and project-decisions workflows. Codex also completed
explicit native `.agents/skills` invocation without `AGENTS.md`.

| Workflow | Searches / reads per host | Exact checked source offsets |
|---|---|---|
| Request leave, fresh task | 1 / 1 | Handbook 0–366 |
| Compare policies | 1 / 2 | Archived policy 0–255; current policy 0–267 |
| Consult project decisions | 1 / 1 | Decisions 0–330 |
| Codex native skill | 1 / 2 | Both policy ranges above |

Seven positive tasks made **seven successful searches and ten bounded source
reads**. Every read used four identities issued by the same connection's search;
returned identities and text matched the exact public fixture slice. Search
evidence parts also matched the fixtures. The answers preserved original citation
coordinates and disclosed evidence gaps. All tasks received the known labeled
injection fixture and stayed within the allowed tools.

The original leave task in each host failed once with `api_unavailable`. Both
agents disclosed missing evidence and stopped without replay or guessing source
IDs. Read-only operator correlation established HTTP **504** and
`retrieval_embedding_timeout`, with **zero database search time**. Effective beta
deadlines were 1.5 seconds for embedding and 3 seconds for retrieval. The logs
identify the failing stage, not its underlying provider/network cause. No API
configuration was changed. Separate, deliberate fresh leave tasks subsequently
passed; the two original failures remain findings and are excluded from the seven
positive tasks. Total QA search attempts were nine, with no automatic retries.

Each task had its own MCP connection and a three-search/three-read budget. Keys
were loaded only into the MCP child, not the model-host environment. Codex used
canonical instructions in temporary `AGENTS.md` for three cases and a native skill
for the fourth; its resolved default model identifier was not captured. Claude
loaded the canonical native project skill. No global configuration changed.

## Limits

This qualifies the guarded advanced local routes with public synthetic fixtures,
not interactive onboarding, general prompt-injection resistance, long-document
paging, other desktop/cloud/browser surfaces, or live billing settlement. Live
expiry, quota and rate fixtures remain deferred. The recurring embedding timeout
needs a separate bounded latency/reliability investigation; fresh passes do not
resolve it. The tools package remains unpublished, and account linking and
ordinary-user distribution remain later stages.
