# Tasks: Maryland Constituent Connect

## Foundation

- [x] CC-001 Create repository structure, devcontainer, environment template, and CI.
- [x] CC-002 Create React inbox with Conversation, Summary, Evidence, Route, Response, and Coach Trace panels.
- [x] CC-003 Create FastAPI service with intake, classify, respond, approve, route, case, and evaluation endpoints.
- [x] CC-004 Define Pydantic models and JSON schemas.
- [x] CC-005 Add synthetic agencies, services, public documents, inquiries, and expected routes.
- [x] CC-006 Establish `CONTEXT.md` as the canonical domain vocabulary and add drift tests.

## Agents and workflow

- [x] CC-010 Implement channel adapters and normalized message schema.
- [x] CC-011 Implement Safety and Privacy Agent with emergency, PII, and injection controls.
- [x] CC-012 Implement Intent Agent and configurable taxonomy.
- [x] CC-013 Implement Public Knowledge Agent with citation support.
- [x] CC-014 Implement Response Agent with plain-language and multilingual modes.
- [x] CC-015 Implement Routing Agent with confidence and alternative routes.
- [x] CC-016 Implement Case Agent and human approval workflow.
- [x] CC-017 Implement Quality Agent and outbound-response policy checks.
- [x] CC-018 Prove the Safety/Privacy and Routing Engines perform zero generative calls for gating decisions.
- [x] CC-019 Add authority-boundary tests for every agent and tool.

## Observability and security

- [x] CC-020 Add structured traces, correlation IDs, and transformation history.
- [x] CC-021 Add Key Vault, managed identity, and least-privilege configuration.
- [x] CC-022 Add configurable retention and redaction.
- [x] CC-023 Add cross-agency disclosure controls.

## Evals and red team

- [x] CC-030 Implement evaluation runner.
- [x] CC-031 Add golden routing and response datasets.
- [x] CC-032 Add emergency, ambiguity, cross-agency, and unsupported-answer tests.
- [x] CC-033 Add PII, injection, fraud, discriminatory-routing, legal, medical, and threatening-content tests.
- [x] CC-034 Add language and accessibility quality slices.
- [x] CC-035 Produce machine-readable and HTML score reports.
- [x] CC-036 Enforce critical-failure release gate in CI.

## Azure and workshop

- [x] CC-040 Add Bicep and Azure Developer CLI configuration.
- [x] CC-041 Deploy Container Apps, AI Search, Blob, Cosmos DB, Key Vault, and monitoring.
- [x] CC-042 Add optional Communication Services extension behind a feature flag.
- [x] CC-043 Create participant quickstart and seven progressive labs (Lab 00-06).
- [x] CC-044 Create coach runbook, demo prompts, judging guide, and recovery steps.
- [x] CC-045 Conduct concurrent smoke test and record evidence.
- [x] CC-046 Create progressive Lab 00-06 paths: local run, orchestration, safety/privacy, retrieval/routing, approval, deployment, eval/red team.
- [x] CC-047 Create participant site, coach site, architecture page, and evaluation scorecard.
- [x] CC-048 Maintain editable Draw.io diagrams with Fluent 2 icons and accessibility labels.
- [x] CC-049 Add optional MAI Image 2.5/2.6 asset manifest if generated non-diagram imagery is introduced.

## Reconciled requirements

- [x] CC-050 Add visible AI-assistance disclosure to response models, UI, API, and audit events.
- [x] CC-051 Capture human corrections, reroutes, and review outcomes as evaluation signals without automatic policy mutation.
- [x] CC-052 Add deterministic injection handling for constituent and retrieved content with authority-boundary tests.
- [x] CC-053 Add canonical-vocabulary drift tests and explicit zero-generative-call tests for safety and routing gates.
- [x] CC-054 Add measurable release assertions for 90% routing accuracy, 100% critical emergency recall, 95% citation precision, and quickstart timing.
- [x] CC-055 Reconcile the OpenAPI contract with typed request/response schemas and classify/route operations.
- [x] CC-056 Add structured correlation, latency, model/cost telemetry, configurable retention, and privacy-safe persistence.
