from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from linguistic_data_core.release.fetch import fetch_release
from linguistic_data_core.release.package import package_language_bundles
from linguistic_data_core.validation import validate_processed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ldc")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ingest = sub.add_parser("ingest", help="Build canonical processed datasets from raw inputs.")
    ingest.add_argument("--all", action="store_true", help="Run all ingest steps.")
    ingest.add_argument("--only", action="append", default=[], help="Run only specific tags (repeatable).")
    ingest.add_argument("--resources-dir", type=Path, default=None, help="External datasets folder.")
    ingest.add_argument("--require-inputs", action="store_true", help="Fail if required inputs are missing.")
    ingest.add_argument("--fail-fast", action="store_true", help="Stop on first failed step.")
    ingest.add_argument("--skip-missing-inputs", action="store_true", help="Skip steps whose inputs are missing.")
    ingest.add_argument("--no-write-manifest", action="store_true", help="Do not write a manifest JSON.")

    val = sub.add_parser("validate", help="Validate processed outputs.")
    val.add_argument("--all", action="store_true", help="Validate all canonical outputs (skipping missing by default).")
    val.add_argument("--require-files", action="store_true", help="Fail if required files are missing.")

    pkg = sub.add_parser("package", help="Package per-language release assets.")
    pkg.add_argument("--version", required=True, help="Date version, e.g. 2025.12.19")

    fetch = sub.add_parser("fetch", help="Fetch and extract published release assets.")
    fetch.add_argument("--release", default="latest", help="Release tag (or 'latest').")
    fetch.add_argument("--dest", type=Path, default=Path("."), help="Destination folder for extraction.")

    args = ap.parse_args(argv)

    repo_root = Path.cwd()

    if args.cmd == "ingest":
        script = repo_root / "scripts" / "ingest" / "run_ingest_all.py"
        if not script.exists():
            raise FileNotFoundError(str(script))

        cmd: list[str] = ["python", str(script)]
        if args.only:
            for item in args.only:
                cmd.extend(["--only", str(item)])
        if args.resources_dir is not None:
            cmd.extend(["--resources-dir", str(args.resources_dir)])
        if args.require_inputs:
            cmd.append("--require-inputs")
        if args.fail_fast:
            cmd.append("--fail-fast")
        if args.skip_missing_inputs:
            cmd.append("--skip-missing-inputs")
        if args.no_write_manifest:
            cmd.append("--no-write-manifest")
        proc = subprocess.run(cmd, cwd=str(repo_root), check=False)
        return int(proc.returncode)

    if args.cmd == "validate":
        return validate_processed(repo_root=repo_root, validate_all=bool(args.all), require_files=bool(args.require_files))

    if args.cmd == "package":
        package_language_bundles(repo_root=repo_root, version=args.version)
        return 0

    if args.cmd == "fetch":
        fetch_release(repo_root=repo_root, release=args.release, dest=args.dest)
        return 0

    raise SystemExit(2)
