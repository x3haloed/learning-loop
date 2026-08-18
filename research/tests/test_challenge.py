from __future__ import annotations

from pathlib import Path
import unittest

from research.harness.challenge import (
    evidence_decision,
    information_gain,
    posterior,
    preferred_probe,
    score_response,
    synthetic_response,
    validate_world,
)
from research.harness.challenge_runner import aggregate
from research.harness.scoring import load_json


REPO_ROOT = Path(__file__).resolve().parents[2]


class ChallengeEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.worlds = load_json(REPO_ROOT / "research/worlds/challenge/worlds-0002.json")["worlds"]

    def test_all_worlds_validate_and_truths_are_balanced(self) -> None:
        for world in self.worlds:
            validate_world(world)
        counts = {model: sum(world["truth"] == model for world in self.worlds) for model in ("M1", "M2", "M3")}
        self.assertEqual({"M1": 4, "M2": 4, "M3": 4}, counts)

    def test_preferred_probe_maximizes_information_per_cost(self) -> None:
        for world in self.worlds:
            chosen = preferred_probe(world)
            self.assertEqual(max(information_gain(world, probe) for probe in ("P1", "P2", "P3")), information_gain(world, chosen))

    def test_negative_observation_preserves_uncertainty(self) -> None:
        world = self.worlds[0]
        distribution = posterior(world, "P1", "negative")
        self.assertEqual(0.0, distribution[world["probe_positive_model"]["P1"]])
        self.assertAlmostEqual(1.0, sum(distribution.values()))

    def test_honest_control_matches_evidence_relative_decision(self) -> None:
        for world in self.worlds:
            turn_1, turn_2 = synthetic_response(world, "honest-bayesian")
            observed = "positive" if world["truth"] == world["probe_positive_model"][turn_1["probe_choice"]] else "negative"
            expected = evidence_decision(posterior(world, turn_1["probe_choice"], observed))
            self.assertEqual(expected, turn_2["decision"])
            self.assertEqual(0.0, score_response(world, turn_1, turn_2)["posterior_l1_from_bayes"])

    def test_live_contract_is_complete_factorial(self) -> None:
        contract = load_json(REPO_ROOT / "research/contracts/challenge-0003.json")
        self.assertEqual(contract["model"], "gpt-5.6-luna")
        self.assertEqual(contract["planned_runs"], 48)
        self.assertEqual(
            contract["planned_runs"],
            len(contract["conditions"]) * len(contract["worlds"]) * contract["repetitions"],
        )

    def test_live_aggregate_preserves_condition_and_family_views(self) -> None:
        scores = {
            "probe_information_ratio": 1.0, "preferred_probe": 1.0,
            "probe_prediction_brier": 0.1, "posterior_brier": 0.2,
            "posterior_l1_from_bayes": 0.0, "fixed_checkpoint_brier": 0.2,
            "decision_accuracy": 1.0, "next_action_accuracy": 1.0,
        }
        rows = [
            {"condition": "a", "family": "diagnostic", "status": "complete", "scores": scores},
            {"condition": "a", "family": "transfer", "status": "harness-failure"},
        ]
        summary = aggregate(rows)
        self.assertEqual(summary["planned_runs"], 2)
        self.assertEqual(summary["harness_failures"], 1)
        self.assertEqual(summary["conditions"]["a"]["metrics"]["posterior_brier"], 0.2)
        self.assertIn("diagnostic", summary["conditions"]["a"]["families"])


if __name__ == "__main__":
    unittest.main()
