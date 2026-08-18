from __future__ import annotations

import json
from pathlib import Path
import unittest

from research.harness.scoring import file_sha256, load_json, score_evidence


REPO_ROOT = Path(__file__).resolve().parents[2]


class ContractIntegrityTests(unittest.TestCase):
    def test_normative_authorities_exist(self) -> None:
        for filename in ("TARGET.md", "RED_LINES.md", "RESEARCH_PROGRAM.md"):
            path = REPO_ROOT / filename
            self.assertTrue(path.is_file(), filename)
            self.assertGreater(path.stat().st_size, 0, filename)

    def test_controls_evidence_and_instruction_files_agree(self) -> None:
        manifest = load_json(REPO_ROOT / "research/controls/manifest.json")
        evidence = load_json(REPO_ROOT / "research/evidence/qualification/synthetic-reference-trajectories.json")
        manifest_ids = {item["id"] for item in manifest["controls"]}
        evidence_ids = {item["id"] for item in evidence["controls"]}
        self.assertEqual(manifest_ids, evidence_ids)
        self.assertEqual(len(manifest_ids), len(manifest["controls"]))
        for control in manifest["controls"]:
            instruction_path = (REPO_ROOT / control["instruction_file"]).resolve()
            self.assertTrue(instruction_path.is_relative_to(REPO_ROOT.resolve()))
            self.assertTrue(instruction_path.is_file(), instruction_path)

    def test_evaluator_metric_catalog_matches_implementation(self) -> None:
        contract = load_json(REPO_ROOT / "research/contracts/evaluator-epoch-0001.json")
        evidence = load_json(REPO_ROOT / "research/evidence/qualification/synthetic-reference-trajectories.json")
        metrics = score_evidence(evidence)
        implemented = set(next(iter(metrics.values())))
        lower = set(contract["metrics"]["lower_is_better"])
        higher = set(contract["metrics"]["higher_is_better"])
        self.assertFalse(lower & higher)
        self.assertEqual(implemented, lower | higher | {"receipt_total"})

    def test_world_metrics_are_implemented(self) -> None:
        worlds = load_json(REPO_ROOT / "research/worlds/qualification/manifest.json")
        evidence = load_json(REPO_ROOT / "research/evidence/qualification/synthetic-reference-trajectories.json")
        implemented = set(next(iter(score_evidence(evidence).values())))
        ids = [world["id"] for world in worlds["worlds"]]
        self.assertEqual(len(ids), len(set(ids)))
        for world in worlds["worlds"]:
            self.assertTrue(set(world["primary_metrics"]) <= implemented, world["id"])

    def test_experiment_record_preserves_synthetic_boundary(self) -> None:
        record = load_json(REPO_ROOT / "research/experiments/LL-0000-ruler-qualification.json")
        self.assertEqual("ruler-qualified", record["disposition"])
        self.assertFalse(record["environment"]["subject_agents_executed"])
        self.assertEqual("DISCOVERY", record["allocation"]["class"])

    def test_ll0000_content_hashes_resolve(self) -> None:
        record = load_json(REPO_ROOT / "research/experiments/LL-0000-ruler-qualification.json")
        candidate_paths = {
            "target": "TARGET.md",
            "red_lines": "RED_LINES.md",
            "research_program": "RESEARCH_PROGRAM.md",
            "control_manifest": "research/controls/manifest.json",
        }
        for name, relative_path in candidate_paths.items():
            self.assertEqual(record["candidate_hashes"][name], file_sha256(REPO_ROOT / relative_path))
        self.assertEqual(
            record["allocation"]["manifest_hash"],
            file_sha256(REPO_ROOT / "research/worlds/qualification/manifest.json"),
        )
        for item in record["raw_evidence"]:
            self.assertEqual(item["sha256"], file_sha256(REPO_ROOT / item["path"]))


if __name__ == "__main__":
    unittest.main()
