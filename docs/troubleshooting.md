# Troubleshoot your Ragwell connection

| What you see | What to do |
|---|---|
| Ragwell is missing or the process cannot start | Check the full executable path and the three required environment variables. Start the agent from the same environment. |
| `authentication_failed` | Replace an expired/revoked key in credential settings and restart. Never send the key in chat. |
| `access_denied` | Check that the key has `retrieval:search` for the configured project. |
| `project_unavailable` | Check the configured project ID and its current availability/access in Ragwell. |
| Successful search with no matches | Check that documents are ready and try a more specific question. |
| Truncated result | Ask a narrower question or view the source in Ragwell. Source expansion is unavailable in this pilot. |
| `quota_exceeded` | Review usage/limits in Ragwell before making further searches. |
| `rate_limited` | Wait for the reported interval before deciding whether another search is needed. |
| `busy` | Wait for the existing search to finish or cancel it in your agent. |
| `local_budget_exhausted` | The local process has attempted its configured number of searches. Review usage before restarting; restarting does not reset account quotas. |
| `search_timeout` or `connection_failed` | Check service/connectivity. Usage may have been recorded; do not automatically replay. |
| `invalid_response` or `search_failed` | Check compatible package/API versions and report the sanitized error code. To capture details, set `RAGWELL_DEBUG_LOG` to an absolute file path, restart the agent and reproduce once. |

For a public issue, include client/version, OS, package version, failing step,
sanitized error code and request ID if present. Diagnostics-file entries contain
no query, source or credential values and may be attached. Omit keys, document/query text,
raw protocol dumps and configuration containing secret values. Report account or
private-data problems through the Ragwell operator's private support channel.
