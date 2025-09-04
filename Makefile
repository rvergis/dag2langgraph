POETRY := poetry

.PHONY: help setup test run-sample clean lock

help:
	@echo "Targets: setup, test, run-sample, lock, clean"

setup:
	$(POETRY) install --with dev

test:
	$(POETRY) run pytest -q

run-sample:
	$(POETRY) run dag2langgraph examples/sample_dag.json

lock:
	$(POETRY) lock --no-update

clean:
	rm -rf .venv .pytest_cache .ruff_cache .mypy_cache
