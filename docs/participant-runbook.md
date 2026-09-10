# Participant Runbook

## Goal

Demonstrate a safe, human-reviewed path from a synthetic inquiry to a synthetic case. Never enter real constituent data, credentials, or confidential agency material.

## Lab 1: Start the local application

1. Use Python 3.11 or newer.
2. Run `make test`.
3. Run `make run`.
4. Open `http://127.0.0.1:8000` and confirm the local synthetic banner.

## Lab 2: Routine grounded response

1. Select **Routine license replacement**.
2. Process the inquiry.
3. Confirm the proposed `professional-licensing` route.
4. Open the citation and review the public excerpt.
5. Confirm the response is pending human approval.

## Lab 3: Privacy and hostile input

1. Run **PII redaction** and verify the summary contains redaction markers.
2. Confirm raw PII is absent from the coach trace and response.
3. Run **Prompt injection defense**.
4. Confirm the hostile instruction is detected, ignored, and cannot select a privileged queue.

## Lab 4: Ambiguity and emergency boundary

1. Run **Ambiguous permit** and confirm the system asks a clarifying question.
2. Verify a case cannot be created.
3. Run **Emergency boundary**.
4. Confirm call-911 guidance, human escalation, no routine route, and the explicit no-dispatch message.

## Lab 5: Human approval and cross-agency work

1. Run **Cross-agency business move**.
2. Inspect primary and secondary services.
3. Edit the response without adding promises.
4. Approve it as the human reviewer and create the case.
5. Confirm separate synthetic work items share only the redacted summary.

## Lab 6: Bring it home through configuration

1. Add one synthetic agency to `data/agencies.json`.
2. Add three synthetic services with keywords and distinct queues to `data/services.json`.
3. Add at least one approved synthetic public passage for each service.
4. Add sample inquiries to `data/inquiries.json`.
5. Restart the server, process each sample, and run `make test && make eval`.

Do not change routing behavior based on protected characteristics, neighborhood, language, or channel. Corrections belong in tests and reviewed configuration, not as unreviewed policy.

## Evaluation evidence

Run `make eval`. Review `reports/evaluation.json` for machine-readable checks and `reports/evaluation.html` for the summary. A critical failure blocks the workshop release gate.
