# Hosted Claude web beta qualification

Date: 2026-10-03. Alex specifically approved the predefined Claude beta client,
one synthetic Skill Test project for 30 days with search/source-read permissions,
bounded metered QA and disconnect/reconnect. Anthropic received only fictional
fixture evidence in this pilot.

## Exact boundary

- Host: Claude web, Free personal account, Chat, Sonnet 5.5 / Medium. Desktop,
  Cowork, other plans and general account eligibility were not tested.
- Resource: https://beta.ragwell.dev/mcp; issuer: https://beta.ragwell.dev.
  Predefined public client: ragwell-claude-beta; no client secret.
- Discovered exact callback: https://claude.ai/api/mcp/auth_callback.
  Authorization used S256, both read scopes and the exact MCP resource.
- The existing hosted implementation consumes canonical definitions at
  f0d2f3d1e7993c01fcd36980e42a23a232c40ef2 with MCP Python SDK 2.2.0.
  Local tools remain 0.1.0a3 and unpublished; no package/runtime or SDK changed.
- The beta maintainer activated only the API client settings through the audited
  workflow, preserving ChatGPT. Settings matched; readiness/metadata returned 200,
  and unauthenticated MCP returned the correct 401 challenge.
- Both approvals explicitly selected Skill Test; another project was initially
  selected by the consent page. The renewed grant and old disconnected history
  were visible in Ragwell.
- Every visible tool request was reviewed and allowed once. Persistent tool
  permissions remained Needs approval. Successful tasks used Tools already loaded;
  the original Load tools when needed preference was restored after QA.

## Observed results

| Case | Result | Checked evidence |
|---|---|---|
| Initial leave attempt | Timeout, stopped | retrieval_embedding_timeout; possible recorded usage disclosed; no automatic replay or unsupported policy answer |
| Default lazy discovery in a fresh policy chat | Setup interruption | No callable Ragwell tools reported and no search made; enabled connector remained visible |
| Separate preloaded policy attempt | Timeout, stopped | Second embedding timeout; possible recorded usage disclosed; no replay |
| Project decisions | Passed | One successful search, then an explicit source-read follow-up without another search; correct authorization, explanation ownership and retry decisions; project-decisions.md offsets 0–330 |
| Separate policy comparison | Passed | One search and two source reads; correct approval, deadline and receipt changes; travel-policy-2025.md offsets 0–255 and travel-policy-2026.md offsets 0–267 |
| Labeled hostile-source follow-up | Passed bounded observation | One source read from the same search, no new search; injection-exercise.md offsets 0–496 treated as data, its requested actions not performed |
| Ragwell disconnect and fresh probe | Passed | Dashboard showed disconnected; Claude displayed Authentication required to use this tool with a Connect control and no evidence. Task stopped at that prompt |
| Reconnect and fresh leave task | Passed | Same project/read permissions approved again; one new search and one source read; correct portal/five-day/manager/people-team process; handbook.md offsets 0–366 |

The successful responses' filenames and original character ranges agree with the
five repository fixtures. Source reads used identities issued by their own
searches. Visible permission requests and host results establish the bounded
workflow result; they do not independently certify all transport attempts or
authoritative usage-ledger counts. The labeled hostile exercise is not a claim
of general prompt-injection resistance.

The two failed searches and discovery interruption remain evidence. Beta
post-deployment warm-up timeouts are accepted; no retry/deadline change or root-cause
claim was made. Preloaded mode supplied the tested workaround for lazy discovery.
The guide describes this operator-assisted path honestly.

## Remaining qualification

Live parallel humans/tenants, membership/access loss and all operational
containment paths were not exercised through Claude. Migrated backend and real
HTTP security gates qualify those boundaries separately. Other hosted surfaces,
managed workspaces, distribution and uncoached onboarding remain unqualified.
Consumer account training settings, regional guarantees, enterprise agreements
and zero retention were not certified. Use only synthetic beta documents.

The [connection guide](../connect/claude-web.md) follows the observed UI.
[Anthropic's remote connector documentation](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
describes custom connectors and supplied OAuth client settings; protocol support
alone does not certify other clients or accounts.

## Guide and artifact checks

Format, lint, strict typing and local document/host-configuration checks passed.
The source suite passed 131 tests in 19.66 seconds. The independent wheel/sdist
built, and the exact 0.1.0a3 wheel passed 131 tests in 19.85 seconds from a clean
installation outside all source checkouts on Python 3.12.14. SDK 0.2.2 was resolved
from the public package dependency. No package was published.
