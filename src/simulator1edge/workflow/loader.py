from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from simulator1edge.workflow.dag import WorkflowDAG
from simulator1edge.workflow.model import FunctionSpec


def load_workflow_dag(path: str | Path) -> WorkflowDAG:
    """Load a workflow DAG from JSON or YAML file."""
    dag_path = Path(path)
    suffix = dag_path.suffix.lower()
    if suffix == ".json":
        with dag_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return workflow_dag_from_mapping(payload)

    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "YAML support requires 'PyYAML'. Install it or use JSON input."
            ) from exc

        with dag_path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle)
        return workflow_dag_from_mapping(payload)

    raise ValueError(f"Unsupported workflow file format '{suffix}'. Use .json/.yaml/.yml.")


def workflow_dag_from_mapping(data: dict[str, Any]) -> WorkflowDAG:
    """Create a workflow DAG from a dictionary payload."""
    if not isinstance(data, dict):
        raise ValueError("Workflow payload must be a dictionary.")

    name = data.get("name") or data.get("workflow_name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Workflow payload requires non-empty string field 'name'.")

    dag = WorkflowDAG(name=name)

    raw_nodes = data.get("nodes")
    if raw_nodes is None:
        raw_nodes = data.get("functions")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise ValueError("Workflow payload requires non-empty list field 'nodes' (or 'functions').")

    for index, raw_node in enumerate(raw_nodes):
        if not isinstance(raw_node, dict):
            raise ValueError(f"Node at index {index} must be an object.")
        try:
            node = FunctionSpec(
                name=str(raw_node["name"]),
                image=str(raw_node["image"]),
                base_duration_ms=int(raw_node["base_duration_ms"]),
                memory_mb=int(raw_node.get("memory_mb", 128)),
                payload_bytes=int(raw_node.get("payload_bytes", 0)),
                retries=int(raw_node.get("retries", 0)),
            )
        except KeyError as exc:
            raise ValueError(f"Node at index {index} is missing required field '{exc.args[0]}'.") from exc
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Node '{raw_node.get('name', index)}' contains invalid numeric field values."
            ) from exc

        dag.add_node(node)

    raw_dependencies = data.get("dependencies", [])
    if not isinstance(raw_dependencies, list):
        raise ValueError("'dependencies' must be a list.")

    for dep in raw_dependencies:
        source, target = _parse_dependency(dep)
        dag.add_dependency(source, target)

    return dag


def _parse_dependency(dep: Any) -> tuple[str, str]:
    if isinstance(dep, dict):
        source = dep.get("source")
        target = dep.get("target")
        if isinstance(source, str) and isinstance(target, str):
            return source, target
        raise ValueError("Dependency objects must contain string fields 'source' and 'target'.")

    if isinstance(dep, (list, tuple)) and len(dep) == 2:
        source, target = dep
        if isinstance(source, str) and isinstance(target, str):
            return source, target
        raise ValueError("Dependency pairs must contain two string node names.")

    raise ValueError("Dependency must be either {'source','target'} or [source, target].")

