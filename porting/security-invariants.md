# 🛡️ Security Invariants

**Revision:** 2026-09-17 · **Status:** 🟩🟩🟩🟩⬜ port blockers defined

## Deterministic gates

- Emergency, PII, prompt-injection, service ownership, confidence, disclosure scope, and approval gates are deterministic.
- Emergency decisions make zero generative-model calls.
- Generative agents may propose, summarize, retrieve, translate, or draft; they cannot override deterministic gates.

## PII containment

Raw constituent content must not appear in normal browser/API responses, logs, traces, reports, work items, analytics, or errors. Redact formatted/unformatted SSNs, phone numbers, email addresses, street addresses, DOBs, license IDs, benefit/tax/case/account IDs, payment cards, bank data, passwords, tokens, one-time codes, credentials, secrets, and supported-language variants.

## Approval and cases

Reviewer identity is resolved server-side. Client-supplied reviewer names are untrusted. Case creation is blocked until approval, emergency approvals are rejected, duplicate case creation returns the same case, and every consequential decision records an immutable audit event.
