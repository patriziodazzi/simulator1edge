from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from simulator1edge.workflow.dag import WorkflowDAG
from simulator1edge.workflow.engine import FunctionExecutionResult, WorkflowExecutionEngine
from simulator1edge.workflow.model import FunctionSpec


class WorkflowEngineTests(unittest.TestCase):
    def _dag(self) -> WorkflowDAG:
        dag = WorkflowDAG("wf")
        dag.add_node(FunctionSpec("a", "img", 10))
        dag.add_node(FunctionSpec("b", "img", 20))
        dag.add_node(FunctionSpec("c", "img", 30))
        dag.add_node(FunctionSpec("d", "img", 40))
        dag.add_dependency("a", "b")
        dag.add_dependency("a", "c")
        dag.add_dependency("b", "d")
        dag.add_dependency("c", "d")
        return dag

    def test_success_path_uses_layer_parallelism(self):
        dag = self._dag()
        engine = WorkflowExecutionEngine()

        def run_function(spec: FunctionSpec) -> FunctionExecutionResult:
            return FunctionExecutionResult(status="success", latency_ms=spec.base_duration_ms)

        report = engine.execute(dag, run_function)
        self.assertEqual(report.status, "success")
        # layers: a(10) -> max(b=20,c=30)=30 -> d(40) = 80
        self.assertEqual(report.total_latency_ms, 80)
        self.assertEqual(report.node_executions["d"].status, "success")

    def test_failure_skips_dependent_nodes(self):
        dag = self._dag()
        engine = WorkflowExecutionEngine()

        def run_function(spec: FunctionSpec) -> FunctionExecutionResult:
            if spec.name == "c":
                return FunctionExecutionResult(status="failed", latency_ms=15, details="boom")
            return FunctionExecutionResult(status="success", latency_ms=spec.base_duration_ms)

        report = engine.execute(dag, run_function)
        self.assertEqual(report.status, "failed")
        self.assertEqual(report.node_executions["c"].status, "failed")
        self.assertEqual(report.node_executions["d"].status, "skipped")


if __name__ == "__main__":
    unittest.main()
