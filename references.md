# Sources and claim boundaries

Read on 17 October 2026. Links are primary papers, specifications, official documentation, or firsthand engineering accounts. Living documentation is not an archived snapshot. No claim is made that the example ran on the website archive date.

## AWS idempotent APIs

- Source: [AWS idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/).
- Version/date: 2021-01-15 announcement.
- Read: Retrying side effects, caller identity, atomicity, semantic replay, late requests, same ID with different intent.
- Use and limits: Caller intent and retained request identity matter. The example adapts these principles to one local database; AWS results are not reproduced.

## AWS retry policy

- Source: [AWS retry policy](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/).
- Version/date: 2019-12-05.
- Read: Timeouts, retries, backoff and jitter sections.
- Use and limits: Retry amplification and bounded policies; article does not prescribe provider-specific timeout constants.

## HTTP semantics RFC 9110

- Source: [HTTP semantics RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2).
- Version/date: 2022-06.
- Read: Sections 9.2.1 and 9.2.2.
- Use and limits: Intended effect defines idempotency; arbitrary POST cannot automatically be retried.

## SQLite transactions

- Source: [SQLite transactions](https://sqlite.org/lang_transaction.html).
- Version/date: Live documentation, retrieved 2026-10-17.
- Read: Transactions, one writer, IMMEDIATE and SQLITE_BUSY.
- Use and limits: BEGIN IMMEDIATE starts a write transaction. Lock timeout does not imply throughput or eliminate external side-effect gaps.

## Stripe idempotent requests

- Source: [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests).
- Version/date: Live documentation, retrieved 2026-10-17.
- Read: Full short API reference, especially API v1 semantics.
- Use and limits: Article explicitly scopes cached status/body and retention discussion to API v1. API v2 differences are not projected backwards.

