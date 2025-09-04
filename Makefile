POETRY := poetry
VENV := .venv

.PHONY: help setup venv test run-sample clean lock

help:
	@echo "Targets: setup, test, run-sample, lock, clean"

# Ensure in-project venv exists and dependencies are installed via Poetry
venv:
	$(POETRY) install --with dev

# Setup will create the .venv (if needed) and install deps via Poetry.
# Note: Activation can't persist from Make; use 'poetry shell' when needed.
setup: venv
	@echo "Virtualenv ready at $(VENV) (Poetry-managed)."
	@echo "To work inside it: 'poetry shell' or prefix commands with 'poetry run'"

test:
	$(POETRY) run pytest -q

run-sample:
	$(POETRY) run dag2langgraph examples/sample_dag.json

lock:
	$(POETRY) lock --no-update

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache .mypy_cache
