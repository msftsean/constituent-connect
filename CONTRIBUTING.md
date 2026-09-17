# 🤝 Contributing

**Revision:** 2026-09-17 · **Target branch:** `main` via PR · **Status:** 🟩🟩🟩⬜⬜ contributor-ready

## Ground rules

1. Use `main`, never `master`.
2. Keep data synthetic; do not add credentials, tenant IDs, subscription IDs, private endpoints, participant data, or real constituent information.
3. Preserve the Listen → Route → Respond vocabulary in `CONTEXT.md`.
4. Deterministic safety/privacy and routing gates control authority; generative agents may propose but never override gates.
5. Outbound email, SMS, phone calls, dispatch, and production case-system connectors must remain disabled by default.

## Local validation

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
python -m constituent_connect.eval_runner --output reports\local
Set-Location frontend; npm ci; npm run build -- --emptyOutDir
```

## Pull requests

Use the PR template. Include test/eval evidence, note any deferred capabilities, and update docs/specs when behavior changes.
