# Local tool contract

`ragwell_search` accepts only `query` (nonblank, at most 2000 characters) and `k`
(integer 1–5, default 5). Unknown fields and type coercion are rejected before HTTP.
Origin, key and project come from process configuration; there is no filter,
tenant override, reranker selection or project-switch argument in the pilot.

Results contain project/retrieval identity and matches with document/version/chunk
IDs, rank, scores, source filename, representation version, original singular
citation when present, and ordered source parts. Text appears in parts rather than
being duplicated as full chunk content. Evidence, context and separators keep
their original kinds and available page/line/span coordinates. No generation ID or
canonical URL is invented; bounded source fetch is a later stage. Only these
reviewed fields are forwarded: fields added by a later compatible SDK release are
omitted until the adapter projects them deliberately, rather than failing searches.

The MCP result contains structured JSON and an equivalent text fallback for older
hosts. The output budget counts both serialized representations, excluding the
outer JSON-RPC envelope. Part text starts with a 1500-character cap and at most
32 source parts per match; the full byte limit can shorten excerpts further or
omit matches. `original_text_chars`, truncation flags and omission counts make
those limitations explicit. Original offsets are never rewritten.

Errors set `isError` and carry stable adapter codes and actionable messages.
API request IDs are forwarded only when UUID-shaped; raw API/provider error text
is never returned. Deadlines/transport failures mark uncertain usage. Cancellation
propagates locally and frees admission; it does not prove remote usage was refunded.

| Setting | Default and bound |
|---|---|
| `RAGWELL_BASE_URL` | Required HTTPS origin, no userinfo/path/query/fragment |
| `RAGWELL_PROJECT_ID` | Required project UUID |
| `RAGWELL_API_KEY` | Required credential, omitted from representations |
| `RAGWELL_TIMEOUT_SECONDS` | 20; finite, greater than 0 and at most 120 |
| `RAGWELL_MAX_OUTPUT_BYTES` | 24000; 2048–65536 |
| `RAGWELL_MAX_SEARCHES` | 50 attempts per process; 1–10000 |
| `RAGWELL_ALLOW_LOCAL_HTTP` | `false`; `true` permits loopback HTTP for test peers only |
| `RAGWELL_DEBUG_LOG` | Unset; an absolute, writable file path enables local diagnostics |

The diagnostics file receives one JSON line at startup (package, SDK and MCP
versions) and one per failure: adapter code, exception type and cause type, code
locations, SDK operation, HTTP status, UUID request ID, and output-model field
locations for invalid responses. It never records exception messages, queries,
source text, response values or credentials. It is created with owner-only
permissions where supported. An unwritable path stops startup with a configuration
error; later write failures are skipped and never change a tool result.

One search runs per process; simultaneous calls return `busy`. Validation failures
do not consume the local attempt budget; admitted failures/cancellations do. The
SDK makes one metered HTTP search attempt without additional adapter retries.
The local budget is a process safeguard, not an authoritative account spend limit.
