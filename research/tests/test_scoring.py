from __future__ import annotations

import copy
from pathlib import Path
import unittest

from research.harness.scoring import EvidenceError, load_json, qualify, score_evidence


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "research/contracts/evaluator-epoch-0001.json"
EVIDENCE = REPO_ROOT / "research/evidence/qualification/synthetic-reference-trajectories.json"


class RulerQualificationTests(unittest.TestCase):
    def test_frozen_reference_controls_qualify_the_ruler(self) -> None:
        result = qualify(CONTRACT, EVIDENCE)
        self.assertTrue(result.passed)
        self.assertEqual(15, len(result.assertions))

    def test_ritual_volume_does_not_imply_outcome_quality(self) -> None:
        metrics = score_evidence(load_json(EVIDENCE))
        ritual = metrics["ritualistic"]
        adaptive = metrics["adaptive-reference"]
        self.assertGreater(ritual["receipt_total"], adaptive["receipt_total"])
        self.assertLess(ritual["receipt_consequence_rate"], adaptive["receipt_consequence_rate"])
        self.assertLess(ritual["task_fitness"], adaptive["task_fitness"])

    def test_self_selected_error_can_reward_evasion(self) -> None:
        metrics = score_evidence(load_json(EVIDENCE))
        evasive = metrics["error-averse"]
        adaptive = metrics["adaptive-reference"]
        self.assertLess(evasive["selected_prediction_brier"], adaptive["selected_prediction_brier"])
        self.assertGreater(evasive["fixed_checkpoint_brier"], adaptive["fixed_checkpoint_brier"])

    def test_visible_proxy_can_disagree_with_endpoint(self) -> None:
        metrics = score_evidence(load_json(EVIDENCE))
        local = metrics["local-optimizer"]
        adaptive = metrics["adaptive-reference"]
        self.assertGreater(local["visible_task_fitness"], adaptive["visible_task_fitness"])
        self.assertLess(local["task_fitness"], adaptive["task_fitness"])
        self.assertLess(local["worst_slice_fitness"], adaptive["worst_slice_fitness"])

    def test_invalid_probability_fails_closed(self) -> None:
        evidence = copy.deepcopy(load_json(EVIDENCE))
        evidence["controls"][0]["fixed_checkpoint_predictions"][0]["probability"] = 1.5
        with self.assertRaises(EvidenceError):
            score_evidence(evidence)

    def test_consequential_count_cannot_exceed_total(self) -> None:
        evidence = copy.deepcopy(load_json(EVIDENCE))
        evidence["controls"][0]["contacts"] = {"total": 1, "consequential": 2}
        with self.assertRaises(EvidenceError):
            score_evidence(evidence)


if __name__ == "__main__":
    unittest.main()
