# Connect your Ragwell knowledge

Use Ragwell from a terminal, a shell-capable agent, or an agent configured for
local MCP. For browser account linking, follow the [ChatGPT](connect/chatgpt-work.md)
or [Claude web](connect/claude-web.md) guide.

## Prepare your project

In the [Ragwell dashboard](https://app.ragwell.dev), create or choose a project and
upload documents. Wait until they are ready for search. For a safe first test, use
the synthetic documents in [starter pack](../examples/starter/README.md) and its
[starter questions](../examples/workflows/README.md).

Create a dedicated API key granting **`retrieval:search`** to that project. Copy
the project ID and use `https://api.ragwell.dev` as the API origin. The API origin
is the service address, not the dashboard page URL or a `/v1` endpoint.
Keep the key in your credential settings and give it a useful name and expiry.

To let an MCP agent read more surrounding text, also grant **`document:read`**.
The shell search command needs only `retrieval:search`.

## Install the local tool

The standalone `ragwel-cli` executable bundles its runtime for shell search and
local MCP. Run the installer when a binary release is available.

```sh
curl -fsSL https://app.ragwell.dev/ragwell-cli-install.sh | sh
"$HOME/.local/bin/ragwel-cli" --version
```

The installer detects Linux x86-64 or macOS Apple silicon and selects the newest
complete release by version, including prereleases. It checks the binary against
the release's `SHA256SUMS` and runs it to verify the version before installing it.
It prints the full executable path. The default is `$HOME/.local/bin/ragwel-cli`.
Set `RAGWELL_INSTALL_DIR` to an absolute path to use a different directory. The
Linux build targets the Ubuntu 22.04 baseline.

To install a specific version, use `sh -s -- v0.1.0a5` in place of `sh` and
substitute an available tag. Assets use the names `ragwel-cli-<tag>-linux-x86_64`
and `ragwel-cli-<tag>-macos-arm64`. [GitHub Releases](https://github.com/alexd775/ragwell-agent-tools/releases)

Use the full path to `ragwel-cli` in an MCP configuration and in the commands below.
In a cloud sandbox, choose a path where the sandbox allows programs to run.
The sandbox needs HTTPS access to Ragwell and a way to inject secrets into the
process environment. To run the installer inside it, allow HTTPS access to the
Ragwell dashboard, GitHub's API, and GitHub release assets as well.

The macOS executable uses an ad hoc signature. Use the Python package on systems
that require notarization for downloaded executables.

The published [Python package](https://pypi.org/project/ragwell-agent-tools/0.1.0a4/)
offers local MCP with Python 3.11 or newer and [uv](https://docs.astral.sh/uv/getting-started/installation/).
For example, to install the published `0.1.0a4` MCP adapter:

```sh
uv tool install 'ragwell-agent-tools==0.1.0a4' --python 3.12
ragwell-agent-tools --version
uv tool dir --bin
```

The last command shows the executable directory. Use the full `ragwell-agent-tools`
path in agent configuration. Shell search requires `0.1.0a5` or a later version
that includes the command.

## Supply your connection details

Set these variables in the environment from which you run Ragwell or start your
agent:

```sh
export RAGWELL_BASE_URL="https://api.ragwell.dev"
export RAGWELL_PROJECT_ID="your-project-uuid"
```

Enter the key without putting its value into command history. On macOS's default
zsh shell:

```sh
read -rs 'RAGWELL_API_KEY?Ragwell API key: '
export RAGWELL_API_KEY
```

On bash:

```sh
read -r -s -p 'Ragwell API key: ' RAGWELL_API_KEY
export RAGWELL_API_KEY
```

The key prompt hides typing. For a cloud sandbox, use the host's secret settings
to provide `RAGWELL_API_KEY`. Keep the key out of chat, command arguments, and
project files. Set the API origin and project in your trusted configuration.
Terminal exports apply to processes launched from that terminal.

## Check the connection without a search

After supplying all three variables, run:

```sh
"$HOME/.local/bin/ragwel-cli" --check
```

For the Python package, use `ragwell-agent-tools --check`. Expect `status: ready`
and `ragwell_search`. With `document:read`, the check also lists
`ragwell_fetch_source` as an MCP tool. This check reads current grants and uses
zero searches.

## Search from a shell

With the starter documents ready, send the UTF-8 query on stdin:

```sh
printf '%s' 'How do I request leave?' | "$HOME/.local/bin/ragwel-cli" search --query-stdin
```

The command writes one JSON result with passages and original source coordinates.
Use `--k` to request one to five matches, with five as the default. Source
expansion is available through MCP. Each search can consume workspace usage.
If a search fails, read the error and stop before deciding whether to make a
new attempt. A timeout can still record usage.

## Choose your agent and try a question

Continue with [Codex](connect/codex.md), [Claude Code](connect/claude-code.md), or
[another local MCP client](connect/other-mcp.md). After connecting, the agent should
discover `ragwell_search`. Ask:

> Using the documents in Ragwell, explain how I request leave. Show the supporting sources.

Expect supporting passages and filenames with available line/page/offset references.
Check them against the documents in Ragwell. Empty results can mean the project
is not ready or the question needs refinement; they do not prove there is no rule.

A successful test search consumes usage. The connection checks current grants
when listing and calling tools. Availability does not guarantee quota or service
health, and the API authorizes each search/read again. If you change grants, your
agent may need to refresh its tool list or restart; cached tools cannot restore access.

## Disconnect

Revoke the dedicated key in Ragwell to stop API access from both local routes.
Remove or disable the Ragwell MCP entry if you configured one. Remove the key
from the terminal or sandbox secret configuration.
When replacing an expired key, update the environment and restart the local agent.
See [troubleshooting](troubleshooting.md) for common problems.
