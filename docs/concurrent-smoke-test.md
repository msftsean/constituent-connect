# Safe synthetic concurrent smoke test

This procedure checks that several **synthetic** routine inquiries can be
processed concurrently without weakening approval or emergency boundaries. It
is not a load test and must not target a deployed service or contain real
constituent data.

## Procedure

1. Run `python scripts/readiness.py`, then start the local server with `make run`.
2. Use only the synthetic sample inquiry IDs already provided by the
   application. Do not paste real messages, identifiers, or credentials.
3. Submit a small batch of concurrent routine requests (the committed evidence
   uses four workers and eight synthetic requests).
4. Confirm every result has a synthetic run/request ID, a draft status, and no
   case ID before approval.
5. Confirm the result set has no emergency dispatch action, no raw PII, and no
   data from another request.
6. Stop the server and retain only the redacted JSON evidence.

The checked-in evidence is a safe example/template, not a claim about a
production deployment. Copy
[the template](evidence/concurrent-smoke-test.template.json), fill it with
synthetic values, and record the command and checks performed.

## Boundary assertions

- `dispatch_actions` must always be an empty array.
- `approval_required` must be `true` for every draft.
- `created_case_ids` must be empty unless a human approval step was explicitly
  performed and recorded.
- Evidence must not include request bodies, raw PII, credentials, or external
  endpoints.
