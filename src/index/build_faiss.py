from __future__ import annotations

"""
Scaffold for building FAISS indexes from embeddings.

Input:
- ids.json (ordered list of ids)
- vectors.npy (float32)

Output:
- index.faiss
- index_meta.json

NOTE: Placeholder using flat L2 index; tune parameters as needed.
"""

import argparse
import json
from pathlib import Path

import faiss
import numpy as np


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a FAISS index from vectors.npy/ids.json (scaffold).")
    ap.add_argument("emb_dir", type=Path, help="Directory containing ids.json and vectors.npy.")
    ap.add_argument("--metric", choices=["l2", "ip"], default="ip", help="FAISS metric (ip ~= cosine if vectors are normalized).")
    args = ap.parse_args()

    ids_path = args.emb_dir / "ids.json"
    vec_path = args.emb_dir / "vectors.npy"
    if not ids_path.exists() or not vec_path.exists():
        raise FileNotFoundError("ids.json or vectors.npy missing in embedding dir.")

    ids = json.loads(ids_path.read_text(encoding="utf-8"))
    vecs = np.load(vec_path)

    if args.metric == "ip":
        index = faiss.IndexFlatIP(vecs.shape[1])
    else:
        index = faiss.IndexFlatL2(vecs.shape[1])

    index.add(vecs)
    faiss.write_index(index, str(args.emb_dir / "index.faiss"))

    meta = {
        "metric": args.metric,
        "dim": int(vecs.shape[1]) if vecs.size else 0,
        "n": int(vecs.shape[0]),
        "source": str(args.emb_dir),
    }
    (args.emb_dir / "index_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built index for {meta['n']} vectors, dim={meta['dim']}, metric={args.metric}")


if __name__ == "__main__":
    main()
