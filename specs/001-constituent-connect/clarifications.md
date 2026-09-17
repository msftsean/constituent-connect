# Clarifications: Maryland Constituent Connect

## Resolved decisions

1. **Relationship to All Clear**: reuse the engineering and workshop patterns, not emergency incident triage.
2. **Primary user**: a constituent or contact-center agent handling a non-emergency inquiry.
3. **Emergency boundary**: immediate-danger signals stop routine processing, give emergency guidance, and require human escalation. The accelerator does not dispatch.
4. **Authority**: approved public agency content and configured service ownership are the only sources for responses and routes.
5. **Decision boundary**: the accelerator does not decide eligibility, legal or medical outcomes, enforcement, complaint disposition, case status, payment, or appointment availability.
6. **Agent boundary**: model-based agents may normalize, classify, retrieve, translate, summarize, and draft. Emergency, privacy, routing, disclosure, and approval gates are deterministic.
7. **Data**: the workshop uses synthetic constituents, messages, services, routes, cases, and public content.
8. **Workshop path**: participants start from a working local application before connecting Azure services.
9. **Architecture diagrams**: editable Draw.io sources using official Fluent 2 system icons and visible text labels.
10. **Generated imagery**: optional only; use MAI Image 2.5 or MAI Image 2.6 with provenance and alt text.

## Open production decisions

- Production channels and system-of-record integrations.
- Agency-specific emergency and crisis language.
- Translation-review process.
- Retention, consent, and public-record requirements.
- Contact-center approval and service-level policies.

These do not block the synthetic workshop accelerator.

