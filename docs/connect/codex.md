# Connect Ragwell to Codex

Paste the [setup prompt](../start-here.md#set-up-with-a-prompt) into a local Codex
CLI session for guided installation. For manual setup, follow the
[quickstart](../start-here.md) to install `ragwel-cli` and supply your project and
API key. See [compatibility](../compatibility.md) for other Codex surfaces.

## Install the Ragwell skill

To install the skill from your local executable, run:

```sh
"$HOME/.local/bin/ragwel-cli" skill install --agent codex
```

The installer saves `~/.agents/skills/ragwell-knowledge/SKILL.md` and preserves
an existing copy. If your executable lacks `skill install`, use a newer release
or download the skill to that path. For a single project, use
`.agents/skills/ragwell-knowledge/SKILL.md` inside that project.
[Download SKILL.md](https://raw.githubusercontent.com/alexd775/ragwell-agent-tools/main/skills/ragwell-knowledge/SKILL.md) · [Codex skill locations](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

Start Codex from the terminal where you supplied the Ragwell variables. Type `$`
and select `ragwell-knowledge`, then ask about your project.

> Use $ragwell-knowledge to compare the old and new travel policies in Ragwell. Cite each changed rule.

The skill can run `ragwel-cli` in the agent's shell. Follow the next section if
you want Codex to use MCP tools and fetch surrounding source passages.

## Add the connection

Add the [Codex configuration](../../integrations/openai/codex.toml) to your local
Codex `config.toml`, replacing `command` with the full installed executable path.
Use the path to `ragwel-cli` for the standalone release or `ragwell-agent-tools` for
the Python package. Merge the entry with existing configuration. It
forwards the three Ragwell environment variables without storing their values.

Start `codex` from the terminal where you supplied those variables. Open `/mcp`
and look for Ragwell and `ragwell_search`. If a workspace policy disallows local
MCP tools, an administrator may need to allow the connection.

## Remove the connection

Remove the skill folder. If you configured MCP, disable or remove the
`mcp_servers.ragwell` entry. Revoke the dedicated key in Ragwell. Do not use
`codex mcp get --json` output as a support attachment if any of your other MCP
configurations contains static secrets.

This guide follows [Codex's MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
See [troubleshooting](../troubleshooting.md) if the tool is unavailable.
