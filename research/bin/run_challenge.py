#!/usr/bin/env python3
"""Run the frozen LL-0003 GPT-5.6-Luna challenge."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from research.harness.challenge_runner import run_challenge  # noqa: E402
from research.harness.pilot import PilotError, prepare_isolated_codex_home  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=REPO_ROOT / "research/contracts/challenge-0003.json")
    parser.add_argument("--evidence-root", type=Path, default=REPO_ROOT / "research/evidence/challenge/LL-0003")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--codex-binary", default=shutil.which("codex"))
    parser.add_argument("--source-codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")))
    args = parser.parse_args()
    if not args.codex_binary or not 1 <= args.concurrency <= 8:
        print("ERROR: valid codex binary and concurrency 1..8 required", file=sys.stderr)
        return 2
    try:
        with tempfile.TemporaryDirectory(prefix="learning-loop-challenge-home-") as temp_dir:
            isolated_home = Path(temp_dir) / "home"
            prepare_isolated_codex_home(args.source_codex_home, isolated_home)
            summary = asyncio.run(run_challenge(
                repo_root=REPO_ROOT, evidence_root=args.evidence_root, contract_path=args.contract,
                codex_home=isolated_home, codex_binary=args.codex_binary, concurrency=args.concurrency,
            ))
    except (OSError, PilotError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["harness_failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
