# Compatibility and tested surfaces

The local adapter supports Python 3.11–3.14, Ragwell SDK 0.2.x and MCP Python SDK
2.2.0. Candidate **0.1.0a3** uses published SDK **0.2.2** for current-grant checks,
search and bounded supporting-source reads.

The client observations below were recorded on **2026-10-02 through 2026-10-04**.
They establish the named versions and account surfaces; other versions, plans
and installation routes need their own checks.

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

The tools package is not yet published to PyPI or an agent directory. Source
installation, directory listing and hosted account eligibility are separate.
For setup, choose a guide from the [repository overview](../README.md). For a
problem, use [troubleshooting](troubleshooting.md) and report the observed client,
surface, version, sanitized error code and failing step.
