# Workshop readiness

This accelerator is **Codespaces-first** and local-synthetic by default. A
participant can complete the intake, draft, human approval, and synthetic case
creation path without Azure credentials. Do not enter real constituent data,
credentials, confidential agency material, or live emergency details.

## Definition of done

Participants are done when they can:

1. Start the local app and see `/health` return `mode: local-synthetic`.
2. Process the **Routine license replacement** sample.
3. Confirm the draft is pending human approval and has a public synthetic
   citation.
4. Approve the draft as the local workshop reviewer.
5. Create a synthetic case and confirm case creation was blocked before approval.
6. Run the readiness check successfully.

## Preflight and readiness

From a Codespace or devcontainer:

```bash
python -m pip install -e .
python scripts/readiness.py
PYTHONPATH=src python -m unittest discover -s tests -v
```

Use `python scripts/readiness.py --full-eval` when a coach wants the complete
synthetic release gate. It writes generated evidence to `reports/readiness/`,
which is ignored by Git.

`scripts/readiness.py` also creates or refreshes the untracked `.env` with a
generated local approval token. Start the app with `make run` or
`PYTHONPATH=src python scripts/run_local.py` so that file is loaded.

## Reset and cleanup

To reset generated workshop artifacts:

```bash
python scripts/reset_workshop.py
```

Use `python scripts/reset_workshop.py --dry-run` to preview removals and
`python scripts/reset_workshop.py --include-node-modules` only when the frontend
dependency install itself needs to be rebuilt.

The local case store is in process memory. Restarting the server clears
inquiries, approvals, cases, and review events.

## Environment variables

| Variable | Required for local workshop? | Purpose |
|---|---:|---|
| `CC_PROJECT_ROOT` | No | Optional override when running outside the repository root. |
| `CC_CONFIG_PATH` | No | Optional path to `config/app.json`. |
| `CC_HOST`, `CC_PORT` | No | Optional local server bind settings for scripts or wrappers. |
| `CC_ENABLE_AZURE_AI_SEARCH` | No | Reserved feature indicator; local implementation does not consume Azure Search. |
| `CC_ENABLE_COSMOS_DB` | No | Reserved feature indicator; local implementation does not consume Cosmos DB. |
| `CC_ENABLE_COMMUNICATION_SERVICES` | No | Reserved feature indicator; sending is not enabled. |
| `CONSTITUENT_CONNECT_APPROVER_ID` | No | Optional configured reviewer identity for token-backed API approval. |
| `CONSTITUENT_CONNECT_APPROVER_TOKEN` | No | Optional local secret for token-backed API approval. Do not print or commit real values. |
| `CC_LOCAL_WORKSHOP_APPROVAL` | No | Explicit opt-in that allows the local UI to retrieve the generated workshop token. Never set it in deployed environments. |

Approval always requires `X-Approval-Role: approver`, a configured approver
identity, and `X-Approver-Token` matching the configured token. With default
tracked configuration and no generated `.env`, the gate fails closed. In a
Codespace, `scripts/readiness.py` generates an untracked local token and
`CC_LOCAL_WORKSHOP_APPROVAL=true`; the local UI reads that token from the local
server. This is a training-only control, not a production authentication
boundary.

## Claims versus evidence

| Claim | Evidence | Release label |
|---|---|---|
| Local synthetic app runs without Azure credentials. | `constituent_connect.server`, packaged fallback UI, `config/app.json` feature flags all false, `scripts/readiness.py`. | Backed for workshop. |
| Human approval is required before case creation. | `CaseAgent.create`, workflow tests, API tests, readiness check. | Backed. |
| Approvals are bound to configured server identity. | Approval requires the configured approver token and uses `CONSTITUENT_CONNECT_APPROVER_ID`; reviewer names supplied by clients are ignored. Bare `X-Approval-Role` is rejected. | Backed. |
| Emergency messages stop routine routing and do not dispatch. | Safety/routing workflow tests, red-team evals, readiness emergency check. | Backed for synthetic inputs. |
| PII is redacted from summaries and traces. | `security.py`, workflow tests, evaluation datasets. | Backed for covered patterns. |
| Prompt injection cannot override policy or routing. | Security patterns, unsafe retrieval filtering, tests and evals. | Backed for covered synthetic attacks. |
| Azure infrastructure is production-shaped and no-secret. | `infra/` Bicep, `azure.yaml`, `infra/README.md`; no deployment is performed in this workshop readiness loop. | Defined, not production-verified. |
| Current app consumes Azure AI Search, Cosmos DB, or ACS data planes. | README and infra note these are feature indicators only; local adapters do not consume endpoints. | Not claimed. |
| Production authentication/authorization is complete. | The generated local token is a workshop convenience and is not production auth. | Not claimed. |

## Known issues and recovery

| Symptom | Recovery |
|---|---|
| Port 8000 is busy. | Run `PYTHONPATH=src python -m constituent_connect.server --port 8001` and open that port. |
| Approval says an approver token is required. | Run `python scripts/readiness.py`, restart with `make run`, and use the provided UI. Manual API calls need both `X-Approval-Role: approver` and the generated `X-Approver-Token`. |
| Case creation fails before approval. | Expected behavior. Approve the draft first. |
| Invalid JSON after a configuration exercise. | Run `python -m json.tool data/services.json` or the edited file and compare with neighboring entries. |
| Evaluation fails. | Inspect `reports/evaluation.json` or `reports/readiness/evaluation.json`; critical failures block release. |
| Azure command fails. | Stop for the workshop path. Azure validation requires an Azure identity and is outside local readiness. |
