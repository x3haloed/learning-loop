"""Execution and deterministic scoring for controlled subject-agent pilot LL-0001."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import time
from typing import Any


class PilotError(RuntimeError):
    """Raised for a harness-level pilot failure."""


@dataclass(frozen=True)
class RunSpec:
    condition: str
    world_id: str
    repetition: int

    @property
    def run_id(self) -> str:
        return f"{self.condition}__{self.world_id}__r{self.repetition}"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(payload).hexdigest()


def file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def score_run(world: dict[str, Any], turn_1: dict[str, Any], turn_2: dict[str, Any]) -> dict[str, float]:
    oracle = world["oracle"]
    probe = turn_1["probe_choice"]
    expected_support = 1 if oracle["checkpoint_outcomes"] else 0
    del expected_support  # The phase-one probability is retained as evidence, not scored without a binary probe proposition oracle.
    brier = sum(
        (float(turn_2["probabilities"][case_id]) - int(outcome)) ** 2
        for case_id, outcome in oracle["checkpoint_outcomes"].items()
    ) / len(oracle["checkpoint_outcomes"])
    return {
        "probe_value": float(oracle["probe_value"][probe]),
        "preferred_probe": 1.0 if probe == oracle["preferred_probe"] else 0.0,
        "fixed_checkpoint_brier": brier,
        "model_accuracy": 1.0 if turn_2["model_choice"] == oracle["model_choice"] else 0.0,
        "decision_accuracy": 1.0 if turn_2["decision"] == oracle["decision"] else 0.0,
        "next_action_accuracy": 1.0 if turn_2["next_action"] == oracle["next_action"][probe] else 0.0,
    }


def extract_thread_id(events_path: Path) -> str:
    with events_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") in {"thread.started", "session.started"}:
                thread_id = event.get("thread_id") or event.get("session_id")
                if isinstance(thread_id, str) and thread_id:
                    return thread_id
    raise PilotError(f"No thread/session id found in {events_path}")


def extract_usage(events_path: Path) -> dict[str, int]:
    totals = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}
    with events_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            usage = event.get("usage")
            if not isinstance(usage, dict):
                continue
            for key in totals:
                value = usage.get(key)
                if isinstance(value, int):
                    totals[key] = max(totals[key], value)
    return totals


async def _run_command(command: list[str], env: dict[str, str], events_path: Path) -> tuple[int, str]:
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    stdout, stderr = await process.communicate()
    events_path.write_bytes(stdout)
    return process.returncode, stderr.decode("utf-8", errors="replace")


async def run_subject(
    *,
    repo_root: Path,
    evidence_root: Path,
    codex_home: Path,
    codex_binary: str,
    model: str,
    reasoning_effort: str,
    spec: RunSpec,
    world: dict[str, Any],
    instruction_path: Path,
    semaphore: asyncio.Semaphore,
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
                codex_binary,
                "exec",
                "--ignore-user-config",
                "--ignore-rules",
                "--json",
                "-m",
                model,
                "-c",
                f'model_reasoning_effort="{reasoning_effort}"',
                "-s",
                "read-only",
                "-C",
                str(workspace),
            ]

            turn_1_events = run_dir / "turn-1-events.jsonl"
            turn_1_output = run_dir / "turn-1-output.json"
            command_1 = base + [
                "--output-schema",
                str(repo_root / "research/contracts/pilot-turn-1.schema.json"),
                "-o",
                str(turn_1_output),
                world["turn_1"],
            ]
            returncode, stderr = await _run_command(command_1, env, turn_1_events)
            (run_dir / "turn-1-stderr.txt").write_text(stderr, encoding="utf-8")
            if returncode != 0:
                raise PilotError(f"turn 1 exited {returncode}: {stderr[-1000:]}")
            turn_1 = load_json(turn_1_output)
            thread_id = extract_thread_id(turn_1_events)
            probe = turn_1["probe_choice"]
            if probe not in world["observations"]:
                raise PilotError(f"invalid probe {probe!r}")

            turn_2_events = run_dir / "turn-2-events.jsonl"
            turn_2_output = run_dir / "turn-2-output.json"
            prompt_2 = world["turn_2"].format(observation=world["observations"][probe])
            command_2 = [
                codex_binary,
                "exec",
                "resume",
                "--ignore-user-config",
                "--ignore-rules",
                "--json",
                "-m",
                model,
                "-c",
                f'model_reasoning_effort="{reasoning_effort}"',
                "--output-schema",
                str(repo_root / "research/contracts/pilot-turn-2.schema.json"),
                "-o",
                str(turn_2_output),
                thread_id,
                prompt_2,
            ]
            returncode, stderr = await _run_command(command_2, env, turn_2_events)
            (run_dir / "turn-2-stderr.txt").write_text(stderr, encoding="utf-8")
            if returncode != 0:
                raise PilotError(f"turn 2 exited {returncode}: {stderr[-1000:]}")
            turn_2 = load_json(turn_2_output)
            scores = score_run(world, turn_1, turn_2)
            result = {
                "run_id": spec.run_id,
                "condition": spec.condition,
                "world_id": spec.world_id,
                "repetition": spec.repetition,
                "model": model,
                "reasoning_effort": reasoning_effort,
                "thread_id": thread_id,
                "instruction_sha256": file_hash(instruction_path),
                "world_sha256": canonical_hash(world),
                "turn_1": turn_1,
                "turn_2": turn_2,
                "scores": scores,
                "usage": {
                    "turn_1": extract_usage(turn_1_events),
                    "turn_2": extract_usage(turn_2_events),
                },
                "elapsed_seconds": time.time() - started,
                "status": "complete",
            }
            (run_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            return result
        except Exception as error:
            failure = {
                "run_id": spec.run_id,
                "condition": spec.condition,
                "world_id": spec.world_id,
                "repetition": spec.repetition,
                "model": model,
                "reasoning_effort": reasoning_effort,
                "elapsed_seconds": time.time() - started,
                "status": "harness-failure",
                "error": str(error),
            }
            (run_dir / "result.json").write_text(json.dumps(failure, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            return failure
        finally:
            shutil.rmtree(workspace, ignore_errors=True)


def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    metric_names = [
        "probe_value",
        "preferred_probe",
        "fixed_checkpoint_brier",
        "model_accuracy",
        "decision_accuracy",
        "next_action_accuracy",
    ]
    grouped: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        grouped.setdefault(result["condition"], []).append(result)
    conditions: dict[str, Any] = {}
    for condition, rows in sorted(grouped.items()):
        complete = [row for row in rows if row["status"] == "complete"]
        metrics = {
            name: sum(row["scores"][name] for row in complete) / len(complete)
            for name in metric_names
        } if complete else {}
        conditions[condition] = {
            "planned": len(rows),
            "complete": len(complete),
            "harness_failures": len(rows) - len(complete),
            "metrics": metrics,
        }
    return {
        "planned_runs": len(results),
        "complete_runs": sum(result["status"] == "complete" for result in results),
        "harness_failures": sum(result["status"] != "complete" for result in results),
        "conditions": conditions,
    }


async def run_pilot(
    *,
    repo_root: Path,
    evidence_root: Path,
    contract_path: Path,
    codex_home: Path,
    codex_binary: str,
    concurrency: int,
) -> dict[str, Any]:
    contract = load_json(contract_path)
    worlds_doc = load_json(repo_root / "research/worlds/pilot/worlds.json")
    worlds = {world["id"]: world for world in worlds_doc["worlds"]}
    instruction_paths = {
        "current-loop": repo_root / "AGENTS.md",
        "no-loop": repo_root / "research/controls/no-loop/AGENTS.md",
        "ritualistic": repo_root / "research/controls/ritualistic/AGENTS.md",
        "local-optimizer": repo_root / "research/controls/local-optimizer/AGENTS.md",
    }
    specs = [
        RunSpec(condition=condition, world_id=world_id, repetition=repetition)
        for repetition in range(1, contract["repetitions"] + 1)
        for world_id in contract["worlds"]
        for condition in contract["conditions"]
    ]
    if len(specs) != contract["planned_runs"]:
        raise PilotError("planned run count does not match the factorial contract")
    evidence_root.mkdir(parents=True, exist_ok=False)
    manifest = {
        "contract_sha256": file_hash(contract_path),
        "worlds_sha256": file_hash(repo_root / "research/worlds/pilot/worlds.json"),
        "model": contract["model"],
        "reasoning_effort": contract["reasoning_effort"],
        "runs": [spec.run_id for spec in specs],
    }
    (evidence_root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [
        run_subject(
            repo_root=repo_root,
            evidence_root=evidence_root,
            codex_home=codex_home,
            codex_binary=codex_binary,
            model=contract["model"],
            reasoning_effort=contract["reasoning_effort"],
            spec=spec,
            world=worlds[spec.world_id],
            instruction_path=instruction_paths[spec.condition],
            semaphore=semaphore,
        )
        for spec in specs
    ]
    results = await asyncio.gather(*tasks)
    summary = aggregate(results)
    (evidence_root / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def prepare_isolated_codex_home(source_home: Path, target_home: Path) -> None:
    auth_source = source_home / "auth.json"
    if not auth_source.is_file():
        raise PilotError(f"Codex auth file not found: {auth_source}")
    target_home.mkdir(mode=0o700, parents=True, exist_ok=False)
    auth_target = target_home / "auth.json"
    shutil.copy2(auth_source, auth_target)
    auth_target.chmod(stat.S_IRUSR | stat.S_IWUSR)
