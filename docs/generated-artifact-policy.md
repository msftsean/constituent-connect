# 🧾 Generated Artifact Policy

**Revision:** 2026-09-17 · **Status:** 🟩🟩🟩🟩⬜ enforced by `.gitignore` and CI intent

## Track these artifacts

- Curated synthetic datasets in `data/` and `evals/datasets/`.
- Human-authored docs, specs, runbooks, and Draw.io sources.
- Intentional release evidence under `reports/final/` when reviewed for secrets and PII.
- Porting contracts under `porting/`.

## Do not track these artifacts

- `.env` files and local credentials.
- `frontend/node_modules/`, `frontend/dist/`, Python `*.egg-info/`, `__pycache__/`, build folders, and local caches.
- Ad hoc eval output under `reports/local/`, `reports/baseline/`, `reports/hardening/`, `reports/expanded-eval/`, `reports/readiness/`, and team-specific reports.
- Screenshots or logs containing real participant, tenant, subscription, endpoint, or constituent data.

## Release evidence rule

Before moving generated evidence into `reports/final/`, run the release tests and scan the artifact for secrets and PII. Keep evidence synthetic and reproducible.
