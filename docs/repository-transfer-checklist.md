# 📦 Repository Transfer Checklist

**Revision:** 2026-09-17 · **Applies to:** primary repository only · **Status:** 🟩🟩🟩⬜⬜ ready for owner review

## Before transfer

- ✅ Confirm `main` is the default branch and `master` is unused.
- ✅ Confirm `LICENSE`, `NOTICE`, `SECURITY.md`, `CONTRIBUTING.md`, `CODEOWNERS`, issue templates, and PR template are present.
- ✅ Verify no secrets, tenant IDs, subscription IDs, private endpoints, participant data, or real constituent data are tracked.
- ✅ Run tests, evals, frontend build, link checks, and Bicep validation.
- ✅ Confirm `.env`, generated reports, build outputs, caches, `frontend/node_modules/`, and egg-info outputs are ignored.
- ✅ Confirm outbound email, SMS, phone, dispatch, and production case connectors are disabled by default.

## After transfer

- 🔐 Recreate environment secrets in the destination owner; never transfer local `.env` files.
- 🧑‍⚖️ Reconfirm branch protection, CODEOWNERS, dependency review, secret scanning, and least-privilege workflow permissions.
- 🧪 Run a clean-clone quickstart and record evidence in `ACCELERATOR-READINESS-REPORT.md`.
- 🚫 Do not deploy to production as part of transfer.
