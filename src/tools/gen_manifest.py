from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from ingest.utils import write_manifest


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate a manifest for a JSONL file (LV0.7 scaffold).")
    ap.add_argument("jsonl", type=Path, help="Path to JSONL file.")
    ap.add_argument("--schema-version", default="lv0.7", help="Schema version label.")
    ap.add_argument("--id-policy", default=None, help="Short description of ID policy.")
    ap.add_argument("--manifest", type=Path, default=None, help="Manifest path (default: <jsonl>.manifest.json).")
    args = ap.parse_args()

    jsonl_path = args.jsonl
    if args.manifest:
        manifest_path = args.manifest
    else:
        manifest_path = jsonl_path.with_suffix(jsonl_path.suffix + ".manifest.json")

    try:
        git_commit = (
            subprocess.run(["git", "rev-parse", "HEAD"], check=False, capture_output=True, text=True)
            .stdout.strip()
        )
    except Exception:
        git_commit = ""

    payload = write_manifest(
        target=jsonl_path,
        manifest_path=manifest_path,
        schema_version=args.schema_version,
        generated_by="src/tools/gen_manifest.py",
        git_commit=git_commit or None,
        id_policy=args.id_policy,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
