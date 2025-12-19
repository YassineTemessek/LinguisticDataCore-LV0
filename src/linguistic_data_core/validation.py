from __future__ import annotations

import subprocess
from pathlib import Path


def validate_processed(*, repo_root: Path, validate_all: bool, require_files: bool) -> int:
    """
    Thin wrapper around the existing validation script (kept in-tree for now).
    """
    script = repo_root / "scripts" / "ingest" / "validate_processed.py"
    if not script.exists():
        raise FileNotFoundError(str(script))
    cmd = ["python", str(script)]
    if validate_all:
        cmd.append("--all")
    if require_files:
        cmd.append("--require-files")
    proc = subprocess.run(cmd, cwd=str(repo_root), check=False)
    return int(proc.returncode)

