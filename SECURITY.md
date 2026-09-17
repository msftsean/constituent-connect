# 🔐 Security Policy

**Revision:** 2026-09-17 · **Branch:** `feat/maryland-hackathon-readiness` · **Status:** 🟩🟩🟩🟩⬜ workshop hardening active

## Supported scope

This repository is a synthetic workshop accelerator. Supported security reports include emergency-boundary failures, PII leakage, prompt-injection bypasses, unauthorized approval or case creation, cross-agency disclosure, dependency risks, and deployment misconfiguration.

## Reporting

Open a private security advisory or contact the repository owner through the approved GitHub security workflow. Do not include real constituent data, secrets, tenant IDs, subscription IDs, private endpoints, or production system details in a report.

## Security invariants

- 🚨 Emergency detection is deterministic and makes zero generative-model calls.
- 🧹 Raw constituent content is redacted before normal API/browser responses, traces, reports, work items, analytics, and errors.
- 🧑‍⚖️ Human approval requires a configured reviewer identity, role, and token in local workshop mode; production deployments must use Microsoft Entra authorization.
- 🧾 Case creation is approval-gated and idempotent per response.
- 🧱 Outbound email, SMS, phone calls, dispatch, and production system integrations are disabled by default.

## Dependency and secret handling

Use synthetic data only. Keep `.env`, `frontend/node_modules/`, generated reports, build outputs, and local caches untracked. Run the repository tests, eval gate, and secret/PII scans before release.
