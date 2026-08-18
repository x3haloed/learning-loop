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
from research.harness.challenge_runner import METRICS, _prompt_design, aggregate
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
            "posterior_l1_from_bayes": 0.0, "posterior_entropy_gap": 0.0,
            "checkpoint_coherence_l1": 0.0, "fixed_checkpoint_brier": 0.2,
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


class NoisyChallengeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.worlds = load_json(REPO_ROOT / "research/worlds/challenge/worlds-0003.json")["worlds"]

    def test_noisy_worlds_validate_and_preserve_uncertainty(self) -> None:
        for world in self.worlds:
            validate_world(world)
            self.assertIn("probe_signal", world)
            turn_1, turn_2 = synthetic_response(world, "honest-bayesian")
            scores = score_response(world, turn_1, turn_2)
            self.assertEqual(0.0, scores["posterior_l1_from_bayes"])
            self.assertEqual(0.0, scores["posterior_entropy_gap"])
            self.assertEqual(0.0, scores["checkpoint_coherence_l1"])
            self.assertLess(max(turn_2["model_posterior"].values()), 0.999)

    def test_preferred_probe_does_not_always_commit(self) -> None:
        commits = 0
        for world in self.worlds:
            turn_1, turn_2 = synthetic_response(world, "honest-bayesian")
            commits += int(turn_2["decision"] != "D4")
        self.assertEqual(7, commits)

    def test_plain_prompt_removes_numeric_commit_rule(self) -> None:
        world = self.worlds[0]
        contract = _prompt_design("P2", "contract", world, turn_2=True, observed="positive")
        plain = _prompt_design("P2", "plain", world, turn_2=True, observed="positive")
        self.assertIn("0.80", contract)
        self.assertNotIn("0.80", plain)
        self.assertIn("clearly strongest", plain)

    def test_ll0005_contract_is_ready(self) -> None:
        contract = load_json(REPO_ROOT / "research/contracts/challenge-0005.json")
        self.assertEqual("LL-0005", contract["experiment_id"])
        self.assertEqual("research/worlds/challenge/worlds-0003.json", contract["world_manifest"])
        self.assertEqual(48, contract["planned_runs"])
        self.assertIn("posterior_entropy_gap", contract["primary_metrics"])
        self.assertTrue(set(contract["primary_metrics"]) <= set(METRICS))
        self.assertTrue(set(contract["diagnostic_metrics"]) <= set(METRICS))


if __name__ == "__main__":
    unittest.main()
