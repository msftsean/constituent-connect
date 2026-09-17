# C# Gap Analysis

**Revision:** 2026-09-17 · **Repository inspected read-only:** `C:\Users\segayle\repos\constituent-connect-csharp` · **Status:** 🟨🟨🟨⬜⬜ do not modify yet

The C# fork already contains a .NET solution under `dotnet\`, tests, eval project, shared docs, frontend, and infrastructure files. Before implementation work, compare the C# deterministic emergency boundary, expanded PII categories, emergency approval rejection, reroute/escalate decisions, idempotent case creation, OpenAPI decision enum, and expanded 42-case eval dataset against this primary branch.

## Expected gaps to close

- Port the expanded emergency false-positive and critical recall vectors.
- Port expanded PII redaction categories and normal-output leakage tests.
- Ensure server-side reviewer trust does not use client-supplied reviewer identity.
- Ensure duplicate case creation returns the original case.
- Regenerate C# OpenAPI/server DTOs from `porting/api-contract.yaml`.
