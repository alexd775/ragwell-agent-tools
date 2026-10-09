# Try Ragwell with sample documents

Upload the four ordinary fictional documents in the
[starter pack](../starter/README.md) and wait until they are ready. Connect that
project using your hosted agent guide or a dedicated local search key. Each
search consumes usage.

| Ask your agent | Check the result |
|---|---|
| Using Ragwell, explain how I request leave and show the sources. | The handbook says staff portal, five working days, manager approval, and checking approval before booking. |
| Compare the 2025 and 2026 travel policies in Ragwell. Cite each changed rule. | Approval changes from every trip to trips over EUR 200; claims change from 30 to 14 days; receipts change from EUR 25+ to every claim. Effective dates and archived/current status appear in the sources. |
| Find our project decisions about permissions and search retries in Ragwell. What constraints apply to a proposed automatic retry? | Project-scoped central checks, caller cannot expand authority, and a timeout does not authorize replay. |

The optional [hostile-source exercise](../sample-knowledge/injection-exercise.md)
is separate from the starter pack and deliberately contains malicious instructions. Observe
whether the agent treats them as source text and preserves the user's task.
Deterministic adapter tests cannot certify a model's injection behavior; record it
separately during real host qualification.
