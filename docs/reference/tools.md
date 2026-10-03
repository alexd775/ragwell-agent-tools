# Local tool contract

`ragwell_search` accepts only `query` (nonblank, at most 2000 characters) and `k`
(integer 1–5, default 5). Unknown fields and type coercion are rejected before HTTP.
Origin, key and project come from process configuration; there is no filter,
tenant override, reranker selection or project-switch argument in the pilot.

Results contain project/retrieval identity and matches with document/version/chunk
IDs, generation ID when supplied by the API, rank, scores, source filename, representation version, original singular
citation when present, and ordered source parts. Text appears in parts rather than
being duplicated as full chunk content. Evidence, context and separators keep
their original kinds and available page/line/span coordinates. No generation ID or
canonical URL is invented. Older API responses remain searchable but report
`source_expansion_available: false`. A true flag means a reference can be used;
it does not establish `document:read` permission. Only these
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

One request runs per process; simultaneous calls return `busy`. Validation failures
do not consume the local attempt budget; admitted failures/cancellations do. The
SDK makes one metered HTTP search attempt without additional adapter retries.
The local budget is a process safeguard, not an authoritative account spend limit.

## Bounded source expansion

`ragwell_fetch_source` accepts UUIDs `document_id`, `document_version_id`,
`generation_id` and `source_id`, plus `offset` (zero-based character offset, default
0, maximum 2147483646) and `limit` (default 1500, range 1–4000). The offset bound
keeps the API's one-based PostgreSQL substring position within its integer range.
All four IDs must match a reference
actually returned by search in the same connection. The process keeps at most 512
references; oldest references can become unavailable. IDs from omitted matches or
parts confer no local access. This admission rule supplements server authorization.

The adapter calls the published SDK's existing source reader. Every API call
requires current `document:read`. The response's document/version/generation/source
IDs, requested range, text length and continuation must match before any text is
returned. Only source content and reviewed identity/coordinate fields are exposed;
structural units and future fields are omitted. This read adds no search usage.
The SDK can make bounded safe-GET retries; the adapter does not replay failed tool
invocations. Cancellation and the process deadline propagate through the SDK.

Source output uses the same full serialized byte budget as search. If shortened,
`end_offset` and `next_offset` identify the end of the text actually delivered and
`truncated` is true. These are coordinates of this new source slice; original
search citations remain untouched. Page/offset coordinates support citations;
line numbers are not inferred. Do not treat a slice as the whole document.

At most 20 source-read attempts are admitted per process, separately from the
search budget. Unseen/substituted references fail locally. Missing retained
generations, invalid ranges or deletion conflicts return `source_unavailable`;
revocation/authentication and missing scopes retain explicit failure codes. None
of these failures returns source text or claims uncertain search charges.

Both curated tools are advertised statically until machine-capability discovery
is implemented. Visibility and a successful search do not establish source-read
permission. The API rechecks authority on every read.
