# Feature Specification: Maryland Constituent Connect

## Problem

Constituents often do not know which agency owns a service. Contact-center staff repeatedly interpret long or emotional messages, search multiple sites, rewrite standard answers, and transfer people between agencies. Inconsistent routing and unsupported responses increase effort and reduce trust.

## Users

- Constituent seeking a non-emergency service or answer.
- Contact-center agent reviewing an AI-generated summary and response.
- Agency specialist receiving a correctly routed case.
- Supervisor monitoring service quality, unresolved intents, and routing gaps.

## Primary scenarios

### Scenario 1: Multi-channel inquiry

A constituent submits a web, email, chat, or synthetic voice inquiry. The accelerator detects language, summarizes the need, removes unnecessary sensitive data, identifies intent and urgency, and proposes the responsible agency or program.

### Scenario 2: Grounded first-contact response

The accelerator retrieves approved public information, drafts a plain-language response with citations and next steps, and displays confidence. A human can approve or edit the response.

### Scenario 3: Cross-agency routing

An inquiry spans multiple agencies. The accelerator creates one constituent-facing explanation and separate agency work items without forcing the constituent to repeat the entire story.

### Scenario 4: Emergency boundary

The message suggests immediate danger, violence, medical crisis, fire, or another emergency. The accelerator stops the normal workflow, provides appropriate emergency guidance, and triggers a human escalation. It does not attempt emergency dispatch.

### Scenario 5: Bring-it-home configuration

A participant adds a synthetic agency, service taxonomy, public FAQ, and routing rule without changing application code.

## Functional requirements

- FR-001: Accept synthetic web, chat, email, and transcribed voice inquiries.
- FR-002: Detect language and generate a plain-language normalized summary.
- FR-003: Detect current emergency indicators deterministically, distinguish historical/negated/hypothetical/false-positive references, and exit the routine workflow with zero generative calls.
- FR-004: Minimize and redact unnecessary PII from normal API/browser responses, summaries, traces, reports, work items, analytics, errors, and model-call inputs where feasible.
- FR-005: Classify intent, service, agency, urgency, and confidence.
- FR-006: Retrieve approved public content and cite the supporting passages.
- FR-007: Draft a response appropriate to the selected channel and reading level.
- FR-008: Recommend a route, explain why, and identify alternatives when confidence is low.
- FR-009: Create one idempotent synthetic case record only after authenticated human approval.
- FR-010: Preserve the original message and an auditable transformation history.
- FR-011: Support cross-agency cases without duplicating or exposing unrelated sensitive details.
- FR-012: Ignore prompt-injection instructions in constituent messages and retrieved content.
- FR-013: Capture corrections and use them as evaluation signals, not unreviewed policy.
- FR-014: Expose trace, retrieval evidence, routing scores, safety checks, latency, and cost to coaches.
- FR-015: Run locally with synthetic data and provide Azure Developer CLI
  infrastructure definitions for a separately reviewed deployment.
- FR-016: Tell constituents when a response is AI-assisted, keep that disclosure visible in the approved response, and record the disclosure in the audit trail.
- FR-017: Capture human edits, approvals, rejections, and reroutes as evaluation signals without changing policy or routing configuration automatically.
- FR-018: Allow emergency responses to be rejected or escalated by an authenticated reviewer, but never approved as routine responses.
- FR-019: Keep cross-agency work items scoped so unrelated services, facts, attachments, PII, and agency details do not cross disclosure boundaries.

## Non-goals

- Emergency dispatch or replacement for 911.
- Final eligibility, legal, medical, enforcement, or complaint decisions.
- Accessing production case-management systems during the workshop.
- Processing confidential customer data.
- Fully autonomous outbound communication without a configurable approval gate.

## Success criteria

- Correct agency or service route in at least 90% of golden cases.
- Emergency recall of 100% on the critical synthetic test set, with measured false-positive rate at or below 15%.
- Supported responses meet 95% citation precision and coverage.
- PII redaction passes every critical test.
- A participant adds one agency and three service routes through configuration in under 30 minutes.
- A fresh user can complete the local intake-to-approved-response demonstration
  in under 5 minutes after the devcontainer post-create finishes.

## Acceptance scenarios

1. A routine inquiry receives the correct route, grounded response, and next steps.
2. An ambiguous inquiry requests clarification rather than inventing a route.
3. A cross-agency inquiry produces coordinated work items and one constituent summary.
4. An emergency signal exits routine processing immediately.
5. A message containing malicious instructions cannot change system behavior.
6. Language, neighborhood, or demographic cues do not alter routing quality improperly.
7. A routine response visibly identifies itself as AI-assisted before approval and preserves that disclosure after approval.
8. Human corrections are recorded as review events and do not mutate routing policy without an explicit configuration change.
9. Duplicate case-creation attempts for the same approved response return the same case instead of creating another case.
