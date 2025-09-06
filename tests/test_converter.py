from pathlib import Path
import json
import subprocess
import sys

import pytest

from dag2langgraph.converter import (
    convert_dag_to_langgraph,
    DagValidationError,
    INVALID_DAG_ERROR,
    MISSING_ENTRY_POINT_ERROR,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def load_example(name: str):
    with open(EXAMPLES / name, "r", encoding="utf-8") as f:
        return json.load(f)


def test_convert_success_structure():
    dag = load_example("sample_dag.json")
    out = convert_dag_to_langgraph(dag)
    # Structure checks
    assert set(out.keys()) == {"nodes", "edges", "entry_point"}
    assert out["entry_point"] == "start"
    assert set(out["nodes"].keys()) == {"start", "toolA", "end"}
    assert out["nodes"]["toolA"]["type"] == "tool"
    assert out["nodes"]["start"]["name"] == "StartFn"
    # Edge mapping and optional condition
    assert {e["source"] for e in out["edges"]} == {"start", "toolA"}
    cond_edge = next(e for e in out["edges"] if e["source"] == "toolA")
    assert cond_edge["condition"] == "ok"


def test_bool_condition_edges():
    dag = {
        "nodes": [
            {"id": "start", "type": "function", "name": "StartFn"},
            {"id": "yes", "type": "function", "name": "YesFn"},
            {"id": "no", "type": "function", "name": "NoFn"},
        ],
        "edges": [
            {"source": "start", "target": "yes", "condition": True},
            {"source": "start", "target": "no", "condition": False},
        ],
        "entry_point": "start",
    }
    out = convert_dag_to_langgraph(dag)
    conds = {e["condition"] for e in out["edges"]}
    assert conds == {"true", "false"}


def test_missing_entry_point_error():
    dag = load_example("missing_entry_point.json")
    with pytest.raises(DagValidationError) as exc:
        convert_dag_to_langgraph(dag)
    assert str(exc.value) == MISSING_ENTRY_POINT_ERROR


def test_cycle_detection_error():
    dag = load_example("cycle_dag.json")
    with pytest.raises(DagValidationError) as exc:
        convert_dag_to_langgraph(dag)
    assert str(exc.value) == INVALID_DAG_ERROR


def test_invalid_edge_reference_error():
    dag = load_example("invalid_edge.json")
    with pytest.raises(DagValidationError) as exc:
        convert_dag_to_langgraph(dag)
    assert str(exc.value) == INVALID_DAG_ERROR


def test_cli_success(tmp_path: Path):
    out_file = tmp_path / "out.json"
    proc = subprocess.run(
        [sys.executable, "-m", "dag2langgraph.cli", str(EXAMPLES / "sample_dag.json"), "-o", str(out_file)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["entry_point"] == "start"


def test_cli_errors_to_stderr():
    proc = subprocess.run(
        [sys.executable, "-m", "dag2langgraph.cli", str(EXAMPLES / "cycle_dag.json")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1
    assert INVALID_DAG_ERROR in proc.stderr
