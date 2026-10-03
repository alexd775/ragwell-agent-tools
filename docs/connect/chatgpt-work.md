# Ragwell in ChatGPT Work

Hosted account linking is implemented for beta qualification but is not enabled
or user-qualified yet. This guide describes the coming connection flow; it is not
a claim that Ragwell is currently installable in ChatGPT Work. Keep your Ragwell
API key out of chat. Local Codex setup does not configure Work.

Once an invited hosted connection is enabled, you will:

1. Add Ragwell using the beta connection supplied with your invitation.
2. Sign in on Ragwell, select one project and review the requested read access.
3. Approve the connection and return to your agent.
4. Ask a question from the [sample workflows](../../examples/workflows/README.md)
   and check its source citations.

Your agent provider receives retrieved text and citations. Searches use your
workspace allowance. A connection lasts up to 30 days; review and disconnect it
in Ragwell's **Agent connections** page. Disconnecting prevents future access;
it cannot remove text your provider already received. Reconnecting requires
another approval. Use only the synthetic beta documents.

OpenAI's authenticated remote plugins use OAuth rather than a custom Ragwell API
key. This beta uses predefined public clients with exact callbacks, so the
maintainer prepares the connection before inviting testers. Account/workspace
eligibility and administrator requirements still need live qualification.
[Plugin authentication](https://developers.openai.com/plugins/build/auth).

The [delivery plan](../project/plan.md) tracks live linking, privacy/operations
checks and user testing before this becomes a fully verified installation guide.
