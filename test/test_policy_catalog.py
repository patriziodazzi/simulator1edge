from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from simulator1edge.policies.catalog import (
    build_domain_policy,
    build_placement_policy,
)
from simulator1edge.policies.domain import SequentialDomainSelectionPolicy
from simulator1edge.policies.placement import (
    FirstCandidatePlacementPolicy,
    LeastLoadedPlacementPolicy,
    MostFreeMemoryPlacementPolicy,
)


class PolicyCatalogTests(unittest.TestCase):
    def test_build_known_placement_policies(self):
        self.assertIsInstance(build_placement_policy("first_candidate"), FirstCandidatePlacementPolicy)
        self.assertIsInstance(build_placement_policy("least_loaded"), LeastLoadedPlacementPolicy)
        self.assertIsInstance(build_placement_policy("most_free_memory"), MostFreeMemoryPlacementPolicy)

    def test_build_known_domain_policy(self):
        self.assertIsInstance(build_domain_policy("sequential"), SequentialDomainSelectionPolicy)

    def test_unknown_placement_policy_raises(self):
        with self.assertRaises(ValueError):
            build_placement_policy("does_not_exist")

    def test_unknown_domain_policy_raises(self):
        with self.assertRaises(ValueError):
            build_domain_policy("does_not_exist")


if __name__ == "__main__":
    unittest.main()
