#!/usr/bin/env python3
"""Create a content-addressed manifest for an evidence directory."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import tempfile


def file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output-name", default="content-manifest.json")
    args = parser.parse_args()
    root = args.directory.resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")
    output = root / args.output_name
    entries = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path == output:
            continue
        entries.append({
            "path": str(path.relative_to(root)),
            "bytes": path.stat().st_size,
            "sha256": file_hash(path),
        })
    payload = {
        "schema_version": 1,
        "root": str(root),
        "file_count": len(entries),
        "files": entries,
    }
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=root, delete=False) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(output)
    print(f"{file_hash(output)}  {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
