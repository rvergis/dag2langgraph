POETRY := poetry
VENV := .venv

.PHONY: help setup venv test run-sample clean lock patch publish

help:
	@echo "Targets: setup, test, run-sample, lock, patch, publish, clean"

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
	$(POETRY) lock

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache .mypy_cache

# Bump patch version, commit, and tag (vX.Y.Z)
patch:
	@$(POETRY) version patch
	@NEWVER="$$( $(POETRY) version -s )"; \
	  echo "New version: $$NEWVER"; \
	  git add pyproject.toml; \
	  git commit -m "chore(release): v$$NEWVER" >/dev/null 2>&1 || echo "(no changes to commit)"; \
	  git tag v$$NEWVER; \
	  echo "Created tag v$$NEWVER. Run 'make publish' to push and trigger release."

# Push current branch and version tag to origin to trigger GitHub Actions publish
publish:
	@NEWVER="$$( $(POETRY) version -s )"; \
	  echo "Pushing branch and tag v$$NEWVER to origin..."; \
	  git push origin HEAD; \
	  git push origin v$$NEWVER; \
	  echo "Pushed. If workflows are configured, PyPI publish will run."
