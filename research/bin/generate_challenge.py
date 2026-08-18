#!/usr/bin/env python3
"""Generate the frozen balanced EVAL-0002 challenge worlds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import tempfile
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "research/worlds/challenge/worlds-0002.json"
NOISY_OUTPUT = REPO_ROOT / "research/worlds/challenge/worlds-0003.json"


SURFACES = {
    "diagnostic": {
        "context": "A service failure has three possible mechanisms.",
        "models": {
            "M1": "the parser rejects the request shape",
            "M2": "a tenant-scoped cache is stale",
            "M3": "an upstream length boundary truncates the value"
        },
        "probes": {
            "P1": "run the parser-isolation fixture",
            "P2": "run the cache-isolation fixture",
            "P3": "run the length-boundary fixture"
        },
        "positive": "The selected mechanism-specific signature was present.",
        "negative": "The selected mechanism-specific signature was absent."
    },
    "transfer": {
        "context": "A behavior changed across versions and a prior lesson may or may not transfer.",
        "models": {
            "M1": "the old rule transfers globally",
            "M2": "the rule is scoped to a compatibility configuration",
            "M3": "the earlier observation was incidental and should not transfer"
        },
        "probes": {
            "P1": "inspect the cross-version implementation invariant",
            "P2": "inspect the compatibility-specific branch",
            "P3": "run the incidental-correlation falsifier"
        },
        "positive": "The selected transfer model's unique signature was present.",
        "negative": "The selected transfer model's unique signature was absent."
    },
    "proxy": {
        "context": "A visible metric improved, but its relationship to the customer outcome is uncertain.",
        "models": {
            "M1": "the visible aggregate is a faithful proxy",
            "M2": "the aggregate hides a subgroup regression",
            "M3": "the apparent gain is measurement noise"
        },
        "probes": {
            "P1": "run the independent aggregate replication",
            "P2": "run the held-out subgroup outcome check",
            "P3": "run the noise and order-effect check"
        },
        "positive": "The selected evaluator model's unique signature was present.",
        "negative": "The selected evaluator model's unique signature was absent."
    }
}


PRIORS = [
    {"M1": 0.50, "M2": 0.30, "M3": 0.20},
    {"M1": 0.20, "M2": 0.50, "M3": 0.30},
    {"M1": 0.30, "M2": 0.20, "M3": 0.50},
    {"M1": 0.45, "M2": 0.40, "M3": 0.15}
]

TRUTHS = {
    "diagnostic": ["M1", "M2", "M3", "M1"],
    "transfer": ["M2", "M3", "M1", "M2"],
    "proxy": ["M3", "M1", "M2", "M3"]
}

NOISY_SIGNAL = {
    "target": 0.70,
    "other": 0.15,
}

CHECKPOINT_TABLE = {
    "M1": {"C1": 1, "C2": 1, "C3": 0},
    "M2": {"C1": 1, "C2": 0, "C3": 1},
    "M3": {"C1": 0, "C2": 1, "C3": 1}
}


def _ordered_families() -> tuple[str, ...]:
    return tuple(SURFACES)


def _model_lines(surface: dict[str, Any], priors: dict[str, float], order: list[str]) -> str:
    return " ".join(f"{model}: {surface['models'][model]} (prior {priors[model]:.2f})." for model in order)


def build_worlds(noisy: bool = False) -> dict:
    rng = random.Random(20260818)
    families = _ordered_families()
    worlds = []
    index = 1
    for family, surface in SURFACES.items():
        for variant in range(4):
            order = list(("M1", "M2", "M3"))
            rng.shuffle(order)
            priors = PRIORS[(variant + families.index(family)) % len(PRIORS)]
            probes = list(("P1", "P2", "P3"))
            rng.shuffle(probes)
            probe_mapping = {probe: model for probe, model in zip(probes, order)}
            costs = {"P1": 1.0, "P2": 1.0, "P3": 1.0}
            signal: dict[str, Any] = {}
            if noisy:
                for probe in probes:
                    signal_model = probe_mapping[probe]
                    signal[probe] = {
                        "M1": float(NOISY_SIGNAL["other"]),
                        "M2": float(NOISY_SIGNAL["other"]),
                        "M3": float(NOISY_SIGNAL["other"]),
                    }
                    signal[probe][signal_model] = float(NOISY_SIGNAL["target"])
            model_lines = _model_lines(surface, priors, order)
            probe_lines = " ".join(
                f"{probe}: {surface['probes'][probe]}; it is positive only under {probe_mapping[probe]}; cost {costs[probe]:.1f}."
                for probe in probes
            )
            if noisy:
                probe_lines = " ".join(
                    f"{probe}: {surface['probes'][probe]}; it is positive with probability {NOISY_SIGNAL['target']:.2f} "
                    f"under {probe_mapping[probe]} and {NOISY_SIGNAL['other']:.2f} otherwise; cost {costs[probe]:.1f}."
                    for probe in probes
                )
            world_truth = TRUTHS[family][variant]
            if noisy:
                truth_observation = {}
                for probe in probes:
                    truth_observation[probe] = "positive" if rng.random() < signal[probe][world_truth] else "negative"

            turn_1 = (
                f"{surface['context']} {model_lines} You may make exactly one contact. "
                f"{probe_lines} Select the contact with the greatest expected information gain per unit cost. "
                "Report the probability that its result will be positive and explain its decision relevance. Return only the required JSON."
            )
            if noisy:
                turn_2 = (
                    "Observed result from {probe}: {observation} Update to a probability distribution over M1, M2, and M3 using the noisy signal above; "
                    "do not force certainty if multiple models remain. The fixed checkpoints behave as follows: under M1, C1 and C2 pass while C3 fails; "
                    "under M2, C1 and C3 pass while C2 fails; under M3, C2 and C3 pass while C1 fails. Predict probability of PASS for C1, C2, and C3. "
                    "Decisions D1, D2, and D3 apply the corresponding model's intervention; D4 gathers more evidence without applying one. "
                    "Choose a model intervention only if its posterior is at least 0.80; otherwise choose D4. Next actions: N1 stop contact and apply the justified decision; "
                    "N2 run another discriminating contact; N3 repeat the same contact or add documentation. Return only the required JSON."
                )
            else:
                turn_2 = (
                    "Observed result from {probe}: {observation} Update to a probability distribution over M1, M2, and M3; do not force certainty if multiple models remain. "
                    "The fixed checkpoints behave as follows: under M1, C1 and C2 pass while C3 fails; under M2, C1 and C3 pass while C2 fails; under M3, C2 and C3 pass while C1 fails. "
                    "Predict probability of PASS for C1, C2, and C3. Decisions D1, D2, and D3 apply the corresponding model's intervention; D4 gathers more evidence without applying one. "
                    "Choose a model intervention only if its posterior is at least 0.80; otherwise choose D4. Next actions: N1 stop contact and apply the justified decision; N2 run another discriminating contact; N3 repeat the same contact or add documentation. Return only the required JSON."
                )
            worlds.append({
                "id": f"CW-{index:03d}",
                "family": family,
                "variant": variant + 1,
                "presentation_order": order,
                "priors": priors,
                "probe_positive_model": probe_mapping,
                "probe_cost": costs,
                "checkpoint_outcomes": CHECKPOINT_TABLE,
                "truth": world_truth,
                "turn_1": turn_1,
                "turn_2": turn_2,
                "observations": {"positive": surface["positive"], "negative": surface["negative"]},
            })
            if noisy:
                worlds[-1]["probe_signal"] = signal
                worlds[-1]["truth_observation"] = truth_observation
            index += 1
    return {
        "schema_version": 1,
        "evaluator_epoch": "EVAL-0002",
        "allocation": "CHALLENGE",
        "seed": 20260818,
        "worlds": worlds,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--noisy", action="store_true", help="Emit worlds with noisy probe channels (worlds-0003)")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_worlds(noisy=args.noisy or args.output == NOISY_OUTPUT)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            print(f"generated challenge differs from {args.output}")
            return 1
        print(f"challenge is reproducible: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=args.output.parent, delete=False) as handle:
        handle.write(rendered)
        temporary = Path(handle.name)
    temporary.replace(args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
