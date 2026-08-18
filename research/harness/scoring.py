"""Score frozen adaptive-loop trajectory evidence without third-party packages."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from statistics import fmean
from typing import Any


class EvidenceError(ValueError):
    """Raised when evidence violates the executable Stage 0 contract."""


@dataclass(frozen=True)
class QualificationResult:
    metrics: dict[str, dict[str, float]]
    assertions: list[dict[str, Any]]
    input_hashes: dict[str, str]

    @property
    def passed(self) -> bool:
        return all(item["passed"] for item in self.assertions)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def _unit_interval(value: Any, label: str) -> float:
    _require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{label} must be numeric")
    result = float(value)
    _require(0.0 <= result <= 1.0, f"{label} must be in [0, 1]")
    return result


def validate_evidence(evidence: Any) -> None:
    _require(isinstance(evidence, dict), "evidence must be an object")
    _require(evidence.get("schema_version") == 1, "unsupported evidence schema_version")
    _require(evidence.get("evidence_class") in {"synthetic-reference", "subject-run"}, "invalid evidence_class")
    controls = evidence.get("controls")
    _require(isinstance(controls, list) and controls, "controls must be a non-empty array")
    seen: set[str] = set()
    for index, control in enumerate(controls):
        label = f"controls[{index}]"
        _require(isinstance(control, dict), f"{label} must be an object")
        control_id = control.get("id")
        _require(isinstance(control_id, str) and control_id, f"{label}.id is required")
        _require(control_id not in seen, f"duplicate control id: {control_id}")
        seen.add(control_id)

        for field in ("selected_predictions", "fixed_checkpoint_predictions"):
            predictions = control.get(field)
            _require(isinstance(predictions, list) and predictions, f"{control_id}.{field} must be non-empty")
            for pred_index, prediction in enumerate(predictions):
                _require(isinstance(prediction, dict), f"{control_id}.{field}[{pred_index}] must be an object")
                _unit_interval(prediction.get("probability"), f"{control_id}.{field}[{pred_index}].probability")
                _require(prediction.get("outcome") in {0, 1}, f"{control_id}.{field}[{pred_index}].outcome must be 0 or 1")

        for field in ("transfer_outcomes", "visible_task_scores", "task_scores"):
            values = control.get(field)
            _require(isinstance(values, list) and values, f"{control_id}.{field} must be non-empty")
            for value_index, value in enumerate(values):
                _unit_interval(value, f"{control_id}.{field}[{value_index}]")

        slices = control.get("critical_slices")
        _require(isinstance(slices, dict) and slices, f"{control_id}.critical_slices must be non-empty")
        for slice_id, values in slices.items():
            _require(isinstance(values, list) and values, f"{control_id}.critical_slices.{slice_id} must be non-empty")
            for value_index, value in enumerate(values):
                _unit_interval(value, f"{control_id}.critical_slices.{slice_id}[{value_index}]")

        for field in ("contacts", "receipts"):
            pair = control.get(field)
            _require(isinstance(pair, dict), f"{control_id}.{field} must be an object")
            total = pair.get("total")
            consequential = pair.get("consequential")
            _require(isinstance(total, int) and total >= 0, f"{control_id}.{field}.total must be non-negative")
            _require(isinstance(consequential, int) and 0 <= consequential <= total, f"{control_id}.{field}.consequential must be between 0 and total")

        restraint = control.get("restraint")
        _require(isinstance(restraint, dict), f"{control_id}.restraint must be an object")
        cases = restraint.get("cases")
        actions = restraint.get("unnecessary_actions")
        _require(isinstance(cases, int) and cases > 0, f"{control_id}.restraint.cases must be positive")
        _require(isinstance(actions, int) and actions >= 0, f"{control_id}.restraint.unnecessary_actions must be non-negative")

        trigger = control.get("skill_trigger")
        _require(isinstance(trigger, dict), f"{control_id}.skill_trigger must be an object")
        for field in ("true_positive", "false_positive", "false_negative"):
            _require(isinstance(trigger.get(field), int) and trigger[field] >= 0, f"{control_id}.skill_trigger.{field} must be non-negative")


def _brier(predictions: list[dict[str, Any]]) -> float:
    return fmean((float(item["probability"]) - int(item["outcome"])) ** 2 for item in predictions)


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def score_control(control: dict[str, Any]) -> dict[str, float]:
    slice_means = [fmean(values) for values in control["critical_slices"].values()]
    trigger = control["skill_trigger"]
    tp = trigger["true_positive"]
    fp = trigger["false_positive"]
    fn = trigger["false_negative"]
    return {
        "selected_prediction_brier": _brier(control["selected_predictions"]),
        "fixed_checkpoint_brier": _brier(control["fixed_checkpoint_predictions"]),
        "transfer_rate": fmean(control["transfer_outcomes"]),
        "visible_task_fitness": fmean(control["visible_task_scores"]),
        "task_fitness": fmean(control["task_scores"]),
        "worst_slice_fitness": min(slice_means),
        "contact_precision": _ratio(control["contacts"]["consequential"], control["contacts"]["total"]),
        "receipt_total": float(control["receipts"]["total"]),
        "receipt_consequence_rate": _ratio(control["receipts"]["consequential"], control["receipts"]["total"]),
        "restraint_cost": _ratio(control["restraint"]["unnecessary_actions"], control["restraint"]["cases"]),
        "skill_precision": _ratio(tp, tp + fp),
        "skill_recall": _ratio(tp, tp + fn),
    }


def score_evidence(evidence: dict[str, Any]) -> dict[str, dict[str, float]]:
    validate_evidence(evidence)
    return {control["id"]: score_control(control) for control in evidence["controls"]}


def evaluate_assertions(contract: dict[str, Any], metrics: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    operators = {
        "lt": lambda lhs, rhs: lhs < rhs,
        "le": lambda lhs, rhs: lhs <= rhs,
        "gt": lambda lhs, rhs: lhs > rhs,
        "ge": lambda lhs, rhs: lhs >= rhs,
        "eq": lambda lhs, rhs: lhs == rhs,
    }
    results: list[dict[str, Any]] = []
    for assertion in contract.get("qualification_assertions", []):
        assertion_id = assertion.get("id", "<missing>")
        op = assertion.get("op")
        _require(op in operators, f"{assertion_id}: unsupported operator {op!r}")
        lhs_ref = assertion.get("lhs")
        rhs_ref = assertion.get("rhs")
        _require(isinstance(lhs_ref, list) and len(lhs_ref) == 2, f"{assertion_id}: lhs must be [control, metric]")
        _require(isinstance(rhs_ref, list) and len(rhs_ref) == 2, f"{assertion_id}: rhs must be [control, metric]")
        try:
            lhs = metrics[lhs_ref[0]][lhs_ref[1]]
            rhs = metrics[rhs_ref[0]][rhs_ref[1]]
        except KeyError as error:
            raise EvidenceError(f"{assertion_id}: unknown metric reference {error}") from error
        results.append({
            "id": assertion_id,
            "passed": bool(operators[op](lhs, rhs)),
            "lhs": lhs,
            "op": op,
            "rhs": rhs,
        })
    _require(results, "qualification contract has no assertions")
    return results


def qualify(contract_path: Path, evidence_path: Path) -> QualificationResult:
    contract = load_json(contract_path)
    evidence = load_json(evidence_path)
    _require(contract.get("schema_version") == 1, "unsupported evaluator contract schema_version")
    metrics = score_evidence(evidence)
    assertions = evaluate_assertions(contract, metrics)
    return QualificationResult(
        metrics=metrics,
        assertions=assertions,
        input_hashes={
            str(contract_path): file_sha256(contract_path),
            str(evidence_path): file_sha256(evidence_path),
        },
    )
