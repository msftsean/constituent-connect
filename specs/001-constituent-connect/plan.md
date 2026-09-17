# Implementation Plan: Maryland Constituent Connect

## Technical approach

Build a React/TypeScript contact-center experience with a Python FastAPI API. Microsoft Agent Framework coordinates intake, safety, retrieval, response, and routing when enabled, while deterministic Safety/Privacy and Routing Engines remain authoritative for gating. Azure AI Search indexes synthetic public content and service definitions. Cosmos DB stores synthetic cases, messages, approvals, and evaluation results. Azure Communication Services is an optional extension for synthetic voice or messaging demonstrations.

The delivery shape follows All Clear: a visible hero scenario, canonical domain language, a three-stage bounded-agent pipeline, deterministic decision gates, a local-first quickstart, progressive labs, separate participant and coach surfaces, and release-gated evals.

## Agent topology

1. Channel Intake Agent: normalizes web, chat, email, or transcription input.
2. Safety and Privacy Agent: deterministically detects current emergencies, distinguishes historical/negated/hypothetical/false-positive references, detects injection attempts, and redacts sensitive data.
3. Intent Agent: classifies service, agency, urgency, language, and confidence.
4. Public Knowledge Agent: retrieves official public passages.
5. Response Agent: drafts a cited plain-language response.
6. Routing Agent: recommends one or more accountable agency queues.
7. Case Agent: prepares a human-approved case record and handoff summary.
8. Quality Agent: checks citation support, tone, accessibility, and prohibited commitments.

## Bounded authority

- Channel Intake Agent: normalize channel content only.
- Safety and Privacy Engine: deterministic emergency exit, injection handling, and PII minimization; zero generative calls for the gating decision.
- Intent Agent: propose intent candidates only.
- Routing Engine: deterministically apply configured service ownership, confidence thresholds, disclosure scope, and escalation rules.
- Public Knowledge Agent: retrieve public evidence only.
- Response Agent: draft from accepted evidence; cannot promise eligibility, payment, status, or outcome.
- Case tool: unavailable until the human-approval gate passes; creation is idempotent per response.
- Quality Agent: block unsupported or prohibited drafts; cannot approve them.

## Data and retrieval

- Blob containers: `public-faq`, `service-catalog`, `forms`, `agency-directory`, `routing-guidance`.
- Search index fields: document ID, agency, service, geography, language, effective date, owner, public URL, content, chunk ID.
- Routing configuration maps intents to primary and secondary queues, escalation owners, and service expectations.
- Conversation content never overrides system policy or authoritative agency configuration.

## Delivery phases

### Phase 0: Local foundation

- Synthetic inquiry stream, agency directory, service taxonomy, and mock public corpus.
- Inbox, conversation, evidence, route, response, and coach trace views.

### Phase 1: Azure connection

- Foundry model configuration.
- Blob ingestion, AI Search, Cosmos persistence, and telemetry.
- Optional Azure Communication Services adapter.

### Phase 2: Agent behavior

- Implement emergency boundary, privacy minimization, grounded response, routing, and human approval.
- Implement cross-agency coordination and correction capture.

### Phase 3: Evaluation and red team

- Run routing, emergency, groundedness, privacy, injection, accessibility, language, and fairness suites.
- Block release on critical failures.

### Phase 4: Workshop packaging

- Codespaces/devcontainer and `azd up`.
- Participant and coach runbooks.
- Demo inquiry library, failure injection, and bring-it-home configuration exercise.
- Editable Draw.io architecture sources using Fluent 2 icons.
- A participant site, coach view, architecture page, and evaluation scorecard modeled on the All Clear workshop experience.

## Key decisions

- All Clear remains the emergency triage application.
- Contact-center actions default to human approval.
- Public content can be multilingual, but the authoritative source remains visible.
- Agency ownership and routing rules are versioned configuration.
- AI assistance is disclosed to constituents and retained in the approved response and audit history.
- Emergency responses may be rejected or escalated, but never approved as routine responses.
- Human corrections are captured as evaluation signals and never mutate policy automatically.
