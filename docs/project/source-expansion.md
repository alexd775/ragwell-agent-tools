# Source expansion candidate

The following is the historical 2026-10-02 local qualification record. SDK 0.2.1
has since been published, hosted tools CI passed, and source expansion passed
seven guarded real tasks; see [2026-10-03 host evidence](source-host-qualification.md).
The old candidate digest below remains distinct from the published SDK wheel.

Unpublished `ragwell-agent-tools` 0.1.0a2 adds `ragwell_fetch_source` alongside
search. It uses the existing public SDK 0.2.0 source reader; no private API checkout,
backend import, new HTTP client or unpublished SDK dependency is needed.

The API prerequisite is machine contract `2026-10-02.1`: search hits carry
`generation_id` and source previews carry document/version identity. Tool reads
accept only references returned in the same connection and verify all identities,
range length and continuation. References and source attempts are bounded. Reads
require `document:read` and add no search usage. See the
[tool contract](../reference/tools.md) for precise limits and failure behavior.

With SDK 0.2.0, older APIs remain searchable without expansion. SDK 0.2.1 is a
separately prepared candidate with typed identity fields and requires the updated
API before adoption. Tool discovery is static until capability discovery exists;
it does not validate the key or prove either permission.

The source suite passed 112 tests with format/lint/strict typing, guide/template
checks and canonical skill validation on macOS arm64, Python 3.12.14. The final
wheel passed all 112 tests with published SDK 0.2.0 outside project checkouts on
Python 3.11.16, 3.12.14, 3.13.11 and 3.14.0. Both final candidate wheels together
passed the same 112 tools tests on Python 3.12.14 with SDK 0.2.1. Protocol tests
exercise discovery, search and source reads in both supported stdio modes.

Tools wheel SHA-256:
`f8893b190ab472bfef00f9185927dc27c9dcd9cc6d2f0bbf8f67f2e987fcb699`.
SDK 0.2.1 candidate wheel SHA-256:
`3089cac40559b0459746d1287ca627cf15beb9b71d45f46e915f34e904a7e688`.

The API project separately passed 310 deterministic tests, 14 migrated source/
retrieval integration tests, generated-consumer checks and all eight cross-repo
HTTP golden scenarios. This qualification uses synthetic documents and local
services. Hosted CI and other operating systems remain unverified for this change.

Earlier search-pilot Codex/Claude
task evidence does not qualify this new source tool or changed skill. Deploy the
updated beta API and qualify source expansion/citations in those exact hosts
before describing expanded host support as tested. Hosted account linking,
interactive onboarding and package publication remain separate gates.
