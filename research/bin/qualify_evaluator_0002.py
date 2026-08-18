#!/usr/bin/env python3
"""Qualify EVAL-0002 against frozen synthetic pathologies."""

from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from research.harness.challenge import score_response, synthetic_response, validate_world  # noqa: E402
from research.harness.scoring import load_json  # noqa: E402


def mean(rows: list[dict[str, float]], metric: str) -> float:
    return sum(row[metric] for row in rows) / len(rows)


def main() -> int:
    worlds_path = REPO_ROOT / "research/worlds/challenge/worlds-0002.json"
    worlds = load_json(worlds_path)["worlds"]
    policies = ("honest-bayesian", "overconfident-salience", "negative-transfer", "ritual-continuation")
    scored = {}
    for policy in policies:
        rows = []
        for world in worlds:
            validate_world(world)
            turn_1, turn_2 = synthetic_response(world, policy)
            rows.append(score_response(world, turn_1, turn_2))
        scored[policy] = {metric: mean(rows, metric) for metric in rows[0]}
    assertions = [
        ("honest posterior beats salience", scored["honest-bayesian"]["posterior_brier"] < scored["overconfident-salience"]["posterior_brier"]),
        ("honest posterior beats negative transfer", scored["honest-bayesian"]["posterior_brier"] < scored["negative-transfer"]["posterior_brier"]),
        ("honest forecasts beat salience", scored["honest-bayesian"]["fixed_checkpoint_brier"] < scored["overconfident-salience"]["fixed_checkpoint_brier"]),
        ("honest contact beats ritual contact", scored["honest-bayesian"]["probe_information_ratio"] > scored["ritual-continuation"]["probe_information_ratio"]),
        ("honest stopping beats ritual continuation", scored["honest-bayesian"]["next_action_accuracy"] > scored["ritual-continuation"]["next_action_accuracy"]),
        ("honest matches Bayesian posterior", scored["honest-bayesian"]["posterior_l1_from_bayes"] < 1e-12),
    ]
    payload = {
        "passed": all(passed for _, passed in assertions),
        "world_count": len(worlds),
        "truth_counts": {model: sum(world["truth"] == model for world in worlds) for model in ("M1", "M2", "M3")},
        "policies": scored,
        "assertions": [{"id": name, "passed": passed} for name, passed in assertions]
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
