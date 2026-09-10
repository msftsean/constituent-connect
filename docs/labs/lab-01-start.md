# Lab 01: Start and inspect

## Objective

Start the local application and verify the workshop is running in synthetic
mode.

## Path

1. Run `make test`.
2. Run `make run`.
3. Open <http://127.0.0.1:8000>.
4. Check `/health` and confirm `local-synthetic`.
5. Select a sample inquiry without adding personal information.

## Check

The page loads locally, the health response is synthetic, and no external
dispatch or live constituent connector is involved.
