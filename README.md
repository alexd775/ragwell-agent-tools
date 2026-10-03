# Ragwell agent tools

Ask your agent questions about documents in your Ragwell project and get evidence
you can check against the original sources. Ragwell retrieves relevant passages;
your agent writes the explanation.

**Local early access:** the local adapter provides MCP search, bounded source
expansion and a reusable Ragwell skill. Source reads passed guarded Codex and
Claude Code tasks. The 0.1.0a3 candidate adds current-grant tool visibility and an
unmetered connection check using published SDK 0.2.2 and the updated API. It requires
terminal setup, a ready Ragwell project and a dedicated API key.

**Hosted beta:** invited testers can connect through ChatGPT web's Personal
custom-MCP plugin flow by signing in to Ragwell and approving one project. Linking,
cited sample tasks and disconnect/reconnect passed. This route needs no local
package or Ragwell API key. Managed workspaces and ordinary-user onboarding
remain unqualified. See the [compatibility record](docs/compatibility.md) for actual
test evidence; intended client support is not yet a certification.

| Your agent | Start here | Current route |
|---|---|---|
| Codex CLI | [Connect Codex](docs/connect/codex.md) | Local MCP and optional skill |
| Claude Code | [Connect Claude Code](docs/connect/claude-code.md) | Local MCP and optional skill |
| ChatGPT web / Personal | [Connect ChatGPT](docs/connect/chatgpt-work.md) | Invited beta OAuth plugin |
| Another MCP client | [Generic setup](docs/connect/other-mcp.md) | Qualify its local transport and credential handling |

Start with [the setup guide](docs/start-here.md), then try the
[sample questions](examples/workflows/README.md). You can ask how a process works,
compare policies, or consult decisions before making a change. The pilot cannot
upload/delete documents or switch projects. With `document:read`, the agent can
read additional context from a source returned by search, keeping its exact
document version and index generation.

Keys belong in agent environment/credential settings, never chat. Searches consume
Ragwell usage and returned text reaches your chosen agent provider. The API checks
access on every search; read-only access can still disclose the permitted documents.

For development, see [CONTRIBUTING.md](CONTRIBUTING.md). The independent package
uses the published Python SDK and requires no backend checkout. Product direction,
remaining delivery stages and boundaries are in [the strategy](docs/project/strategy.md)
and [the plan](docs/project/plan.md).
