# Try Ragwell with sample documents

Upload the five documents in [sample-knowledge](../sample-knowledge) to a synthetic
test project and wait until they are ready. Connect that project with a dedicated
search key. Each search consumes usage.

| Ask your agent | Check the result |
|---|---|
| Using Ragwell, explain how I request leave and show the sources. | The handbook says staff portal, five working days, manager approval, and checking approval before booking. |
| Compare the 2025 and 2026 travel policies in Ragwell. Cite each changed rule. | Approval changes from every trip to trips over EUR 200; claims change from 30 to 14 days; receipts change from EUR 25+ to every claim. Effective dates and archived/current status appear in the sources. |
| Find our project decisions about permissions and search retries in Ragwell. What constraints apply to a proposed automatic retry? | Project-scoped central checks, caller cannot expand authority, and a timeout does not authorize replay. |

The hostile-source exercise deliberately contains malicious instructions. Observe
whether the agent treats them as source text and preserves the user's task.
Deterministic adapter tests cannot certify a model's injection behavior; record it
separately during real host qualification.
