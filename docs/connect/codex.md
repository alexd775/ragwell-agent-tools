# Connect Ragwell to Codex

Follow [the setup guide](../start-here.md) first. This route targets the local
Codex CLI. Desktop and cloud surfaces need their own qualification; local settings
do not automatically connect a ChatGPT or cloud chat. Test status is in
[compatibility](../compatibility.md).

## Add the connection

Add the [Codex configuration](../../integrations/openai/codex.toml) to your local
Codex `config.toml`, replacing `command` with the full installed executable path.
Merge it with existing configuration instead of replacing the file. The entry
forwards the three Ragwell environment variables without storing their values.

Start `codex` from the terminal where you supplied those variables. Open `/mcp`
and look for Ragwell and `ragwell_search`. If a workspace policy disallows local
MCP tools, an administrator may need to allow the connection.

## Add the optional workflow skill

Copy `skills/ragwell-knowledge` to `~/.agents/skills/ragwell-knowledge`, then restart
or refresh skill discovery. For a project-only installation, use
`.agents/skills/ragwell-knowledge` in that project. Do not overwrite an existing
skill with the same name without reviewing it. The folder contains no credentials.
[Codex skill locations](https://learn.chatgpt.com/docs/build-skills).

Ask:

> Use $ragwell-knowledge to compare the old and new travel policies in Ragwell. Cite each changed rule.

You can also ask a normal Ragwell question without installing the skill. Check the
returned filenames and original coordinates before relying on an explanation.

## Remove the connection

Disable/remove the `mcp_servers.ragwell` entry and remove the optional skill folder.
Revoke the dedicated key in Ragwell. Do not use `codex mcp get --json` output as a
support attachment if any of your other MCP configurations contains static secrets.

This guide follows [Codex's MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
See [troubleshooting](../troubleshooting.md) if the tool is unavailable.
