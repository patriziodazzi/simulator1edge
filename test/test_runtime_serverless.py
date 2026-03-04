from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from simulator1edge.runtime.serverless import ServerlessRuntime
from simulator1edge.workflow.dag import WorkflowDAG
from simulator1edge.workflow.engine import WorkflowExecutionEngine
from simulator1edge.workflow.model import FunctionSpec


class ServerlessRuntimeTests(unittest.TestCase):
    def test_cold_then_warm_for_same_image_within_ttl(self):
        runtime = ServerlessRuntime(cold_start_overhead_ms=100, warm_ttl_ms=1000, image_pull_latency_ms=25)
        fn = FunctionSpec(name="f1", image="imgA", base_duration_ms=10)

        first = runtime.invoke(fn, start_ms=0)
        second = runtime.invoke(fn, start_ms=200)

        self.assertTrue(first.cold_start)
        self.assertFalse(second.cold_start)
        self.assertEqual(first.latency_ms, 135)   # 10 + 100 + 25
        self.assertEqual(second.latency_ms, 10)   # warm + cached image

    def test_warm_container_expires_after_ttl(self):
        runtime = ServerlessRuntime(cold_start_overhead_ms=80, warm_ttl_ms=100, image_pull_latency_ms=0)
        fn = FunctionSpec(name="f1", image="imgA", base_duration_ms=10)

        first = runtime.invoke(fn, start_ms=0)
        second = runtime.invoke(fn, start_ms=50)
        third = runtime.invoke(fn, start_ms=300)

        self.assertTrue(first.cold_start)
        self.assertFalse(second.cold_start)
        self.assertTrue(third.cold_start)

    def test_image_cache_eviction_triggers_new_pull(self):
        runtime = ServerlessRuntime(
            cold_start_overhead_ms=0,
            warm_ttl_ms=1_000,
            image_pull_latency_ms=20,
            max_cached_images=1,
        )
        fn_a = FunctionSpec(name="a", image="imgA", base_duration_ms=10)
        fn_b = FunctionSpec(name="b", image="imgB", base_duration_ms=10)

        a1 = runtime.invoke(fn_a, start_ms=0)
        runtime.invoke(fn_b, start_ms=10)
        a2 = runtime.invoke(fn_a, start_ms=20)

        self.assertEqual(a1.latency_ms, 30)
        self.assertEqual(a2.latency_ms, 30)
        self.assertGreaterEqual(runtime.metrics().image_cache_evictions, 1)

    def test_engine_supports_runtime_with_start_time(self):
        dag = WorkflowDAG("wf")
        dag.add_node(FunctionSpec(name="a", image="imgA", base_duration_ms=10))
        dag.add_node(FunctionSpec(name="b", image="imgA", base_duration_ms=10))
        dag.add_dependency("a", "b")

        runtime = ServerlessRuntime(cold_start_overhead_ms=50, warm_ttl_ms=1_000, image_pull_latency_ms=0)
        engine = WorkflowExecutionEngine()
        report = engine.execute(dag, runtime.invoke)

        self.assertEqual(report.status, "success")
        self.assertEqual(report.total_latency_ms, 70)  # a:60 cold, b:10 warm
        self.assertTrue(report.node_executions["a"].cold_start)
        self.assertFalse(report.node_executions["b"].cold_start)


if __name__ == "__main__":
    unittest.main()
