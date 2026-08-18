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


async def run_subject(
    *, repo_root: Path, evidence_root: Path, codex_home: Path, codex_binary: str,
    model: str, reasoning_effort: str, spec: RunSpec, world: dict[str, Any],
    instruction_path: Path, semaphore: asyncio.Semaphore,
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
            rc, stderr = await _run_command(base + [
                "--output-schema", str(repo_root / "research/contracts/challenge-turn-1.schema.json"),
                "-o", str(output_1), world["turn_1"],
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
            prompt_2 = world["turn_2"].format(
                probe=probe,
                observation=f"{observed}. {world['observations'][observed]}",
            )
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
    worlds_path = repo_root / "research/worlds/challenge/worlds-0002.json"
    worlds_doc = load_json(worlds_path)
    worlds = {world["id"]: world for world in worlds_doc["worlds"]}
    instructions = {
        "current-loop": repo_root / "AGENTS.md",
        "no-loop": repo_root / "research/controls/no-loop/AGENTS.md",
        "ritualistic": repo_root / "research/controls/ritualistic/AGENTS.md",
        "local-optimizer": repo_root / "research/controls/local-optimizer/AGENTS.md",
    }
    specs = [RunSpec(condition, world_id, repetition)
             for repetition in range(1, contract["repetitions"] + 1)
             for world_id in contract["worlds"] for condition in contract["conditions"]]
    if len(specs) != contract["planned_runs"]:
        raise PilotError("planned run count does not match the factorial contract")
    if set(contract["worlds"]) != set(worlds):
        raise PilotError("contract and frozen challenge worlds differ")
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
                    world=worlds[spec.world_id], instruction_path=instructions[spec.condition],
                    semaphore=semaphore)
        for spec in specs
    ])
    summary = aggregate(results)
    (evidence_root / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary
