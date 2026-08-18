#!/usr/bin/env python3
"""Qualify evaluator epoch EVAL-0001 against frozen synthetic controls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from research.harness.scoring import EvidenceError, qualify  # noqa: E402


DEFAULT_CONTRACT = REPO_ROOT / "research/contracts/evaluator-epoch-0001.json"
DEFAULT_EVIDENCE = REPO_ROOT / "research/evidence/qualification/synthetic-reference-trajectories.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--json", action="store_true", help="emit one machine-readable JSON document")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = qualify(args.contract, args.evidence)
    except (OSError, json.JSONDecodeError, EvidenceError) as error:
        if args.json:
            print(json.dumps({"passed": False, "error": str(error)}, sort_keys=True))
        else:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    payload = {
        "passed": result.passed,
        "input_hashes": result.input_hashes,
        "metrics": result.metrics,
        "assertions": result.assertions,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Stage 0 ruler qualification")
        for assertion in result.assertions:
            mark = "PASS" if assertion["passed"] else "FAIL"
            print(f"{mark} {assertion['id']}: {assertion['lhs']:.6f} {assertion['op']} {assertion['rhs']:.6f}")
        print(f"Result: {'PASS' if result.passed else 'FAIL'} ({sum(item['passed'] for item in result.assertions)}/{len(result.assertions)})")
        for path, digest in result.input_hashes.items():
            print(f"SHA256 {digest}  {path}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
