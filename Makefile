.PHONY: run test eval

run:
	PYTHONPATH=src python scripts/run_local.py --host 127.0.0.1 --port 8000

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

eval:
	PYTHONPATH=src python -m constituent_connect.eval_runner
