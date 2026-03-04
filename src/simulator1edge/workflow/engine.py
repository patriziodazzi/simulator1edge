from __future__ import annotations

from dataclasses import dataclass
import inspect
from typing import Callable, Literal

from simulator1edge.workflow.dag import WorkflowDAG
from simulator1edge.workflow.model import FunctionSpec


@dataclass(frozen=True)
class FunctionExecutionResult:
    status: Literal["success", "failed"]
    latency_ms: int
    cold_start: bool = False
    details: str = ""


@dataclass(frozen=True)
class NodeExecution:
    node_name: str
    status: Literal["success", "failed", "skipped"]
    start_ms: int
    end_ms: int
    cold_start: bool
    details: str = ""


@dataclass(frozen=True)
class WorkflowExecutionReport:
    workflow_name: str
    status: Literal["success", "failed"]
    total_latency_ms: int
    node_executions: dict[str, NodeExecution]


class WorkflowExecutionEngine:
    """Executes a workflow DAG using a pluggable function runner callback."""

    def execute(
        self,
        workflow: WorkflowDAG,
        run_function: Callable[..., FunctionExecutionResult],
    ) -> WorkflowExecutionReport:
        node_executions: dict[str, NodeExecution] = {}
        layer_end_times: list[int] = []
        accepts_start_ms = _accepts_start_ms(run_function)

        for layer_idx, layer in enumerate(workflow.topological_layers()):
            layer_start_ms = layer_end_times[-1] if layer_end_times else 0
            layer_durations: list[int] = []

            for node_name in layer:
                predecessor_names = workflow.predecessors_of(node_name)
                has_failed_predecessor = any(
                    node_executions[pred].status != "success" for pred in predecessor_names
                )
                if has_failed_predecessor:
                    node_executions[node_name] = NodeExecution(
                        node_name=node_name,
                        status="skipped",
                        start_ms=layer_start_ms,
                        end_ms=layer_start_ms,
                        cold_start=False,
                        details=f"Skipped at layer {layer_idx}: predecessor failed.",
                    )
                    layer_durations.append(0)
                    continue

                if accepts_start_ms:
                    result = run_function(workflow.nodes[node_name], layer_start_ms)
                else:
                    result = run_function(workflow.nodes[node_name])
                node_status: Literal["success", "failed"] = result.status
                end_ms = layer_start_ms + result.latency_ms
                node_executions[node_name] = NodeExecution(
                    node_name=node_name,
                    status=node_status,
                    start_ms=layer_start_ms,
                    end_ms=end_ms,
                    cold_start=result.cold_start,
                    details=result.details,
                )
                layer_durations.append(result.latency_ms)

            layer_end_times.append(layer_start_ms + (max(layer_durations) if layer_durations else 0))

        has_failures = any(node.status == "failed" for node in node_executions.values())
        final_status: Literal["success", "failed"] = "failed" if has_failures else "success"
        return WorkflowExecutionReport(
            workflow_name=workflow.name,
            status=final_status,
            total_latency_ms=layer_end_times[-1] if layer_end_times else 0,
            node_executions=node_executions,
        )


def _accepts_start_ms(run_function: Callable[..., FunctionExecutionResult]) -> bool:
    signature = inspect.signature(run_function)
    positional = [
        p
        for p in signature.parameters.values()
        if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    return len(positional) >= 2
