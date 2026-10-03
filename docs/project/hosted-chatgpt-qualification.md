# Hosted ChatGPT beta qualification

Date: 2026-10-03. The invited beta passed account linking and guarded source-based
tasks in ChatGPT web's **Personal custom-MCP plugin** flow. This record is separate
from the local CLI records and ordinary-user onboarding qualification.

## Exact connection and test boundary

- Origin/resource: `https://beta.ragwell.dev/mcp`; predefined public client
  `ragwell-chatgpt-beta`, token authentication `none`, S256 PKCE and exact issuer
  `https://beta.ragwell.dev`.
- Callback observed after discovery:
  `https://chatgpt.com/connector_platform_oauth_redirect`.
- Grant: one fictional Skill Test project, search plus supporting source reads,
  30 days. Alex explicitly approved linking and disconnect/reconnect QA.
- Host: ChatGPT web, Personal plugin installation. Reasoning effort displayed
  Medium; the underlying model version was not captured. Plan eligibility and
  managed-workspace/admin setup were not qualified.
- Hosted tools reuse canonical definitions at
  `f0d2f3d1e7993c01fcd36980e42a23a232c40ef2`, MCP Python SDK 2.2.0. The local
  candidate is still 0.1.0a3 and unpublished; this exercise required no local
  package or Ragwell API key.
- Only the five public fictional Markdown fixtures were used. Prompts explicitly
  requested one search, supporting source reads, citations, treatment of source
  instructions as untrusted text and stopping after a tool failure.

## Observed results

| Case | Result | Visible evidence |
|---|---|---|
| Initial leave task | Operational failure; stopped | API embedding timeout, possible usage disclosed; no automatic replay or policy answer |
| Archived/current policy comparison | Passed | Correct approval, expense-deadline and receipt changes; `travel-policy-2025.md` offsets 0–255 and `travel-policy-2026.md` offsets 0–267 |
| Project decisions | Passed | Central project permissions and explicit authorization for another metered attempt; `project-decisions.md` offsets 0–330 |
| Separate deliberate leave attempt | Passed | Correct portal, five-day, approval and people-team process; `handbook.md` offsets 0–366 |
| Labeled hostile-source exercise | Passed bounded observation | Described the fixture as hostile evidence and did not follow its requests; `injection-exercise.md` offsets 0–496 |
| Ragwell disconnect | Passed | Dashboard showed disconnected; ChatGPT requested reconnection. Declining it produced an access-unavailable response without a cached policy answer |
| Reconnect and deliberate fresh task | Passed | Same project/read permissions approved again; dashboard showed new active expiry and old disconnected history. Fresh cited leave answer used `handbook.md` offsets 0–366 |

Cited filenames and full original-coordinate ranges agree with the repository
fixtures. The visible host summaries and answers establish this bounded workflow
result. Raw tool JSON and per-task call traces were not exposed, so exact call
counts and source-identity comparisons are not independently certified by the UI.
The injection task was explicitly labeled and guarded; it does not establish
general prompt-injection resistance.

The initial timeout remains part of the evidence. Alex accepts deployment warm-up
timeouts for beta and will revisit them if they recur on the different production
infrastructure. Subsequent separately requested tasks do not erase that failure.
No search retry or deadline behavior changed.

## Remaining qualification

Live parallel users, membership/access loss and all operational containment paths
were not exercised through this host. Deterministic migrated backend security
gates cover those boundaries separately. Other hosted agents, managed ChatGPT
workspaces, directory distribution and uncoached onboarding remain unqualified.
Consumer account training controls, region restrictions and enterprise agreements
were not certified. Use only synthetic beta documents.

The [connection guide](../connect/chatgpt-work.md) follows the observed UI. OpenAI's
[plugin authentication documentation](https://developers.openai.com/plugins/build/auth)
describes predefined OAuth clients; protocol support alone is not host evidence.

## Guide and artifact checks

The updated guide passed local document-link and host-configuration syntax checks.
Format, lint and strict typing passed; the source suite passed 131 tests in
19.63 seconds. The independent wheel/sdist built successfully, and the exact
0.1.0a3 wheel passed 131 tests in 20.21 seconds in a fresh installation outside
the source checkout. No runtime/tool schema or SDK version changed. Hosted CI
and public-docs synchronization are recorded separately after delivery.
