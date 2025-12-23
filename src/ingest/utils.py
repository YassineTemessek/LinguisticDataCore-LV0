from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Tuple


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def count_jsonl(path: Path) -> int:
    total = 0
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.strip():
                total += 1
    return total


def load_jsonl(path: Path, limit: int | None = None) -> Iterable[dict]:
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for idx, line in enumerate(fh):
            if limit is not None and idx >= limit:
                break
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def write_manifest(
    *,
    target: Path,
    manifest_path: Path,
    schema_version: str,
    generated_by: str,
    git_commit: str | None = None,
    id_policy: str | None = None,
) -> dict:
    sha = sha256_file(target)
    rows = count_jsonl(target)
    payload = {
        "file": str(target),
        "sha256": sha,
        "row_count": rows,
        "schema_version": schema_version,
        "generated_by": generated_by,
    }
    if git_commit:
        payload["git_commit"] = git_commit
    if id_policy:
        payload["id_policy"] = id_policy
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload
