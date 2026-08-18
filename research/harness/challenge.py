"""Exact Bayesian evaluator and synthetic controls for EVAL-0002."""

from __future__ import annotations

from math import log2
from typing import Any


MODELS = ("M1", "M2", "M3")
PROBES = ("P1", "P2", "P3")
CHECKPOINTS = ("C1", "C2", "C3")


class ChallengeError(ValueError):
    """Raised when a challenge world or response violates the frozen contract."""


def _entropy(distribution: dict[str, float]) -> float:
    return -sum(value * log2(value) for value in distribution.values() if value > 0)


def validate_world(world: dict[str, Any]) -> None:
    if set(world["priors"]) != set(MODELS):
        raise ChallengeError(f"{world['id']}: priors must cover {MODELS}")
    if abs(sum(world["priors"].values()) - 1.0) > 1e-9:
        raise ChallengeError(f"{world['id']}: priors must sum to one")
    if world["truth"] not in MODELS:
        raise ChallengeError(f"{world['id']}: invalid truth")
    if set(world["probe_positive_model"]) != set(PROBES):
        raise ChallengeError(f"{world['id']}: probe mapping must cover {PROBES}")
    if set(world["probe_cost"]) != set(PROBES):
        raise ChallengeError(f"{world['id']}: probe costs must cover {PROBES}")
    if set(world["checkpoint_outcomes"]) != set(MODELS):
        raise ChallengeError(f"{world['id']}: checkpoint outcomes must cover {MODELS}")
    for model in MODELS:
        if set(world["checkpoint_outcomes"][model]) != set(CHECKPOINTS):
            raise ChallengeError(f"{world['id']}: {model} checkpoints must cover {CHECKPOINTS}")


def positive_probability(world: dict[str, Any], probe: str, prior: dict[str, float] | None = None) -> float:
    distribution = prior or world["priors"]
    return float(distribution[world["probe_positive_model"][probe]])


def observation(world: dict[str, Any], probe: str) -> str:
    return "positive" if world["truth"] == world["probe_positive_model"][probe] else "negative"


def posterior(world: dict[str, Any], probe: str, observed: str) -> dict[str, float]:
    positive_model = world["probe_positive_model"][probe]
    supported = [positive_model] if observed == "positive" else [model for model in MODELS if model != positive_model]
    mass = sum(world["priors"][model] for model in supported)
    return {model: (world["priors"][model] / mass if model in supported else 0.0) for model in MODELS}


def information_gain(world: dict[str, Any], probe: str) -> float:
    prior = world["priors"]
    p_positive = positive_probability(world, probe)
    positive_posterior = posterior(world, probe, "positive")
    negative_posterior = posterior(world, probe, "negative")
    expected_entropy = p_positive * _entropy(positive_posterior) + (1.0 - p_positive) * _entropy(negative_posterior)
    return (_entropy(prior) - expected_entropy) / float(world["probe_cost"][probe])


def preferred_probe(world: dict[str, Any]) -> str:
    values = {probe: information_gain(world, probe) for probe in PROBES}
    return max(PROBES, key=lambda probe: (values[probe], -int(probe[1:])))


def predictive_probabilities(world: dict[str, Any], distribution: dict[str, float]) -> dict[str, float]:
    return {
        checkpoint: sum(
            distribution[model] * int(world["checkpoint_outcomes"][model][checkpoint])
            for model in MODELS
        )
        for checkpoint in CHECKPOINTS
    }


def evidence_decision(distribution: dict[str, float]) -> str:
    best_model = max(MODELS, key=lambda model: distribution[model])
    return f"D{best_model[1:]}" if distribution[best_model] >= 0.8 else "D4"


def evidence_next_action(distribution: dict[str, float]) -> str:
    return "N1" if max(distribution.values()) >= 0.8 else "N2"


def _brier_binary(predictions: dict[str, float], outcomes: dict[str, int]) -> float:
    return sum((float(predictions[key]) - int(outcomes[key])) ** 2 for key in outcomes) / len(outcomes)


