from typing import Any, Dict, List, Set


class DagValidationError(ValueError):
    pass


INVALID_DAG_ERROR = "Invalid DAG structure or cycles detected."
MISSING_ENTRY_POINT_ERROR = "Entry point not specified."


def _ensure_bool(condition: bool, msg: str) -> None:
    if not condition:
        raise DagValidationError(msg)


def _validate_node(node: Dict[str, Any]) -> None:
    _ensure_bool(isinstance(node, dict), INVALID_DAG_ERROR)
    _ensure_bool("id" in node and isinstance(node["id"], str) and node["id"], INVALID_DAG_ERROR)
    _ensure_bool("type" in node and node["type"] in {"function", "tool"}, INVALID_DAG_ERROR)
    _ensure_bool("name" in node and isinstance(node["name"], str) and node["name"], INVALID_DAG_ERROR)


def _validate_edge(edge: Dict[str, Any], node_ids: Set[str]) -> None:
    _ensure_bool(isinstance(edge, dict), INVALID_DAG_ERROR)
    _ensure_bool("source" in edge and isinstance(edge["source"], str) and edge["source"], INVALID_DAG_ERROR)
    _ensure_bool("target" in edge and isinstance(edge["target"], str) and edge["target"], INVALID_DAG_ERROR)
    _ensure_bool(edge["source"] in node_ids and edge["target"] in node_ids, INVALID_DAG_ERROR)
    if "condition" in edge:
        _ensure_bool(edge["condition"] is None or isinstance(edge["condition"], str), INVALID_DAG_ERROR)


def _has_cycle_kahn(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> bool:
    node_ids = [n["id"] for n in nodes]
    indeg = {nid: 0 for nid in node_ids}
    adj: Dict[str, List[str]] = {nid: [] for nid in node_ids}
    for e in edges:
        s, t = e["source"], e["target"]
        indeg[t] += 1
        adj[s].append(t)
    queue = [nid for nid in node_ids if indeg[nid] == 0]
    visited = 0
    while queue:
        cur = queue.pop(0)
        visited += 1
        for nxt in adj[cur]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)
    return visited != len(node_ids)


def validate_dag(dag: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(dag, dict):
        raise DagValidationError(INVALID_DAG_ERROR)

    # entry_point validation as separate error type per spec
    if "entry_point" not in dag or not isinstance(dag["entry_point"], str) or not dag["entry_point"]:
        raise DagValidationError(MISSING_ENTRY_POINT_ERROR)

    nodes = dag.get("nodes")
    edges = dag.get("edges")
    _ensure_bool(isinstance(nodes, list) and isinstance(edges, list), INVALID_DAG_ERROR)

    # validate nodes
    seen: Set[str] = set()
    for node in nodes:
        _validate_node(node)
        _ensure_bool(node["id"] not in seen, INVALID_DAG_ERROR)
        seen.add(node["id"])

    _ensure_bool(dag["entry_point"] in seen, INVALID_DAG_ERROR)

    # validate edges
    for edge in edges:
        _validate_edge(edge, seen)

    # cycle check
    if _has_cycle_kahn(nodes, edges):
        raise DagValidationError(INVALID_DAG_ERROR)

    return {"nodes": nodes, "edges": edges, "entry_point": dag["entry_point"]}


def map_nodes(validated_nodes: List[Dict[str, Any]]) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    for n in validated_nodes:
        out[n["id"]] = {"type": n["type"], "name": n["name"]}
    return out


def map_edges(validated_edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for e in validated_edges:
        item: Dict[str, Any] = {"source": e["source"], "target": e["target"]}
        if "condition" in e and e["condition"] is not None:
            item["condition"] = e["condition"]
        out.append(item)
    return out


def convert_dag_to_langgraph(dag: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and converts a DAG JSON structure into LangGraph JSON format.

    Raises DagValidationError with one of the messages specified in the spec.
    """
    validated = validate_dag(dag)
    lg_nodes = map_nodes(validated["nodes"])
    lg_edges = map_edges(validated["edges"])
    return {"nodes": lg_nodes, "edges": lg_edges, "entry_point": validated["entry_point"]}

