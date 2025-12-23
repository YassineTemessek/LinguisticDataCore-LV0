from __future__ import annotations

"""
Scaffold search utility for FAISS indexes built from embeddings.
"""

import argparse
import json
from pathlib import Path

import faiss
import numpy as np


def main() -> None:
    ap = argparse.ArgumentParser(description="Search FAISS index with a query vector (placeholder).")
    ap.add_argument("emb_dir", type=Path, help="Directory containing index.faiss and ids.json.")
    ap.add_argument("--query", type=str, help="Comma-separated floats for a query vector.")
    ap.add_argument("--topk", type=int, default=5)
    args = ap.parse_args()

    ids = json.loads((args.emb_dir / "ids.json").read_text(encoding="utf-8"))
    index = faiss.read_index(str(args.emb_dir / "index.faiss"))

    if not args.query:
        raise SystemExit("Provide --query as comma-separated floats.")
    q = np.array([float(x) for x in args.query.split(",")], dtype="float32")
    if q.shape[0] != index.d:
        raise SystemExit(f"Query dim {q.shape[0]} != index dim {index.d}")
    q = q.reshape(1, -1)
    scores, idxs = index.search(q, args.topk)
    for rank, (score, idx) in enumerate(zip(scores[0], idxs[0]), start=1):
        if idx < 0 or idx >= len(ids):
            continue
        print(f"{rank}: id={ids[idx]} score={score}")


if __name__ == "__main__":
    main()
