#!/usr/bin/env python3
"""Run the frozen LL-0001 controlled subject-agent pilot."""

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

from research.harness.pilot import PilotError, prepare_isolated_codex_home, run_pilot  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=REPO_ROOT / "research/contracts/pilot-0002.json")
    parser.add_argument("--evidence-root", type=Path, default=REPO_ROOT / "research/evidence/pilot/LL-0002")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--codex-binary", default=shutil.which("codex"))
    parser.add_argument("--source-codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.codex_binary:
        print("ERROR: codex binary not found", file=sys.stderr)
        return 2
    if args.concurrency < 1 or args.concurrency > 8:
        print("ERROR: concurrency must be between 1 and 8", file=sys.stderr)
        return 2
    try:
        with tempfile.TemporaryDirectory(prefix="learning-loop-codex-home-") as temp_dir:
            isolated_home = Path(temp_dir) / "home"
            prepare_isolated_codex_home(args.source_codex_home, isolated_home)
            summary = asyncio.run(
                run_pilot(
                    repo_root=REPO_ROOT,
                    evidence_root=args.evidence_root,
                    contract_path=args.contract,
                    codex_home=isolated_home,
                    codex_binary=args.codex_binary,
                    concurrency=args.concurrency,
                )
            )
    except (OSError, PilotError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["harness_failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
