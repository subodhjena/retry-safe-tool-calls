# Local tool contract

| Property | Demonstration behavior |
| --- | --- |
| Scope | Authorized tenant plus operation ID |
| Same intent | Replay stored creation receipt |
| Changed arguments | `IntentConflict`, no additional write |
| New intent | New operation ID, even for the same subject |
| Atomic unit | Task and replay response in one SQLite transaction |
| Concurrency | One SQLite writer, unique operation constraint |
| Retention | Indefinite; no cleanup implementation |
| Before-commit failure | Both writes rolled back |
| After-commit failure | Effect remains; retry finds stored result |
| External effects | None; not covered by this transaction |

The application must persist the operation ID before delivery and authorize
every request, including result replay. Do not let the model select a tenant or
treat the ID as a secret credential. This example accepts trusted caller inputs
and does not implement an authentication server.

Before adapting to an external service, specify downstream key scope, expiry,
parameter matching, status lookup, and recovery for uncertain outcomes. A local
outbox can preserve pending work; it does not make the downstream effect atomic
with the local database. Retry limits and backoff belong to the caller and are
intentionally outside this local transaction demonstration.
