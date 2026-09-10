# Lab 06: Configuration and evaluation

## Objective

Extend the synthetic catalog without changing Python workflow behavior.

## Path

1. Add one synthetic agency to `data/agencies.json`.
2. Add three synthetic services with keywords and distinct queues to
   `data/services.json`.
3. Add at least one approved synthetic public passage per service.
4. Add sample inquiries to `data/inquiries.json`.
5. Restart the server.
6. Process each sample and run `make test && make eval`.

## Check

Review `reports/evaluation.json` and `reports/evaluation.html`. Do not route
using protected characteristics, neighborhood, language, or channel. Policy
corrections belong in tests and reviewed configuration.
