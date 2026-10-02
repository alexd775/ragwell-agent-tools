# ADR 0001 Public tools and retrieval boundary

Status: accepted direction. Date: 2026-10-02.

## Context

Ragwell needs integrations people can use directly in Codex, ChatGPT Work, Claude
and other agents. Alex selected a separate public repository and created this one
with an MIT license. A published Python SDK already supplies machine HTTP access.

## Decision

Maintain an independently released public package containing curated MCP tools,
one canonical workflow skill, host-specific installation overlays, ordinary-user
guides and synthetic examples. The local pilot consumes the published SDK and
exposes search only. The backend remains authoritative for current permission,
tenant/project scope, retrieval, usage and lifecycle. The agent generates any
explanation; this package does not introduce server answer generation.

Local clients use a dedicated scoped API key and explicit project. Hosted OAuth
and simpler onboarding are planned, with grant/topology decisions before building
the hosted service. Source expansion/discovery need backend contract improvements.
Writes/sync/memory are deferred until separately selected.

## Alternatives and consequences

An SDK example alone would mix package ownership with the SDK's application-facing
scope. Independent implementations per host would duplicate tool and credential
behavior. The shared package instead requires visible SDK/API/protocol compatibility
and independent installed-artifact tests. A skill alone supplies no execution or
access enforcement. Host testing remains separate from protocol documentation.

## Rollout and reversal

Follow the [plan](../plan.md): local proof, supported read access, hosted account
linking, and user-qualified beta distribution. Reconsider investment if tasks do
not benefit, citations fail, setup prevents repeat use, or hosted authority/operation
cannot meet Ragwell's existing boundaries. The REST API and SDK remain independently
usable.
