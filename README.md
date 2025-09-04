# dag2langgraph

Compiles a DAG JSON into LangGraph JSON. Includes validation for structure and cycles.

## Install / Run (Poetry)

- Ensure Poetry is installed: https://python-poetry.org/docs/#installation
- Create an in-project virtualenv and install deps (creates `.venv`):
  - `make setup`
- Run tests:
  - `make test`
- Convert a DAG file via console script:
  - `poetry run dag2langgraph examples/sample_dag.json -o /tmp/langgraph.json`
- Or via stdin/stdout:
  - `cat examples/sample_dag.json | poetry run dag2langgraph - > /tmp/langgraph.json`

## Makefile Targets

- `setup`: creates/uses `.venv` and installs deps via Poetry.
- `test`: `poetry run pytest -q`.
- `run-sample`: run CLI on `examples/sample_dag.json`.
- `lock`: create/update `poetry.lock` without resolving newer versions.
- `clean`: remove `.venv` and caches.

## Publishing

- GitHub Actions workflow `Publish to PyPI` builds and uploads the package when:
  - A GitHub Release is published, or
  - You push a tag like `v0.1.0`, or
  - You manually dispatch the workflow.

- Required secret in the repo settings:
  - `PYPI_API_TOKEN`: PyPI API token (user: `__token__`).

## Releasing (Patch)

- Use the `Release Patch Version` workflow (workflow_dispatch) to:
  - Bump the patch version via Poetry
  - Commit the change and create tag `vX.Y.Z`
  - Create a GitHub Release
  - This will trigger the publish workflow to upload to PyPI


## Input DAG schema (summary)

- `nodes`: array of objects with `id` (string), `type` ("function" | "tool"), `name` (string)
- `edges`: array of objects with `source` (string), `target` (string), optional `condition` (string)
- `entry_point`: string (must match a node `id`)

## Output LangGraph JSON (summary)

- `nodes`: object keyed by node `id`, each with `{ type, name }`
- `edges`: array of `{ source, target }` plus `condition` when provided
- `entry_point`: copied from input

## Errors

- `Entry point not specified.` — when `entry_point` is missing/empty
- `Invalid DAG structure or cycles detected.` — for malformed fields, missing refs, duplicate ids, or cycles
