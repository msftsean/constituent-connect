# Spec Kit Analysis: Maryland Constituent Connect

## Constitution alignment

- Non-emergency scope, emergency exit, grounded response, privacy minimization, human approval, synthetic data, and evaluation gates are represented in the specification and plan.
- Bounded agent authority is explicit.
- Emergency, privacy, routing, disclosure, and approval decisions are deterministic.
- Draw.io and Fluent 2 design requirements are represented in the constitution, plan, and tasks.

## All Clear pattern alignment

| Pattern | Constituent Connect application |
| --- | --- |
| Hero scenario | License replacement plus tax-registration cross-agency inquiry |
| Canonical terms | `CONTEXT.md` |
| Three stages | Listen → Route → Respond |
| Deterministic stage | Safety/Privacy Engine and Routing Engine |
| Bounded action | Cited draft; approved synthetic case |
| Visible terminal state | Drafted, clarification, emergency exit, escalated |
| Participant progression | Local app → orchestration → safety → retrieval/routing → approval → Azure → eval |
| Coach visibility | Redaction, evidence, route confidence, trace, safety result, evaluation score |

## Consistency findings

- The specification and data model use consistent terms after adopting `CONTEXT.md`.
- The API supports intake, response, approval, case, and evaluation flows.
- The task list includes zero-generative-call gate tests and authority-boundary tests.
- The emergency boundary remains distinct from All Clear's dispatch-oriented incident domain.
- The existing local implementation is a foundation; Azure infrastructure remains intentionally incomplete.
- AI assistance disclosure, correction capture, measurable thresholds, and deterministic engine authority are now explicit requirements.

## Required implementation follow-through

1. Add drift tests enforcing canonical terms.
2. Prove the Safety/Privacy and Routing Engines make zero generative calls for gates.
3. Add the progressive Lab 00-06 structure.
4. Surface the Draw.io diagram in the architecture documentation.
5. Build the participant and coach web experiences to All Clear's delivery quality.

## Reconciliation status

The original analysis was stale. The following contradictions were resolved before implementation:

- Added FR-016 and FR-017 for AI disclosure and correction signals.
- Standardized the workshop path to Lab 00-06 (seven labs).
- Clarified that agents orchestrate bounded deterministic Safety/Privacy and Routing Engines.
- Added CC-050 through CC-056 for disclosure, correction capture, drift/authority tests, measurable gates, OpenAPI reconciliation, and telemetry/retention.

Implementation may proceed against the reconciled tasks.
