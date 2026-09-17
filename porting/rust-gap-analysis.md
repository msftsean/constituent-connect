# Rust Gap Analysis

**Revision:** 2026-09-17 · **Repository inspected read-only:** `C:\Users\segayle\repos\constituent-connect-rust` · **Status:** 🟨🟨🟨⬜⬜ do not modify yet

The Rust fork already contains Cargo files, Rust entry points under `src\`, tests/evals, shared docs, frontend, and infrastructure files. Before implementation work, compare the Rust deterministic engines and API DTOs against this primary branch.

## Expected gaps to close

- Port the primary deterministic emergency boundary exactly, including Spanish critical terms and false-positive contexts.
- Port expanded PII regex categories with tests that prevent leakage to normal responses, traces, reports, and work items.
- Preserve zero-model-call gating and bounded agent authority in Rust abstractions.
- Implement authenticated decision states: approve, edit, reject, reroute, escalate.
- Make case creation idempotent per response.
- Run conformance vectors before updating workshop docs.
