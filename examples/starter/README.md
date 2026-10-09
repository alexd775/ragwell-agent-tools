# Try Ragwell with fictional documents

Use this small example to connect a Ragwell project and check your agent's answers
against their sources. It needs a Ragwell beta invitation and a supported agent
connection.

## Prepare the documents

1. Download [starter-documents.zip](starter-documents.zip) and unzip it.
2. Create a Ragwell project named **My Ragwell example**.
3. Upload the four `.md` files, then wait until they are ready for search. Upload
   the documents themselves, not the ZIP.

The pack contains a fictional employee handbook, archived 2025 and current 2026
travel policies, and project decisions. It contains no real company or employee
information.

## Connect your agent

Choose [ChatGPT web](../../docs/connect/chatgpt-work.md),
[Claude web](../../docs/connect/claude-web.md),
[Codex CLI](../../docs/connect/codex.md) or
[Claude Code](../../docs/connect/claude-code.md).

The hosted browser routes use Ragwell sign-in and project approval. They require
no API key, Python or terminal. Local coding agents use a dedicated project-scoped
API key and terminal setup. Follow the guide for your actual account surface;
the [compatibility page](../../docs/compatibility.md) records the tested routes.

## Ask and check

> Using Ragwell, explain how I request leave. Read the supporting source and show
> its filename and original coordinates. If a tool fails, stop without replaying
> the search.

Open `handbook.md` in Ragwell or the downloaded files. Check that the cited
passage supports the answer. Try the
[policy-comparison and project-decision questions](../workflows/README.md) next.
Filenames and section/line/character coordinates can be valid citations without
a clickable link; do not accept a fabricated source URL.

Searches consume Ragwell usage and retrieved text goes to your selected agent
provider. If a search fails, stop and follow
[troubleshooting](../../docs/troubleshooting.md) before deciding whether to make
a separate new attempt.

To stop future access, follow your connection guide's disconnect instructions.
Disconnecting cannot retract text already received by your agent provider.
