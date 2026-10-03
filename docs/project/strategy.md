# Agent tools strategy

Direction accepted by Alex on 2026-10-02. This repository makes Ragwell knowledge
usable in the agents people already use, without requiring an application of their
own. The external agent composes explanations; Ragwell supplies authorized evidence,
provenance and usage accounting.

The first local candidate is implemented; see [qualification](qualification.md)
for passing local gates and unrun live/client checks, and
[ADR 0001](adr/0001-public-tools-and-retrieval-boundary.md) for the accepted boundary.

The intended everyday user can upload documents and use an assistant but should
not need to edit manifests or install Python. Local coding-agent setup is the first
experiment; hosted sign-in-and-connect onboarding is the longer-term product target.

## Shared tools and separate installation guides

Keep one curated MCP implementation, one canonical evidence skill and small client
configuration/package overlays. Consume the independently published Python SDK.
The backend owns policy, tenant/project scope, retrieval, source access and budgets;
this repository owns bounded projection, agent workflows, user guides and client
qualification. Documentation should publish from this source through Ragwell's
public docs site rather than diverging into independently edited copies.

Use a dedicated API key for local agents. Hosted ChatGPT plugins use OAuth account
linking; a raw Ragwell key cannot be supplied through the documented remote-plugin
authentication. The accepted beta design uses user-bound grants, one-project
consent and current membership checks. The Personal custom-MCP flow and Claude web
Free personal pilot passed guarded live tasks/source reads and disconnect/reconnect.
Managed workspaces and other hosted surfaces require their own qualification.
Existing organization-owned service accounts keep their separate lifecycle.
[OpenAI authentication](https://developers.openai.com/plugins/build/auth).

## Workflows and stages

Prove three useful workflows: explain a process with sources, compare policies with
evidence for each change, and consult project decisions before proposing a change.
Use synthetic documents during beta and distinguish source support from inference.

The [plan](plan.md) separates local proof, fuller supported read access, hosted
account linking and nontechnical onboarding/distribution. MCP support alone is
not sufficient: useful evidence, citations, setup friction and repeat usage determine
whether the investment succeeds. Qualify each client/surface/version separately.

For the hosted stage, aim for at least four of five nontechnical testers reaching
a useful cited result within 15 minutes without live coaching. This is a proposed
acceptance target; measure actual results and revise the experience if necessary.

Keep uploads, deletion, automatic memory and synchronization outside this first
direction. Select each later workflow from concrete demand with explicit authority,
idempotency, lifecycle and budget decisions. Public repository visibility does not
authorize a production endpoint or waive Ragwell's release gates.
