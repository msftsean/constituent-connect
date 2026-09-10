# Maryland Constituent Connect Constitution

## Article I: Mission

Help Maryland agencies receive, understand, answer, summarize, and route non-emergency constituent inquiries across web, chat, email, and voice while preserving human accountability.

## Article II: Scope boundary

- This accelerator is for non-emergency constituent communications and contact-center support.
- All Clear is the emergency and incident-triage path.
- Potential emergencies must immediately receive emergency guidance and human escalation; they must not be processed as routine service requests.

## Article III: Truth and transparency

- Responses use approved agency content and include citations or official links.
- The system must identify the agency, program, and confidence behind a route.
- The system must not invent eligibility, deadlines, case status, legal rights, or commitments.
- Uncertain or conflicting guidance is escalated.
- Constituents are informed when a response is generated or assisted by AI.

## Article IV: Equity, accessibility, and privacy

- The system supports plain language, translation, and accessible response formats.
- Routing and service quality must not vary improperly by protected characteristic, neighborhood, language, or communication channel.
- PII is minimized and redacted from summaries unless needed for the authorized workflow.
- The workshop uses synthetic constituents, cases, and agency content.

## Article V: Human control

- Agents may classify, summarize, retrieve, draft, translate, and recommend routing.
- Agents do not determine benefits eligibility, legal outcomes, enforcement, emergency dispatch, or final complaint disposition.
- Human agents can edit, approve, reroute, and audit every consequential output.

## Article VI: Engineering quality

- The application runs locally with synthetic data before Azure integration.
- Channel intake, safety, retrieval, response, routing, and case actions are separate components.
- The system is observable and evaluation-gated.
- Agency routes and content are configuration, not hardcoded branches.

## Article VII: All Clear engineering inheritance

- The repository must define one canonical domain vocabulary in `CONTEXT.md`.
- The runtime must preserve a three-stage Listen → Route → Respond pipeline.
- Each agent has bounded authority; emergency, privacy, routing, disclosure, and approval gates must be deterministic.
- Configuration owns thresholds, service ownership, escalation mappings, and data-sharing boundaries.
- The participant experience starts from a working local application and adds Azure capabilities progressively.

## Article VIII: Design artifacts

- Architecture diagrams must be maintained as editable Draw.io source files.
- Diagram nodes must use Microsoft Fluent 2 system icons with accessible text labels.
- Generated raster art must never replace an architecture diagram.
- If non-diagram imagery is required, use MAI Image 2.5 or MAI Image 2.6, keep it optional to function, record provenance, and provide alt text.
