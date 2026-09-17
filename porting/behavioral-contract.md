# 📜 Behavioral Contract

**Revision:** 2026-09-17 · **Status:** 🟩🟩🟩🟩⬜ reference behavior specified

## Pipeline

1. **LISTEN**: normalize web, chat, email, or synthetic voice input; retain raw content server-side only under retention policy.
2. **ROUTE**: deterministic Safety/Privacy Engine decides emergency/privacy/injection gates before any routine route; deterministic Routing Engine applies configured service ownership and thresholds.
3. **RESPOND**: retrieve approved public information, draft a cited plain-language response, run quality checks, require authenticated human decision, and create one idempotent case only after approval.

## Required terminal states

- `route_proposed`: cited routine response is pending human approval.
- `clarification_required`: evidence or routing confidence is insufficient.
- `emergency_exit`: routine processing stops; emergency guidance and human escalation are visible; no dispatch and no routine case.
- `approved`, `rejected`, `escalated`: authenticated reviewer decisions. Emergency responses may be rejected or escalated, never approved as routine.

## Prohibited behavior

Ports must not guarantee eligibility, payment, appointments, legal/medical determinations, enforcement outcomes, complaint disposition, case status, emergency dispatch, autonomous outbound communication, or discriminatory routing.
