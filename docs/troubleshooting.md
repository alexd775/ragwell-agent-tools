# Troubleshoot your Ragwell connection

## Hosted ChatGPT beta

| What you see | What to do |
|---|---|
| Custom MCP setup is unavailable | Check the beta invitation and ask the maintainer about your account's supported route. Personal plugin qualification does not establish managed-workspace availability. |
| OAuth discovery fails or shows another callback | Check the exact beta `/mcp` URL and public client ID in the [ChatGPT guide](connect/chatgpt-work.md). Leave the client secret empty. Report the failing step; do not invent a callback or paste credentials. |
| Ragwell says the request expired | Restart from ChatGPT's **Continue connecting app** control. Pending approval lasts 10 minutes and creates no grant after expiry. |
| The wrong project/account appears | Cancel, open the intended browser profile/account and restart. Check the selected project before approving. |
| ChatGPT asks to reconnect | Check Ragwell's **Agent connections**. If disconnected or expired, reconnect from the plugin and approve the intended project/read access again. |
| A search reports an embedding timeout | Stop; usage may have been recorded. Deployment warm-up is an accepted beta limitation. Decide deliberately whether a separate new attempt is needed; never automatically replay. |

## Local agents

| What you see | What to do |
|---|---|
| Ragwell is missing or the process cannot start | Check the full executable path and the three required environment variables. Start the agent from the same environment. |
| `authentication_failed` | Replace an expired/revoked key in credential settings and restart. Never send the key in chat. |
| Claude says its OAuth access token has expired, even though `/mcp` connects | Run `claude auth login` again and complete the browser sign-in. A saved login can still contain an expired provider token; this error occurs before a Ragwell search. |
| `access_denied` or no tools listed | Check that the key has `retrieval:search` for the configured project. Source reads also require `document:read`. Existing key scopes are immutable; create a replacement, update local settings and restart. |
| `project_unavailable` | Check the configured project ID and its current availability/access in Ragwell. |
| Successful search with no matches | Check that documents are ready and try a more specific question. |
| Truncated result | Ask for a bounded supporting source slice when `ragwell_fetch_source` is available, or view the source in Ragwell. |
| `discovery_unavailable`, `discovery_timeout` or a tool-list error | Run `ragwell-agent-tools --check`. Verify API/package compatibility and connectivity. Discovery makes no search; unavailable discovery never enables tools. |
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
