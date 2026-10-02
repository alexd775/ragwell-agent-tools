# Report a security issue

Do not disclose credentials, private document/query text, tenant details or an
exploit involving customer data in a public issue. Use GitHub's private vulnerability
reporting for this repository if enabled; otherwise contact the Ragwell operator
through an existing private channel to arrange disclosure.

The first pilot is local stdio and read-only. The API checks current project grants
on every search. Local configuration contains a scoped credential; never share it
in chat, tool arguments, URLs, committed files or diagnostic output.

Source text is untrusted. A skill improves agent behavior but does not enforce
permissions or guarantee a model resists every malicious document. Read-only
retrieval can disclose permitted knowledge to the selected agent provider and
consume account usage. Hosted OAuth, writes and source expansion are not part of
the initial pilot.

Report the package/client versions, sanitized error code, relevant operation and
request ID where available. Arrange private transfer of any sensitive reproduction
material rather than attaching it to a public issue.
