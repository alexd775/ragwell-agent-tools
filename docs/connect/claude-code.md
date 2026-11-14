# Connect Ragwell to Claude Code

Paste the [setup prompt](../start-here.md#set-up-with-a-prompt) into a local Claude
Code session for guided installation. For manual setup, follow the
[quickstart](../start-here.md) to install `ragwel-cli` and supply your project and
API key. See [compatibility](../compatibility.md) for other Claude surfaces.

## Install the Ragwell skill

To install the skill from your local executable, run:

```sh
"$HOME/.local/bin/ragwel-cli" skill install --agent claude-code
```

The installer saves `~/.claude/skills/ragwell-knowledge/SKILL.md` and preserves an
existing copy. If your executable lacks `skill install`, use a newer release or
download the skill to that path. For a single project, use
`.claude/skills/ragwell-knowledge/SKILL.md` inside that project.
[Download SKILL.md](https://raw.githubusercontent.com/alexd775/ragwell-agent-tools/main/skills/ragwell-knowledge/SKILL.md) · [Claude Code skill locations](https://code.claude.com/docs/en/skills#choose-where-skills-load)

Start Claude Code from the terminal where you supplied the Ragwell variables.
Type `/ragwell-knowledge` and ask about your project.

> /ragwell-knowledge Using Ragwell, explain how to request leave and cite the supporting passages.

The skill can run `ragwel-cli` in the agent's shell. Follow the next section if
you want Claude Code to use MCP tools and fetch surrounding source passages.

## Add the connection

Set `RAGWELL_TOOLS_COMMAND` to the full executable path in the terminal where you
set the other Ragwell variables. For the standalone release, use:

```sh
export RAGWELL_TOOLS_COMMAND="/absolute/path/to/ragwel-cli"
```

For the Python package, use the full path to `ragwell-agent-tools`.
Merge [the Claude configuration](../../integrations/claude/mcp.json) into the
project's `.mcp.json`. It contains variable references rather than secret values.
Do not overwrite other MCP entries. Start `claude` from that terminal and approve
the project connection when prompted. Open `/mcp` and check for `ragwell_search`.

Claude Code expands the variables in this configuration. If a variable is absent,
the host can retain its literal placeholder; supply all four variables and restart
before trying again. A desktop process launched elsewhere may not inherit them.

## Disconnect

Remove the skill folder. If you configured MCP, remove or disable the Ragwell
entry in `.mcp.json`. Revoke the dedicated key in Ragwell to stop subsequent
searches. Replace an expired key in your environment and restart the agent when
reconnecting.

The configuration follows [Claude Code's MCP documentation](https://code.claude.com/docs/en/mcp).
See [troubleshooting](../troubleshooting.md) for connection and permission errors.
