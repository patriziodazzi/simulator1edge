from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from simulator1edge.workflow.dag import WorkflowDAG
from simulator1edge.workflow.model import FunctionSpec


class WorkflowDagTests(unittest.TestCase):
    def _node(self, name: str) -> FunctionSpec:
        return FunctionSpec(name=name, image="img", base_duration_ms=10)

    def test_topological_layers_for_fan_out_fan_in(self):
        dag = WorkflowDAG("wf")
        for name in ["a", "b", "c", "d"]:
            dag.add_node(self._node(name))
        dag.add_dependency("a", "b")
        dag.add_dependency("a", "c")
        dag.add_dependency("b", "d")
        dag.add_dependency("c", "d")

        self.assertEqual(dag.topological_layers(), [["a"], ["b", "c"], ["d"]])

    def test_cycle_detection_raises(self):
        dag = WorkflowDAG("wf")
        for name in ["a", "b", "c"]:
            dag.add_node(self._node(name))
        dag.add_dependency("a", "b")
        dag.add_dependency("b", "c")

        with self.assertRaises(ValueError):
            dag.add_dependency("c", "a")

    def test_duplicate_node_raises(self):
        dag = WorkflowDAG("wf")
        dag.add_node(self._node("a"))
        with self.assertRaises(ValueError):
            dag.add_node(self._node("a"))


if __name__ == "__main__":
    unittest.main()
