# Compatibility and tested surfaces

The local adapter supports Python 3.11–3.14 and MCP Python SDK 2.2.0. Version
**0.1.0a4** requires Ragwell SDK **0.2.3** or later in the 0.2.x series and the
project-description API. It adds fresh, authorized project context to tool
listings and uses published SDK **0.2.3**. Synthetic source and installed-wheel
qualification covers updated/cleared descriptions, current grants, scoped
metadata reads, failure handling and no-search discovery. These checks do not
establish new live-host qualification. Earlier **0.1.0a3**
observations below used published SDK **0.2.2**.

The client observations below were recorded on **2026-10-02 through 2026-10-04**.
They establish the named versions and account surfaces; other versions, plans
and installation routes need their own checks.

The current hosted setup guides target production `https://app.ragwell.dev/mcp`
with public clients `ragwell-chatgpt` and `ragwell-claude`. The production
configuration declares their exact callbacks. On 2026-10-17, OAuth and protected
resource discovery returned the production issuer, resource and supported scopes;
unauthenticated MCP access required authentication. Full browser linking, cited
tasks and disconnect/reconnect were
not repeated on production. The earlier beta observations below remain historical
evidence and do not certify those production flows.

| Surface | Recorded support | Limits |
| --- | --- | --- |
| Local adapter and clean installed wheel | Deterministic protocol, validation, provenance, authorization projection, failure and no-replay tests passed. CI covers Linux Python 3.11–3.14 and macOS/Windows Python 3.12. | Synthetic peers exercise the adapter; they do not certify live service capacity or human usability. |
| Codex CLI 0.131.0 | Guarded process, policy-comparison and project-decision tasks passed on macOS arm64, including source reads and explicit project-skill invocation. | Desktop/cloud and uncoached installation remain unverified; the resolved default model was not captured. |
| Claude Code 2.1.287 / claude-opus-5-5 | The same guarded workflows, supporting-source reads and native project-skill loading passed on macOS arm64. | Other Claude Code versions and uncoached installation need separate checks. |
| ChatGPT web / Personal custom MCP | Invited beta account linking, cited workflows, source reads and disconnect/reconnect passed. | Operator-assisted setup; underlying model version was not captured. |
| Claude web / Free personal / Chat / Sonnet 5.5 Medium | Invited beta account linking, cited workflows, source reads and disconnect/reconnect passed. | Operator-assisted setup. Successful tasks used preloaded tools after a lazy-loading interruption. |
| ChatGPT Work / managed workspaces | Unqualified. | Personal custom-MCP observations do not establish workspace eligibility or administrator setup. |
| Codex desktop/cloud, Claude desktop/Cowork and other providers | Unverified. | Generic MCP compatibility is not a tested installation or account route. |

## Requirements and known limitations

Local keys need current `retrieval:search` access to the configured project.
Source reads additionally need `document:read` and the generation/source identity
contract. `ragwell-agent-tools --check` reads current grants without making a
search; it does not prove document readiness, available quota or provider health.

`uv tool install` resolves compatible public SDK dependencies rather than applying
the repository's development lock. Changes to projected fields or supported
versions are reviewed explicitly.

Beta searches have encountered embedding timeouts following deployment. Agents
stopped without automatic replay; separate later tasks succeeded. A timeout can
still record usage. Claude web also encountered a tool-loading interruption;
the [connection guide](connect/claude-web.md) describes the observed workaround.

Guarded tests using a labeled hostile document do not establish general
prompt-injection resistance. Nontechnical onboarding, production reliability,
consumer data controls and regional/enterprise guarantees are not certified by
these observations. Live local-key expiry, quota and rate fixtures remain
unqualified.

Use an explicit prerelease version when installing the package. Agent-directory
listing and hosted account eligibility remain separate from Python installation.
For setup, choose a guide from the [repository overview](../README.md). For a
problem, use [troubleshooting](troubleshooting.md) and report the observed client,
surface, version, sanitized error code and failing step.
