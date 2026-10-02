# Connect your Ragwell knowledge

This local early-access setup is for people comfortable using a terminal. If you
prefer a sign-in-and-connect flow, follow the [hosted connection plan](connect/chatgpt-work.md).
The pilot retrieves passages and citations from one project; your agent explains them.

## Prepare your project

In Ragwell, create or choose a project and upload documents. Wait until they are
ready for search. For a safe first test, use the synthetic documents in
[sample-knowledge](../examples/sample-knowledge) and their
[starter questions](../examples/workflows/README.md).

Create a dedicated API key granting **`retrieval:search`** to that project. Copy
the project ID and the API origin provided for your beta environment. The API
origin is the service address, not the dashboard page URL or a `/v1` endpoint.
Keep the key in your credential settings and give it a useful name and expiry.

## Install the local tool

Use Python 3.11 or newer and [uv](https://docs.astral.sh/uv/getting-started/installation/).
From a checkout containing this pilot, run:

```sh
uv tool install . --python 3.12
ragwell-agent-tools --version
uv tool dir --bin
```

The version should be `0.1.0a1`. The last command shows the executable directory;
use its full `ragwell-agent-tools` path in agent configuration. This package has
not been published to PyPI; do not substitute an unverified package with the same name.

## Supply your connection details

Set these variables in the environment from which you start your local agent:

```sh
export RAGWELL_BASE_URL="https://your-ragwell-api.example"
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

The key prompt hides typing. Do not paste it into a conversation, configuration
example, issue or Git file. These variables apply to processes launched from this
terminal; a separately opened desktop app may not inherit them.

## Choose your agent and try a question

Continue with [Codex](connect/codex.md), [Claude Code](connect/claude-code.md), or
[another local MCP client](connect/other-mcp.md). After connecting, the agent should
discover `ragwell_search`. Ask:

> Using the documents in Ragwell, explain how I request leave. Show the supporting sources.

Expect supporting passages and filenames with available line/page/offset references.
Check them against the documents in Ragwell. Empty results can mean the project
is not ready or the question needs refinement; they do not prove there is no rule.

A successful test search consumes usage. The local connection advertises its tool
before validating the key; tool discovery alone does not establish API access.

## Disconnect

Remove or disable the Ragwell MCP entry in your agent. Revoke its dedicated key
in Ragwell to stop API access even if another process retains the old configuration.
When replacing an expired key, update the environment and restart the local agent.
See [troubleshooting](troubleshooting.md) for common problems.
