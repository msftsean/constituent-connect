# 🧭 Constituent Connect Porting Package

**Revision:** 2026-09-17 · **Reference branch:** `feat/maryland-hackathon-readiness` · **Status:** 🟩🟩🟩🟩⬜ primary implementation is behavioral reference

This package defines the language-neutral contract for future C# and Rust ports. Do not change `C:\Users\segayle\repos\constituent-connect-csharp` or `C:\Users\segayle\repos\constituent-connect-rust` until the primary implementation has passed its gates and this package is reviewed.

## Contract files

- `behavioral-contract.md` — required Listen → Route → Respond behavior.
- `api-contract.yaml` — versioned OpenAPI contract copied from the primary FastAPI surface.
- `domain-schemas/` — JSON schemas for transport-neutral domain objects.
- `conformance-vectors/` — deterministic vectors ports must pass.
- `security-invariants.md` — non-negotiable safety/privacy/approval rules.
- `evaluation-contract.md` — release-gate metrics and report shapes.
- `csharp-gap-analysis.md` and `rust-gap-analysis.md` — read-only fork gap notes.
- `porting-order.md` — recommended implementation order.

## Release bar

Ports must pass the same expected outcomes as the primary implementation: zero critical eval failures, 100% emergency recall, emergency false-positive rate ≤ 15%, zero critical PII leakage, approval-gated idempotent case creation, scoped cross-agency work items, and no enabled outbound connector by default.
