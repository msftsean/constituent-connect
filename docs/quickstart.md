# Fresh-user quickstart

This workshop is a local, synthetic demonstration of a human-reviewed constituent
communications workflow. It is not a production service. Do not enter real
constituent information, credentials, confidential agency material, or live
emergency details.

## 1. Get oriented

- Read the [participant runbook](participant-runbook.md).
- Open the [coach site](coach-site.html) for the session map.
- Review the [architecture page](architecture.html) and its
  [editable Drawio source](../design/constituent-connect-architecture.drawio).

## 2. Start safely

From the repository root, use Python 3.11 or newer:

```bash
python -m pip install -e .
python scripts/readiness.py
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python scripts/run_local.py
```

On systems with GNU Make, `make test` and `make run` are equivalent. To use the
React development experience, run `npm --prefix frontend ci` and
`npm --prefix frontend run dev` in a second terminal, then open forwarded port
5173. The Vite app uses relative API calls through the checked-in proxy; do not
configure browser-facing `localhost` API URLs in Codespaces.

Open the forwarded port 8000 URL in Codespaces, or <http://127.0.0.1:8000>
when running locally. Confirm that the page identifies the local synthetic mode
before entering a sample inquiry.
The approve button uses the generated local approver token from the untracked
`.env` created by `scripts/readiness.py`; no Azure credentials are required.
That local workshop identity is a training-only assertion, not production
authentication.

## 3. Follow the participant path

1. [Lab 00: Orientation and safety](labs/lab-00-orientation.md)
2. [Lab 01: Start and inspect](labs/lab-01-start.md)
3. [Lab 02: Grounded routine response](labs/lab-02-routine-response.md)
4. [Lab 03: Privacy and hostile input](labs/lab-03-safety-privacy.md)
5. [Lab 04: Ambiguity and emergency boundary](labs/lab-04-boundaries.md)
6. [Lab 05: Approval and cross-agency work](labs/lab-05-approval-handoff.md)
7. [Lab 06: Configuration and evaluation](labs/lab-06-configuration.md)

Every lab uses synthetic examples. Keep the explicit boundaries in view:
emergency handling gives guidance and human escalation only, the system never
dispatches, and a case cannot be created before human approval.

## 4. Capture evidence

Run the safe smoke-test instructions in
[concurrent smoke-test evidence](concurrent-smoke-test.md). The committed JSON
is synthetic evidence only; copy the template for a new run rather than adding
real data.

## 5. Finish the session

Run the commands above followed by
`PYTHONPATH=src python -m constituent_connect.eval_runner`, inspect
`reports/evaluation.html`, and use the
[evaluation scorecard](evaluation-scorecard.md) to record observations. Stop
the local server when the workshop ends. For reset and recovery steps, see
[workshop readiness](workshop-readiness.md).
