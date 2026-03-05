from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from simulator1edge.workflow.loader import load_workflow_dag, workflow_dag_from_mapping


class WorkflowLoaderTests(unittest.TestCase):
    def test_load_workflow_dag_from_json_file(self):
        payload = {
            "name": "wf-json",
            "nodes": [
                {"name": "a", "image": "img-a", "base_duration_ms": 10},
                {"name": "b", "image": "img-b", "base_duration_ms": 20, "retries": 2},
            ],
            "dependencies": [["a", "b"]],
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "workflow.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            dag = load_workflow_dag(path)

        self.assertEqual(dag.name, "wf-json")
        self.assertEqual(dag.topological_layers(), [["a"], ["b"]])
        self.assertEqual(dag.nodes["b"].retries, 2)

    def test_workflow_dag_from_mapping_supports_dependency_objects(self):
        dag = workflow_dag_from_mapping(
            {
                "name": "wf-map",
                "functions": [
                    {"name": "a", "image": "img", "base_duration_ms": 10},
                    {"name": "b", "image": "img", "base_duration_ms": 10},
                ],
                "dependencies": [{"source": "a", "target": "b"}],
            }
        )

        self.assertEqual(dag.topological_layers(), [["a"], ["b"]])

    def test_loader_rejects_unsupported_extension(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "workflow.txt"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_workflow_dag(path)


if __name__ == "__main__":
    unittest.main()

