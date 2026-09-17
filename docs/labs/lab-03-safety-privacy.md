# Lab 03: Privacy and hostile input

## Objective

Verify that privacy minimization and prompt-injection defenses remain active
before routing and response generation.

## Path

1. Run **PII redaction** and confirm redaction markers appear in the summary.
2. Confirm raw PII is absent from the coach trace and response.
3. Run **Prompt injection defense**.
4. Confirm the hostile instruction is detected and ignored.
5. Confirm the input cannot select a privileged queue.

## Check

Only synthetic identifiers may be used. Never paste a real SSN, phone number,
email address, address, or case number into the exercise.