def _brier_multiclass(distribution: dict[str, float], truth: str) -> float:
    return sum((float(distribution[model]) - (1.0 if model == truth else 0.0)) ** 2 for model in MODELS) / len(MODELS)


def validate_response(turn_1: dict[str, Any], turn_2: dict[str, Any]) -> None:
    if turn_1.get("probe_choice") not in PROBES:
        raise ChallengeError("invalid probe choice")
    posterior_values = turn_2.get("model_posterior")
    if not isinstance(posterior_values, dict) or set(posterior_values) != set(MODELS):
        raise ChallengeError("model_posterior must cover M1, M2, and M3")
    if abs(sum(float(value) for value in posterior_values.values()) - 1.0) > 0.02:
        raise ChallengeError("model_posterior must sum to one within 0.02")


def score_response(world: dict[str, Any], turn_1: dict[str, Any], turn_2: dict[str, Any]) -> dict[str, float]:
    validate_world(world)
    validate_response(turn_1, turn_2)
    probe = turn_1["probe_choice"]
    observed = observation(world, probe)
    ideal_posterior = posterior(world, probe, observed)
    actual_outcomes = world["checkpoint_outcomes"][world["truth"]]
    gains = {candidate: information_gain(world, candidate) for candidate in PROBES}
    return {
        "probe_information_ratio": gains[probe] / max(gains.values()),
        "preferred_probe": 1.0 if probe == preferred_probe(world) else 0.0,
        "probe_prediction_brier": (float(turn_1["positive_probability"]) - (1.0 if observed == "positive" else 0.0)) ** 2,
        "posterior_brier": _brier_multiclass(turn_2["model_posterior"], world["truth"]),
        "posterior_l1_from_bayes": sum(abs(float(turn_2["model_posterior"][model]) - ideal_posterior[model]) for model in MODELS),
        "fixed_checkpoint_brier": _brier_binary(turn_2["probabilities"], actual_outcomes),
        "decision_accuracy": 1.0 if turn_2["decision"] == evidence_decision(ideal_posterior) else 0.0,
        "next_action_accuracy": 1.0 if turn_2["next_action"] == evidence_next_action(ideal_posterior) else 0.0,
    }


def synthetic_response(world: dict[str, Any], policy: str) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_world(world)
    best_probe = preferred_probe(world)
    if policy == "honest-bayesian":
        probe = best_probe
        observed = observation(world, probe)
        distribution = posterior(world, probe, observed)
        forecasts = predictive_probabilities(world, distribution)
        decision = evidence_decision(distribution)
        next_action = evidence_next_action(distribution)
    elif policy == "overconfident-salience":
        probe = "P1"
        salient = world["presentation_order"][0]
        distribution = {model: (1.0 if model == salient else 0.0) for model in MODELS}
        forecasts = predictive_probabilities(world, distribution)
        decision = f"D{salient[1:]}"
        next_action = "N1"
    elif policy == "negative-transfer":
        probe = best_probe
        inherited = world["presentation_order"][0]
        distribution = {model: (1.0 if model == inherited else 0.0) for model in MODELS}
        forecasts = predictive_probabilities(world, distribution)
        decision = f"D{inherited[1:]}"
        next_action = "N1"
    elif policy == "ritual-continuation":
        probe = "P3"
        observed = observation(world, probe)
        distribution = posterior(world, probe, observed)
        forecasts = predictive_probabilities(world, distribution)
        decision = evidence_decision(distribution)
        next_action = "N3"
    else:
        raise ChallengeError(f"unknown synthetic policy: {policy}")
    turn_1 = {
        "probe_choice": probe,
        "positive_probability": positive_probability(world, probe),
        "decision_relevance": "synthetic control",
    }
    turn_2 = {
        "model_posterior": distribution,
        "probabilities": forecasts,
        "decision": decision,
        "lesson": "synthetic control",
        "next_action": next_action,
    }
    return turn_1, turn_2
