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


def _model_support(world: dict[str, Any], probe: str) -> dict[str, float]:
    noisy = world.get("probe_signal")
    if noisy is None:
        return {model: 1.0 if model == world["probe_positive_model"][probe] else 0.0 for model in MODELS}
    signal = noisy[probe]
    return {model: float(signal[model]) for model in MODELS}


def validate_world(world: dict[str, Any]) -> None:
    if set(world["priors"]) != set(MODELS):
        raise ChallengeError(f"{world['id']}: priors must cover {MODELS}")
    if abs(sum(world["priors"].values()) - 1.0) > 1e-9:
        raise ChallengeError(f"{world['id']}: priors must sum to one")
    if world["truth"] not in MODELS:
        raise ChallengeError(f"{world['id']}: invalid truth")
    if set(world["probe_positive_model"]) != set(PROBES):
        raise ChallengeError(f"{world['id']}: probe mapping must cover {PROBES}")
    noisy = world.get("probe_signal")
    if noisy is not None:
        if not isinstance(noisy, dict):
            raise ChallengeError(f"{world['id']}: probe_signal must be an object")
        if set(noisy) != set(PROBES):
            raise ChallengeError(f"{world['id']}: probe_signal must cover {PROBES}")
        for probe in PROBES:
            if set(noisy[probe]) != set(MODELS):
                raise ChallengeError(f"{world['id']}: probe_signal[{probe}] must cover {MODELS}")
            total = sum(noisy[probe][model] for model in MODELS)
            if not all(0 <= noisy[probe][model] <= 1 for model in MODELS):
                raise ChallengeError(f"{world['id']}: probe_signal[{probe}] values must be in [0, 1]")
            if abs(total - 1.0) > 1e-9:
                raise ChallengeError(f"{world['id']}: probe_signal[{probe}] probabilities must sum to one")
        if "truth_observation" not in world:
            raise ChallengeError(f"{world['id']}: noisy worlds require truth_observation")
        truth_observation = world["truth_observation"]
        if isinstance(truth_observation, str):
            if truth_observation not in ("positive", "negative"):
                raise ChallengeError(f"{world['id']}: truth_observation must be positive or negative")
        elif isinstance(truth_observation, dict):
            if set(truth_observation) != set(PROBES):
                raise ChallengeError(f"{world['id']}: truth_observation must cover {PROBES}")
            for probe in PROBES:
                if truth_observation[probe] not in ("positive", "negative"):
                    raise ChallengeError(f"{world['id']}: truth_observation[{probe}] must be positive or negative")
        else:
            raise ChallengeError(f"{world['id']}: truth_observation must be a string or a probe-object map")
    if set(world["probe_cost"]) != set(PROBES):
        raise ChallengeError(f"{world['id']}: probe costs must cover {PROBES}")
    if set(world["checkpoint_outcomes"]) != set(MODELS):
        raise ChallengeError(f"{world['id']}: checkpoint outcomes must cover {MODELS}")
    for model in MODELS:
        if set(world["checkpoint_outcomes"][model]) != set(CHECKPOINTS):
            raise ChallengeError(f"{world['id']}: {model} checkpoints must cover {CHECKPOINTS}")


def positive_probability(world: dict[str, Any], probe: str, prior: dict[str, float] | None = None) -> float:
    distribution = prior or world["priors"]
    if world.get("probe_signal") is not None:
        return sum(float(distribution[model]) * float(world["probe_signal"][probe][model]) for model in MODELS)
    return float(distribution[world["probe_positive_model"][probe]])


def _posterior_entropy(distribution: dict[str, float]) -> float:
    return _entropy(distribution)


def signal_likelihood(world: dict[str, Any], probe: str, observed: str) -> dict[str, float]:
    support = _model_support(world, probe)
    if observed == "positive":
        return support
    return {model: 1.0 - support[model] for model in MODELS}


def observation(world: dict[str, Any], probe: str) -> str:
    if "truth_observation" in world:
        truth_observation = world["truth_observation"]
        if isinstance(truth_observation, dict):
            return truth_observation[probe]
        return truth_observation
    return "positive" if world["truth"] == world["probe_positive_model"][probe] else "negative"


def posterior(world: dict[str, Any], probe: str, observed: str) -> dict[str, float]:
    evidence = signal_likelihood(world, probe, observed)
    mass = sum(world["priors"][model] * evidence[model] for model in MODELS)
    return {model: ((world["priors"][model] * evidence[model]) / mass if mass else 1.0 / len(MODELS))
            for model in MODELS}


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
        "posterior_entropy_gap": abs(_posterior_entropy(ideal_posterior) - _posterior_entropy(turn_2["model_posterior"])),
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
