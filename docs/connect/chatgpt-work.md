# Ragwell in ChatGPT

The invited beta connection passed source-based tasks in ChatGPT web's
**Personal** custom-MCP plugin flow on 2026-10-03. This guide follows that exact
flow. Your account must show the custom MCP option; managed workspaces, ChatGPT
Work and other installation routes have not been qualified. Ragwell is not yet
listed in a public agent directory.

You do not need a Ragwell API key, Python or a terminal for this hosted connection.
Use only synthetic beta documents. The [compatibility record](../compatibility.md)
describes the evidence and remaining limits.

## Prepare your Ragwell project

Sign in to Ragwell, choose a project and wait until its documents are ready for
search. For the first test, upload the fictional documents in
[starter pack](../../examples/starter/README.md). Remember that project's name
so you can select it during approval. If you use several browser profiles, open
ChatGPT and Ragwell in the profile with the intended Ragwell account.

## Add the beta plugin

In ChatGPT, open **Plugins → Personal → Add** and choose
**Create custom MCP server**. Enter:

| Setting | Value |
|---|---|
| Name | `Ragwell Beta` |
| Server URL | `https://beta.ragwell.dev/mcp` |
| Authentication | OAuth |

Open the advanced OAuth settings and let ChatGPT discover Ragwell's settings.
Select **User-Defined OAuth Client** and use the supplied beta settings:

| Setting | Value |
|---|---|
| Client ID | `ragwell-chatgpt-beta` |
| Client secret | Leave empty |
| Token endpoint authentication | `none` |
| Default scopes | `retrieval:search document:read` |
| Base scopes | `retrieval:search` |

These scope names let the connection search and read supporting passages. The
client ID is public configuration; it is not a secret or an API key. After
discovery, the callback must be exactly
`https://chatgpt.com/connector_platform_oauth_redirect`. If ChatGPT shows a
different callback or cannot discover the server, contact the beta maintainer
before continuing. Do not guess a replacement URL or supply a client secret.

Review ChatGPT's connection notice, create the plugin and choose
**Continue to Ragwell Beta**. Menu wording may change. If your account does not
offer this setup, ask the beta maintainer which route is available to you.

## Approve one project

On Ragwell's **Connect ChatGPT** page:

1. Check the signed-in account and workspace.
2. Select the project you prepared. Check the selection even if a project was
   already selected when the page opened.
3. Review search and supporting-source permissions, usage and the 30-day expiry.
4. Choose **Connect ChatGPT** and return to ChatGPT.

Your agent provider receives retrieved text and citations. Searches consume your
workspace allowance. Review your provider's account data controls before approval;
this test does not establish managed-workspace or enterprise data terms.

If the approval request expires, start again from the plugin's
**Continue connecting app** control. A pending Ragwell request lasts 10 minutes;
an expired request grants no access.

## Ask a question and check its sources

Open **Ragwell Beta → Try in chat**. With the sample documents, try:

> Using Ragwell, explain how I request leave. Read the supporting source and show
> its filename and original coordinates. If a tool fails, stop without replaying
> the search.

Check the answer against `handbook.md`. It should mention the staff portal,
five working days, manager approval and checking approval before booking travel.
Try the [policy comparison and project-decision questions](../../examples/workflows/README.md)
next. Ask the agent to read supporting sources and distinguish evidence from its
own inference. Retrieved text is untrusted content, including instructions inside
documents.

Expect filenames and available page/line/offset coordinates. The sample Markdown
files use offsets; a citation need not be a clickable link. Do not accept a made-up
source URL. An empty search is not proof that no policy exists.

## Disconnect and reconnect

In Ragwell, open **Agent connections**, choose **Disconnect** for ChatGPT and
confirm. The connection changes to **Disconnected or expired**. ChatGPT will
need to reconnect before making another request. Disconnecting stops future
access; it cannot remove text already received or saved by the provider.

To reconnect, open the Ragwell Beta plugin in ChatGPT and choose **Reconnect**.
Continue to Ragwell, check the account, project and read permissions, and approve
again. A new connection lasts up to 30 days. You can see its expiry in Ragwell;
the old disconnected entry can remain in the history.

If a search times out, usage may already have been recorded. Stop and review the
error before deciding on a separate new attempt. The beta has an accepted
deployment warm-up limitation; never automatically replay a metered search.
See [troubleshooting](../troubleshooting.md).

This is an operator-assisted beta setup, not a measured ordinary-user onboarding
result. The [compatibility summary](../compatibility.md) records the tested
surface, workflows and remaining client scope.
