"""Isolated subject execution for the frozen LL-0003 challenge."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Any

from research.harness.challenge import observation, score_response
from research.harness.pilot import (
    PilotError,
    RunSpec,
    _run_command,
    canonical_hash,
    extract_thread_id,
    extract_usage,
    file_hash,
    load_json,
)


METRICS = (
    "probe_information_ratio",
    "preferred_probe",
    "probe_prediction_brier",
    "posterior_brier",
    "posterior_l1_from_bayes",
    "fixed_checkpoint_brier",
    "decision_accuracy",
    "next_action_accuracy",
)

INSTRUCTION_PACKAGES = {
    "adaptive-reference": "AGENTS.md",
    "no-loop": "research/controls/no-loop/AGENTS.md",
    "ritualistic": "research/controls/ritualistic/AGENTS.md",
    "local-optimizer": "research/controls/local-optimizer/AGENTS.md",
}

LEGACY_INSTRUCTION_PACKAGES = {
    "current-loop": "adaptive-reference",
    "no-loop": "no-loop",
    "ritualistic": "ritualistic",
    "local-optimizer": "local-optimizer",
}

PROMPT_STYLES = ("contract", "plain")


def _resolve_condition_metadata(contract: dict[str, any], condition: str) -> tuple[str, str]:
    legacy = condition in LEGACY_INSTRUCTION_PACKAGES
    if legacy and "condition_profiles" not in contract:
        instruction = LEGACY_INSTRUCTION_PACKAGES[condition]
        return (
            instruction,
            "contract",
        )

    profiles = contract.get("condition_profiles", {})
    if condition not in profiles:
        raise KeyError(f"missing condition profile for {condition!r}")
    profile = profiles[condition]
    instruction = profile.get("instruction_package", "adaptive-reference")
    prompt_style = profile.get("prompt_design", "contract")
    if prompt_style not in PROMPT_STYLES:
        raise ValueError(f"invalid prompt design {prompt_style!r} for {condition!r}")
    return instruction, prompt_style


def _prompt_design(prompt_text: str, prompt_style: str, world: dict[str, Any], *, turn_2: bool = False,
                  observed: str | None = None) -> str:
    if prompt_style == "contract":
        if turn_2 and observed is not None:
            return world["turn_2"].format(
                probe=prompt_text,
                observation=f"{observed}. {world['observations'][observed]}",
            )
        return prompt_text

    if turn_2 and observed is not None:
        base = world["turn_2"].format(
            probe=prompt_text,
            observation=f"{observed}. {world['observations'][observed]}",
        )
        return (
            base.replace("Select a model intervention only if its posterior is at least 0.80; otherwise choose D4.",
                          "If one model is clearly strongest, choose that model's intervention; otherwise prefer to gather more evidence safely.")
                   .replace("Return only the required JSON.", "Return a JSON payload with the required fields.")
        )

    base = prompt_text.replace("Select the contact with the greatest expected information gain per unit cost.", "Choose one contact.")
    base = base.replace("Return only the required JSON.", "Return a JSON payload with the required fields.")
    return base


async def run_subject(
    *, repo_root: Path, evidence_root: Path, codex_home: Path, codex_binary: str,
    model: str, reasoning_effort: str, spec: RunSpec, world: dict[str, Any],
    instruction_path: Path, prompt_style: str, semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    async with semaphore:
        run_dir = evidence_root / "runs" / spec.run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        workspace = Path(tempfile.mkdtemp(prefix=f"ll-{spec.run_id}-"))
        started = time.time()
        try:
            shutil.copy2(instruction_path, workspace / "AGENTS.md")
            subprocess.run(["git", "init", "-q", str(workspace)], check=True)
            subprocess.run(["git", "-C", str(workspace), "add", "AGENTS.md"], check=True)
            env = os.environ.copy()
            env["CODEX_HOME"] = str(codex_home)
            base = [
                codex_binary, "exec", "--ignore-user-config", "--ignore-rules", "--json",
                "-m", model, "-c", f'model_reasoning_effort="{reasoning_effort}"',
                "-s", "read-only", "-C", str(workspace),
            ]
            events_1 = run_dir / "turn-1-events.jsonl"
            output_1 = run_dir / "turn-1-output.json"
            turn_1_prompt = _prompt_design(world["turn_1"], prompt_style, world)
            rc, stderr = await _run_command(base + [
                "--output-schema", str(repo_root / "research/contracts/challenge-turn-1.schema.json"),
                "-o", str(output_1), turn_1_prompt,
            ], env, events_1)
            (run_dir / "turn-1-stderr.txt").write_text(stderr, encoding="utf-8")
            if rc != 0:
                raise PilotError(f"turn 1 exited {rc}: {stderr[-1000:]}")
            turn_1 = load_json(output_1)
            thread_id = extract_thread_id(events_1)
            probe = turn_1.get("probe_choice")
            if probe not in world["probe_positive_model"]:
                raise PilotError(f"invalid probe {probe!r}")

            observed = observation(world, probe)
            prompt_2 = _prompt_design(probe, prompt_style, world, turn_2=True, observed=observed)
            events_2 = run_dir / "turn-2-events.jsonl"
            output_2 = run_dir / "turn-2-output.json"
            rc, stderr = await _run_command([
                codex_binary, "exec", "resume", "--ignore-user-config", "--ignore-rules", "--json",
                "-m", model, "-c", f'model_reasoning_effort="{reasoning_effort}"',
                "--output-schema", str(repo_root / "research/contracts/challenge-turn-2.schema.json"),
                "-o", str(output_2), thread_id, prompt_2,
            ], env, events_2)
            (run_dir / "turn-2-stderr.txt").write_text(stderr, encoding="utf-8")
            if rc != 0:
                raise PilotError(f"turn 2 exited {rc}: {stderr[-1000:]}")
            turn_2 = load_json(output_2)
            result = {
                "run_id": spec.run_id, "condition": spec.condition, "world_id": spec.world_id,
                "family": world["family"], "repetition": spec.repetition, "model": model,
                "reasoning_effort": reasoning_effort, "thread_id": thread_id,
                "instruction_sha256": file_hash(instruction_path), "world_sha256": canonical_hash(world),
                "selected_observation": observed, "turn_1": turn_1, "turn_2": turn_2,
                "scores": score_response(world, turn_1, turn_2),
                "usage": {"turn_1": extract_usage(events_1), "turn_2": extract_usage(events_2)},
                "elapsed_seconds": time.time() - started, "status": "complete",
            }
        except Exception as error:
            result = {
                "run_id": spec.run_id, "condition": spec.condition, "world_id": spec.world_id,
                "family": world.get("family"), "repetition": spec.repetition, "model": model,
                "reasoning_effort": reasoning_effort, "elapsed_seconds": time.time() - started,
                "status": "harness-failure", "error": str(error),
            }
        (run_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        shutil.rmtree(workspace, ignore_errors=True)
        return result


def _metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    return {name: sum(row["scores"][name] for row in rows) / len(rows) for name in METRICS} if rows else {}


def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    conditions: dict[str, Any] = {}
    for condition in sorted({row["condition"] for row in results}):
        planned = [row for row in results if row["condition"] == condition]
        complete = [row for row in planned if row["status"] == "complete"]
        families = {
            family: _metrics([row for row in complete if row["family"] == family])
            for family in sorted({row["family"] for row in complete})
        }
        conditions[condition] = {
            "planned": len(planned), "complete": len(complete),
            "harness_failures": len(planned) - len(complete), "metrics": _metrics(complete),
            "families": families,
        }
    return {
        "planned_runs": len(results),
        "complete_runs": sum(row["status"] == "complete" for row in results),
        "harness_failures": sum(row["status"] != "complete" for row in results),
        "conditions": conditions,
    }


async def run_challenge(*, repo_root: Path, evidence_root: Path, contract_path: Path,
                        codex_home: Path, codex_binary: str, concurrency: int) -> dict[str, Any]:
    contract = load_json(contract_path)
    worlds_path = contract.get("world_manifest", "research/worlds/challenge/worlds-0002.json")
    if isinstance(worlds_path, str):
        worlds_path = repo_root / worlds_path
    elif not isinstance(worlds_path, Path):
        raise PilotError("world_manifest must be a string path")
    worlds_path = worlds_path.resolve()
    if not str(worlds_path).startswith(str(repo_root.resolve())):
        raise PilotError("world_manifest must be within repository")
    worlds_doc = load_json(worlds_path)
    worlds = {world["id"]: world for world in worlds_doc["worlds"]}
    plans: list[tuple[str, Path, str]] = []
    for condition in contract["conditions"]:
        instruction_id, prompt_style = _resolve_condition_metadata(contract, condition)
        if instruction_id in INSTRUCTION_PACKAGES:
            instruction_path = repo_root / INSTRUCTION_PACKAGES[instruction_id]
        else:
            candidate = repo_root / instruction_id
            if not candidate.is_file():
                raise PilotError(f"unknown instruction package {instruction_id!r} for condition {condition!r}")
            instruction_path = candidate
        plans.append((condition, instruction_path, prompt_style))
    condition_plan = {condition: (instruction_path, prompt_style) for condition, instruction_path, prompt_style in plans}
    specs = [RunSpec(condition, world_id, repetition)
             for repetition in range(1, contract["repetitions"] + 1)
             for world_id in contract["worlds"] for condition in contract["conditions"]]
    if len(specs) != contract["planned_runs"]:
        raise PilotError("planned run count does not match the factorial contract")
    if set(contract["worlds"]) != set(worlds):
        raise PilotError("contract and frozen challenge worlds differ")
    for condition in contract["conditions"]:
        if condition not in condition_plan:
            raise PilotError(f"missing condition plan for {condition!r}")
    evidence_root.mkdir(parents=True, exist_ok=False)
    (evidence_root / "manifest.json").write_text(json.dumps({
        "contract_sha256": file_hash(contract_path), "worlds_sha256": file_hash(worlds_path),
        "model": contract["model"], "reasoning_effort": contract["reasoning_effort"],
        "runs": [spec.run_id for spec in specs],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    semaphore = asyncio.Semaphore(concurrency)
    results = await asyncio.gather(*[
        run_subject(repo_root=repo_root, evidence_root=evidence_root, codex_home=codex_home,
                    codex_binary=codex_binary, model=contract["model"],
                    reasoning_effort=contract["reasoning_effort"], spec=spec,
                    world=worlds[spec.world_id], instruction_path=condition_plan[spec.condition][0],
                    prompt_style=condition_plan[spec.condition][1],
                    semaphore=semaphore)
        for spec in specs
    ])
    summary = aggregate(results)
    (evidence_root / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary
