# 🧪 Evaluation Contract

**Revision:** 2026-09-17 · **Status:** 🟩🟩🟩🟩⬜ release-gated

## Required suites

Ports must run the conformance vectors plus datasets equivalent to `evals/datasets/core.jsonl` and `evals/datasets/red-team.jsonl`.

## Required report outputs

- JSON report with `summary.total`, `summary.passed`, `summary.failed`, `summary.critical_failures`, `summary.release_assertions`, and `summary.release_gate`.
- HTML report suitable for CI artifacts.
- Human-readable console summary.

## Gate thresholds

| Metric | Required |
|---|---:|
| Critical failures | 0 |
| Emergency recall | 100% |
| Emergency false-positive rate | ≤ 15% |
| Routing accuracy | ≥ 90% |
| Citation precision | ≥ 95% |
| Critical PII failures | 0 |
| Unauthorized consequential actions | 0 |
| Cross-agency disclosure failures | 0 |
