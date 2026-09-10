# Constituent Connect Domain Language

This file is the canonical vocabulary for the repository. If implementation text and this file disagree, this file wins.

| Term | Meaning |
| --- | --- |
| Inquiry | One inbound non-emergency constituent communication. |
| Message | One channel-specific part of an inquiry. |
| Intent | The constituent need inferred from the message. |
| Service | A configured government program or process that may address an intent. |
| Route | The accountable service queue recommended for an inquiry. |
| Evidence | An approved public passage supporting a response. |
| Citation | The visible association between a response claim and its evidence. |
| Draft | An AI-assisted response awaiting the configured human-approval decision. |
| Work item | A scoped agency task created from an approved inquiry summary. |
| Emergency exit | Terminal state that stops routine processing and gives emergency guidance. |
| Clarification | A question required before the system can route safely. |
| Case | A human-approved synthetic record containing scoped work items and audit history. |

## Hero scenario

A constituent asks where to replace a professional license and mentions a related tax-registration change. Constituent Connect minimizes unnecessary personal information, classifies both needs, retrieves current public guidance, drafts one plain-language response with citations, and recommends separate scoped work items. A human approves the response and case. If the message indicates immediate danger, the routine pipeline stops and the application does not dispatch.

## Three-stage pipeline

1. **Listen**: Channel Intake normalizes the message. Safety and Privacy applies deterministic emergency, injection, and redaction rules before any routine action.
2. **Route**: Intent classification proposes candidates. The deterministic Routing Engine applies configured service ownership, confidence thresholds, and disclosure rules.
3. **Respond**: Public Knowledge and Response agents draft only from accepted evidence. Case tools remain unavailable until the human-approval gate passes.

