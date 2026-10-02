# Ragwell agent tools

Ask your agent questions about documents in your Ragwell project and get evidence
you can check against the original sources. Ragwell retrieves relevant passages;
your agent writes the explanation.

**Local early access:** this first pilot provides one read-only MCP search tool and
a reusable Ragwell skill. The installed package passed 74 tests on Python 3.11–3.14
on macOS; real agent tasks and live beta access checks remain pending. It requires
terminal setup, a ready Ragwell project and a dedicated API key. Hosted account
linking for ChatGPT Work and simpler onboarding
are planned. See the [compatibility record](docs/compatibility.md) for actual test
evidence; intended client support is not yet a certification.

| Your agent | Start here | Current route |
|---|---|---|
| Codex CLI | [Connect Codex](docs/connect/codex.md) | Local MCP and optional skill |
| Claude Code | [Connect Claude Code](docs/connect/claude-code.md) | Local MCP and optional skill |
| ChatGPT Work | [Hosted connection plans](docs/connect/chatgpt-work.md) | OAuth connection planned |
| Another MCP client | [Generic setup](docs/connect/other-mcp.md) | Qualify its local transport and credential handling |

Start with [the setup guide](docs/start-here.md), then try the
[sample questions](examples/workflows/README.md). You can ask how a process works,
compare policies, or consult decisions before making a change. The pilot cannot
upload/delete documents, fetch additional source text, or switch projects.

Keys belong in agent environment/credential settings, never chat. Searches consume
Ragwell usage and returned text reaches your chosen agent provider. The API checks
access on every search; read-only access can still disclose the permitted documents.

For development, see [CONTRIBUTING.md](CONTRIBUTING.md). The independent package
uses the published Python SDK and requires no backend checkout. Product direction,
remaining delivery stages and boundaries are in [the strategy](docs/project/strategy.md)
and [the plan](docs/project/plan.md).
