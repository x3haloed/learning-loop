from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from research.harness.pilot import RunSpec, aggregate, prepare_isolated_codex_home, score_run
from research.harness.scoring import load_json


REPO_ROOT = Path(__file__).resolve().parents[2]
WORLDS = load_json(REPO_ROOT / "research/worlds/pilot/worlds.json")


class PilotHarnessTests(unittest.TestCase):
    def test_factorial_contract_has_24_unique_runs(self) -> None:
        contract = load_json(REPO_ROOT / "research/contracts/pilot-0002.json")
        specs = [
            RunSpec(condition=condition, world_id=world, repetition=repetition)
            for repetition in range(1, contract["repetitions"] + 1)
            for world in contract["worlds"]
            for condition in contract["conditions"]
        ]
        self.assertEqual(24, len(specs))
        self.assertEqual(24, len({spec.run_id for spec in specs}))
        self.assertEqual("gpt-5.6-luna", contract["model"])
        self.assertEqual("LL-0002", contract["experiment_id"])

    def test_perfect_world_answers_score_perfectly(self) -> None:
        for world in WORLDS["worlds"]:
            oracle = world["oracle"]
            probe = oracle["preferred_probe"]
            turn_1 = {"probe_choice": probe}
            turn_2 = {
                "model_choice": oracle["model_choice"],
                "probabilities": {key: float(value) for key, value in oracle["checkpoint_outcomes"].items()},
                "decision": oracle["decision"],
                "next_action": oracle["next_action"][probe],
            }
            scores = score_run(world, turn_1, turn_2)
            self.assertEqual(1.0, scores["probe_value"])
            self.assertEqual(0.0, scores["fixed_checkpoint_brier"])
            self.assertEqual(1.0, scores["model_accuracy"])
            self.assertEqual(1.0, scores["decision_accuracy"])
            self.assertEqual(1.0, scores["next_action_accuracy"])

    def test_aggregate_keeps_harness_failures_visible(self) -> None:
        complete = {
            "condition": "a",
            "status": "complete",
            "scores": {
                "probe_value": 1.0,
                "preferred_probe": 1.0,
                "fixed_checkpoint_brier": 0.0,
                "model_accuracy": 1.0,
                "decision_accuracy": 1.0,
                "next_action_accuracy": 1.0,
            },
        }
        failure = {"condition": "a", "status": "harness-failure"}
        result = aggregate([complete, failure])
        self.assertEqual(2, result["planned_runs"])
        self.assertEqual(1, result["harness_failures"])
        self.assertEqual(1, result["conditions"]["a"]["harness_failures"])

    def test_isolated_home_copies_only_auth(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            target = root / "target"
            source.mkdir()
            (source / "auth.json").write_text(json.dumps({"token": "fixture"}), encoding="utf-8")
            (source / "config.toml").write_text("model = 'wrong'", encoding="utf-8")
            prepare_isolated_codex_home(source, target)
            self.assertEqual(["auth.json"], sorted(path.name for path in target.iterdir()))


if __name__ == "__main__":
    unittest.main()
