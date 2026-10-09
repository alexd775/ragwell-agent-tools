# How the agent tools work

Ragwell retrieves authorized evidence from a project. The user's agent writes the
explanation. This package does not generate answers on the Ragwell server or
grant access by itself.

## Local connection

The agent starts the MCP stdio adapter with a configured API origin, project and
dedicated API key. The adapter uses the published Ragwell Python SDK; it needs no
backend checkout or database. Model tool arguments cannot change those connection
settings.

Current-grant discovery controls which tools are offered. Every search and source
read is still authorized by the API. Discovery failure does not fall back to
broader inventory or previously cached authority. The local connection check
does not make a metered search.

## Hosted connection

The supported hosted beta routes use Ragwell account linking and consent to one
project. They require no local package or Ragwell API key. The hosted service
reuses the canonical tool definitions while enforcing authorization, source
access, accounting and credential lifecycle centrally. Hosted OAuth credentials
are not passed through to the local API-key adapter.

## Evidence and bounds

Search preserves document, version, generation and chunk identities, citations
and evidence/context distinctions. Supporting-source reads use a reference from
the same connection's search and retain its exact version and generation. They
do not provide arbitrary document browsing or bulk export.

Queries, result counts, source slices, deadlines, concurrency and output are
bounded. A metered search is one attempt and is never automatically replayed.
Returned source text remains untrusted content; a skill guides model behavior
but cannot enforce server policy or guarantee injection resistance.

See the [tool reference](tools.md) for schemas and behavior, and
[compatibility](../compatibility.md) for actual tested clients and limitations.
Uploads, deletion, synchronization and automatic memory are outside these tools.
