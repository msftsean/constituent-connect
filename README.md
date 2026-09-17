# Maryland Constituent Connect

Local-first implementation foundation for the approved Maryland Constituent Connect specification. It uses only synthetic agencies, public content, constituents, and cases.

The repository follows the proven All Clear delivery pattern while preserving a distinct non-emergency constituent-communications mission. See `SPECKIT.md`, `CONTEXT.md`, and `.specify/ALL-CLEAR-PATTERN.md`.

## Safety boundary

- This is a **non-emergency** contact-center demonstration.
- Emergency language exits routine processing, shows guidance to call 911, and requires human escalation.
- The application **does not dispatch** emergency services.
- AI-assisted responses remain drafts until a human approves them.
- The system does not decide eligibility, legal or medical outcomes, enforcement, complaint disposition, or case status.

## Included

- FastAPI service plus a legacy standard-library local adapter.
- React/Vite contact-center experience with a dependency-free packaged fallback.
- Transport-neutral workflow and modular intake, safety/privacy, intent, retrieval, response, routing, case, and quality agents.
- Configuration-backed synthetic agency/service catalog and public knowledge.
- PII redaction, prompt-injection filtering, citations, abstention, cross-agency handoffs, and approval-gated case creation.
- JSONL evaluation runner with JSON and HTML reports.
- Standard-library `unittest` coverage, frontend build checks, devcontainer, CI, and
  production-shaped Azure infrastructure definitions.
- Editable Draw.io architecture source using Fluent 2 system icons.

The FastAPI adapter is the production-shaped API surface. The standard-library adapter
remains available for an offline zero-dependency smoke test. Build the React app with
`npm --prefix frontend ci && npm --prefix frontend run build`; the local server serves
`frontend/dist` when present and otherwise serves the packaged fallback UI. In
Codespaces, use the forwarded **8000** port as the primary route for first success.

## Run locally

Python 3.11 or newer is required. The editable install provides FastAPI and Uvicorn;
the legacy adapter itself uses only the standard library. Node.js 20+ is required to
build the React frontend.

```bash
cd constituent-connect
python -m pip install -e .
python scripts/readiness.py
PYTHONPATH=src python scripts/run_local.py
```

Open the forwarded port 8000 URL in Codespaces, or <http://127.0.0.1:8000>
when running locally. Use a sample inquiry, review the route and citations, edit
the draft, approve it, then create a synthetic case. `scripts/readiness.py`
creates or updates an untracked local `.env` with a generated workshop approver token; the
UI uses that token for the approval call. This local workshop identity is a
training-only assertion protected by a generated local token, not production
authentication. Emergency responses cannot be approved as routine responses;
they may only be rejected or escalated.

For the FastAPI service:

```bash
PYTHONPATH=src python -m constituent_connect.fastapi_adapter
```

For the React development experience, use a second terminal:

```bash
npm --prefix frontend ci
npm --prefix frontend run dev
```

Codespaces forwards Vite on port 5173. The frontend uses relative `/api` and
`/health` calls through the Vite proxy; do not replace them with a browser
`localhost` backend URL.

Optional console scripts after editable install:

```bash
python -m pip install -e .
constituent-connect
```

## Test and evaluate

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m constituent_connect.eval_runner
```

On systems with GNU Make, `make test` and `make eval` are equivalent.

The evaluation command consumes `evals/datasets/core.jsonl` and `evals/datasets/red-team.jsonl`. It writes JSON and HTML reports and exits nonzero when the release gate fails. Current release assertions cover 100% critical emergency recall, emergency false-positive rate, routing accuracy, citation precision, and zero critical PII failures.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Local health and mode |
| GET | `/api/synthetic/inquiries` | Demo inquiry library |
| POST | `/api/intake` | Normalize and safety-assess |
| POST | `/api/respond` | Run the draft and route workflow |
| POST | `/api/responses/{id}/approve` | Record a human approval, edit, rejection, reroute, or escalation |
| POST | `/api/cases` | Create a synthetic case after approval |
| POST | `/api/evals/run` | Run the approved evaluation datasets |

Example:

```bash
curl -s http://127.0.0.1:8000/api/respond \
  -H 'Content-Type: application/json' \
  -d '{"channel":"web","message":"Where do I apply for a replacement professional license?"}'
```

## Configuration

- `config/app.json`: thresholds, privacy policy, feature flags, and the explicit no-dispatch setting.
- `data/agencies.json`: synthetic agency directory.
- `data/services.json`: services, queues, owners, disclaimers, URLs, and intent keywords.
- `data/public_knowledge.json`: approved synthetic public passages.
- `data/inquiries.json`: demo examples.

To add an agency without changing Python, add its agency entry, service entries, and approved public passages. Keep all workshop content synthetic and use public URLs only.

## Project map

```text
src/constituent_connect/
  agents/          modular workflow stages
  web/             packaged fallback browser experience
  workflow.py      transport-neutral orchestration and approval state
  server.py        local HTTP adapter
  fastapi_adapter.py FastAPI API surface
  eval_runner.py   evaluation and release gate
frontend/          React/Vite contact-center experience
data/              synthetic configuration and content
tests/             standard-library unit tests
docs/              participant and coach runbooks
infra/             Azure Container Apps, identity, data, search, and monitoring
```

## Azure status

`azure.yaml` and `infra/` now define a production-shaped, no-secret Container Apps
baseline: managed identity, ACR, Key Vault, private Blob containers, Cosmos DB, AI
Search, Application Insights, least-privilege RBAC, bounded scaling, and optional
default-disabled Communication Services. Azure commands, including `azd`, are
facilitator-only and not part of the participant path. The current application
remains local-first until its Azure adapters and production authentication are
separately reviewed; no-dispatch and human-approval boundaries remain enforced
locally. Do not treat the Bicep definitions as a verified production deployment.
See `infra/README.md` for deployment, networking, and feature-flag constraints.

## Architecture source

Open `design/constituent-connect-architecture.drawio` in drawio.com. The source uses official Fluent 2 system-icon references and accessible text labels. Architecture diagrams are never replaced with generated images. Optional non-diagram imagery must use MAI Image 2.5 or MAI Image 2.6 and include provenance and alt text.

## Workshop paths

- [Fresh-user quickstart](docs/quickstart.md)
- [Workshop readiness, preflight, reset, and evidence](docs/workshop-readiness.md)
- [Coach site](docs/coach-site.html) and [coach runbook](docs/coach-runbook.md)
- [Participant labs 00-06](docs/quickstart.md#3-follow-the-participant-path)
- [Architecture HTML](docs/architecture.html) and [editable Drawio source](design/constituent-connect-architecture.drawio)
- [Evaluation scorecard](docs/evaluation-scorecard.md)
- [Synthetic concurrent smoke-test evidence and template](docs/concurrent-smoke-test.md)
