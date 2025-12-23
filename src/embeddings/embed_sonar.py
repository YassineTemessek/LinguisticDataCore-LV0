from __future__ import annotations

"""
Scaffold for SONAR embedding generation.

Expected inputs:
- JSONL file with LV0.7 rows containing meaning_text.

Outputs:
- ids.json (ordered IDs)
- vectors.npy (float32, aligned 1:1 with ids)
- meta.json (model id/hash, dim, pooling, text_field, created_at, source hashes)
- coverage.json (embedded vs. skipped)

NOTE: This is a placeholder; plug in real SONAR model inference before use.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Tuple

import numpy as np

from ingest.utils import sha256_file


def iter_rows(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def fake_embed(text: str, dim: int = 8) -> np.ndarray:
    """
    Placeholder deterministic embedding: hash text to a small float vector.
    Replace with real SONAR inference.
    """
    h = hash(text)
    rng = np.random.default_rng(abs(h) % (2**32))
    return rng.standard_normal(dim).astype("float32")


def main() -> None:
    ap = argparse.ArgumentParser(description="Scaffold: generate SONAR meaning embeddings (placeholder).")
    ap.add_argument("jsonl", type=Path, help="Input JSONL with meaning_text.")
    ap.add_argument("out_dir", type=Path, help="Output directory for ids.json/vectors.npy/meta.json/coverage.json.")
    ap.add_argument("--dim", type=int, default=8, help="Embedding dimension for placeholder.")
    ap.add_argument("--model-id", default="sonar-placeholder", help="Model identifier.")
    ap.add_argument("--text-field", default="meaning_text", help="Field to embed.")
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    ids: list[str] = []
    vecs: list[np.ndarray] = []
    skipped = 0
    embedded = 0

    for rec in iter_rows(args.jsonl):
        text = rec.get(args.text_field) or ""
        if not text.strip():
            skipped += 1
            continue
        vid = rec.get("id") or ""
        if not vid:
            skipped += 1
            continue
        ids.append(vid)
        vecs.append(fake_embed(text, dim=args.dim))
        embedded += 1

    if vecs:
        mat = np.stack(vecs, axis=0)
    else:
        mat = np.zeros((0, args.dim), dtype="float32")

    (args.out_dir / "ids.json").write_text(json.dumps(ids, ensure_ascii=False, indent=2), encoding="utf-8")
    np.save(args.out_dir / "vectors.npy", mat)

    meta = {
        "model_id": args.model_id,
        "dim": args.dim,
        "text_field": args.text_field,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_jsonl": str(args.jsonl),
        "source_sha256": sha256_file(args.jsonl),
        "note": "placeholder embedding; replace with real SONAR inference",
    }
    (args.out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    coverage = {
        "embedded": embedded,
        "skipped": skipped,
        "total": embedded + skipped,
    }
    (args.out_dir / "coverage.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Embedded={embedded}, skipped={skipped}, dim={args.dim}, out={args.out_dir}")


if __name__ == "__main__":
    main()
