# 🧱 Porting Order

**Revision:** 2026-09-17 · **Status:** 🟩🟩🟩⬜⬜ ready for future fork work

1. Load `CONTEXT.md`, synthetic data, and shared schemas.
2. Implement pure deterministic Safety/Privacy Engine and PII redaction.
3. Implement intent/routing with configured taxonomy and confidence thresholds.
4. Implement public-knowledge retrieval with citation filtering and retrieved-content injection blocking.
5. Implement response drafting and quality gates without external calls.
6. Implement server-side reviewer authorization, decisions, audit events, and idempotent cases.
7. Implement API contract and safe DTOs.
8. Port eval runner and conformance vectors.
9. Add frontend/workshop docs only after behavior passes.
10. Add Azure adapters behind disabled-by-default feature flags.
