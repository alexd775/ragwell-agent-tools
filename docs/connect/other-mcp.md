# Connect another MCP client

The pilot exposes MCP over local stdio. A client must start the installed
`ragwell-agent-tools` executable and supply `RAGWELL_BASE_URL`, `RAGWELL_PROJECT_ID`
and `RAGWELL_API_KEY` through its process environment or credential configuration.

[The generic descriptor](../../integrations/generic/stdio.json) describes those
requirements; it is not an importable configuration format for every host. Follow
your client's own setup and credential instructions. Do not paste credentials into
a conversation, URL or committed project file.

After setup, verify that `ragwell_search` is discovered and make one sample search.
Check that the returned evidence and source coordinates are visible and that a
revoked key stops searches. Refer to [compatibility](../compatibility.md); unnamed
clients remain unverified until their installed configuration and tasks are tested.
