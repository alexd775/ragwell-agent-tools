# Ragwell agent tools

Ask your agent questions about documents in your Ragwell project and get evidence
you can check against the original sources. Ragwell retrieves relevant passages;
your agent writes the explanation.

**Local early access:** the local adapter provides MCP search, bounded source
expansion and a reusable Ragwell skill. Source reads passed guarded Codex and
Claude Code tasks. Version 0.1.0a4 adds the owner's project description to
authorized tool listings, helping agents recognize the connected knowledge. It
requires published SDK 0.2.3 and a compatible API. Local use requires terminal
setup, a ready Ragwell project
and a dedicated API key. See the [compatibility record](docs/compatibility.md)
for the earlier qualified clients and current delivery limits.

**Hosted connection:** use the production endpoint and OAuth client settings in
the ChatGPT or Claude web guide. Earlier invited testers connected through
ChatGPT web's Personal custom-MCP plugin flow or Claude web by signing in to Ragwell and approving one
project. Linking, cited sample tasks/source reads and disconnect/reconnect passed.
This route needs no local package or Ragwell API key. Managed workspaces and
ordinary-user onboarding remain unqualified. See the [compatibility record](docs/compatibility.md) for actual
test evidence; intended client support is not yet a certification.

| Your agent | Start here | Current route |
|---|---|---|
| Codex CLI | [Connect Codex](docs/connect/codex.md) | Local MCP and optional skill |
| Claude Code | [Connect Claude Code](docs/connect/claude-code.md) | Local MCP and optional skill |
| ChatGPT web / Personal | [Connect ChatGPT](docs/connect/chatgpt-work.md) | Hosted OAuth plugin; see qualification limits |
| Claude web / Free personal | [Connect Claude web](docs/connect/claude-web.md) | Hosted OAuth connector; see qualification limits |
| Another MCP client | [Generic setup](docs/connect/other-mcp.md) | Qualify its local transport and credential handling |

Start with your agent guide above, or try the
[four-document starter pack](examples/starter/README.md) and
[sample questions](examples/workflows/README.md). Local setup is described in
[the setup guide](docs/start-here.md). You can ask how a process works,
compare policies, or consult decisions before making a change. The pilot cannot
upload/delete documents or switch projects. With `document:read`, the agent can
read additional context from a source returned by search, keeping its exact
document version and index generation.

For local connections, keys belong in agent credential settings, never chat. Searches consume
Ragwell usage and returned text reaches your chosen agent provider. The API checks
access on every search; read-only access can still disclose the permitted documents.
Project descriptions also reach agents with current search access. After editing
or clearing a description in Ragwell project settings, refresh the agent's tool
list or reconnect if the client caches it.

For development, see [CONTRIBUTING.md](CONTRIBUTING.md). The independent package
uses the published Python SDK and requires no backend checkout. See
[how the tools work](docs/reference/architecture.md) and
[tested compatibility](docs/compatibility.md) for boundaries and supported routes.
