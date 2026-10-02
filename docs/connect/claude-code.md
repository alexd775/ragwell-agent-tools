# Connect Ragwell to Claude Code

Complete [the setup guide](../start-here.md). This guide targets Claude Code's
local MCP process; it does not establish Claude desktop or web support. See
[compatibility](../compatibility.md) for qualification status.

## Add the connection

Set `RAGWELL_TOOLS_COMMAND` to the full installed executable path in the terminal
where you set the other Ragwell variables. For example:

```sh
export RAGWELL_TOOLS_COMMAND="/absolute/path/to/ragwell-agent-tools"
```

Merge [the Claude configuration](../../integrations/claude/mcp.json) into the
project's `.mcp.json`. It contains variable references rather than secret values.
Do not overwrite other MCP entries. Start `claude` from that terminal and approve
the project connection when prompted. Open `/mcp` and check for `ragwell_search`.

Claude Code expands the variables in this configuration. If a variable is absent,
the host can retain its literal placeholder; supply all four variables and restart
before trying again. A desktop process launched elsewhere may not inherit them.

## Add the optional skill and try a question

Copy `skills/ragwell-knowledge` to `~/.claude/skills/ragwell-knowledge`, or use
`.claude/skills/ragwell-knowledge` inside a project for project-only discovery.
Preserve any existing skill with that name. These local locations do not install
the skill in a cloud/Cowork session. [Claude skill locations](https://code.claude.com/docs/en/skills).
Ask:

> Using Ragwell, explain how to request leave and cite the supporting passages.

Compare the explanation with the source document. The skill guides evidence use,
but the API enforces project access and limits independently.

## Disconnect

Remove/disable the Ragwell entry in `.mcp.json` and remove the optional skill.
Revoke the dedicated key in Ragwell to stop subsequent searches. Replace an expired
key in your environment and restart the agent when reconnecting.

The configuration follows [Claude Code's MCP documentation](https://code.claude.com/docs/en/mcp).
See [troubleshooting](../troubleshooting.md) for connection and permission errors.
