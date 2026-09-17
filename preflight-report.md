# 🚦 Azure Deployment Preflight Report

**Revision:** 2026-09-17 · **Branch:** `feat/maryland-hackathon-readiness` · **Status:** 🟨🟨🟨⬜⬜ syntax valid; preview blocked by local Docker

## Summary

| Check | Result | Notes |
|---|---|---|
| Project type | ✅ `azd` | `azure.yaml` exists. |
| Bicep files | ✅ Valid syntax | `infra\main.bicep` and `infra\modules\constituent-connect.bicep` built successfully with `az bicep build`. |
| Azure CLI login | ✅ Present | Account context exists; tenant/subscription IDs intentionally omitted. |
| `azd provision --preview` | ⚠️ Blocked | Local Docker/Podman runtime is not running; no Azure resources were deployed. |
| Production deployment | 🚫 Not run | Production deployment is explicitly out of scope. |

## Tools executed

```powershell
az --version
azd version
az account show --output json
azd env list
azd provision --preview --no-prompt
az bicep version
az bicep build --file infra\main.bicep --stdout
az bicep build --file infra\modules\constituent-connect.bicep --stdout
```

## Issues

| Severity | Issue | Remediation |
|---|---|---|
| ⚠️ Medium | Standalone `bicep` executable is not on PATH. | Use `az bicep` or install/upgrade Bicep CLI. |
| ⚠️ Medium | `azd provision --preview` failed because Docker/Podman is not running. | Start Docker Desktop or configure Azure remote build in `azure.yaml`, then rerun preview. |
| ℹ️ Info | Azure CLI and azd updates are available. | Upgrade in a controlled dev environment before final event validation. |

## What-if results

No what-if resource diff was produced because `azd provision --preview` stopped before deployment analysis due to the missing local container runtime. Bicep syntax validation completed successfully, so the independent blocker is the local preview/build environment, not template parsing.

## Recommendations

1. Start Docker Desktop and rerun `azd provision --preview --no-prompt`.
2. If an authorized Spektra development environment is available, run preview first, then deploy only to the authorized dev environment.
3. Keep Azure Communication Services and all outbound connectors disabled unless explicitly feature-flagged for a synthetic exercise.
