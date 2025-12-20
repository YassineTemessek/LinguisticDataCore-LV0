"""
Build a wide-coverage Arabic word/lemma lexicon with derived binary roots.

LV2 goal: regroup Arabic words by a biconsonantal (2-letter) nucleus.

Inputs (default):
  - data/processed/arabic/classical/sources/word_root_map_filtered.jsonl
  - data/processed/arabic/classical/sources/quran_lemmas_enriched.jsonl

Output (default):
  - data/processed/arabic/classical/arabic_words_binary_roots.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from processed_schema import ensure_min_schema


AR_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670\u0640]")

# Common normalization for Arabic root strings.
_ROOT_NORM_MAP = str.maketrans(
    {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
        "ى": "ي",
        "ؤ": "و",
        "ئ": "ي",
        "ة": "ه",
    }
)

# Letters often treated as "weak/auxiliary" in some analyses.
DEFAULT_WEAK_LETTERS = "اوييء"


def normalize_root(root: str) -> str:
    root = (root or "").strip()
    if not root:
        return ""
    root = AR_DIACRITICS_RE.sub("", root)
    root = root.translate(_ROOT_NORM_MAP)
    return root


def derive_binary_root(root_norm: str, *, weak_letters: str) -> tuple[str, str, str]:
    """
    Returns: (binary_root, method, weakless_root)

    - binary_root_first2 is always the first two chars of `root_norm` (if available)
    - LV0 canonical binary_root is the first two chars of `root_norm`
    """
    r = root_norm or ""
    first2 = r[:2] if len(r) >= 2 else ""
    weak_set = set((weak_letters or "").strip())
    weakless = "".join(ch for ch in r if ch not in weak_set)
    weakless2 = weakless[:2] if len(weakless) >= 2 else ""
    if first2:
        return first2, "first2", weakless
    return "", "missing", weakless


def best_status(a: str, b: str) -> str:
    rank = {"gold": 3, "silver": 2, "auto": 1, "auto_brut": 1}
    ra = rank.get((a or "").strip(), 0)
    rb = rank.get((b or "").strip(), 0)
    return a if ra >= rb else b


def merge_records(cur: dict[str, Any], nxt: dict[str, Any]) -> dict[str, Any]:
    cur.setdefault("sources", [])
    src = str(nxt.get("source") or "").strip()
    if src and src not in cur["sources"]:
        cur["sources"].append(src)
    cur["lemma_status"] = best_status(str(cur.get("lemma_status") or ""), str(nxt.get("lemma_status") or ""))

    for key in ("translit", "ipa_raw", "ipa", "type"):
        if not cur.get(key) and nxt.get(key):
            cur[key] = nxt.get(key)

    for ref_key in ("source_ref",):
        if not cur.get(ref_key) and nxt.get(ref_key):
            cur[ref_key] = nxt.get(ref_key)
    return cur


def iter_jsonl(path: Path) -> Any:
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def build(
    *,
    word_root_map_path: Path,
    quran_lemmas_path: Path,
    out_path: Path,
    weak_letters: str,
    keep_missing_root: bool,
) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    merged: dict[tuple[str, str], dict[str, Any]] = {}

    def add(rec: dict[str, Any]) -> None:
        lemma = str(rec.get("lemma") or "").strip()
        root = str(rec.get("root") or "").strip()
        if not lemma:
            return
        if (not root) and (not keep_missing_root):
            return

        root_norm = normalize_root(root)
        binary_root, method, weakless_root = derive_binary_root(root_norm, weak_letters=weak_letters)

        key = (lemma, root_norm or root or "")
        base = merged.get(key)
        if base is None:
            base = {
                "lemma": lemma,
                "root": root,
                "root_norm": root_norm,
                "weakless_root": weakless_root,
                "binary_root": binary_root,
                "binary_root_method": method,
                "binary_root_first2": root_norm[:2] if len(root_norm) >= 2 else "",
                "binary_root_weakless_first2": weakless_root[:2] if len(weakless_root) >= 2 else "",
                "language": "ara",
                "source": "lv2:arabic_binary_root_lexicon",
                "lemma_status": str(rec.get("lemma_status") or "auto_brut"),
                "sources": [],
            }
            merged[key] = base
        merge_records(base, rec)

    if word_root_map_path.exists():
        for rec in iter_jsonl(word_root_map_path):
            add(rec)
    if quran_lemmas_path.exists():
        for rec in iter_jsonl(quran_lemmas_path):
            add(rec)

    total = 0
    with out_path.open("w", encoding="utf-8") as out_f:
        for _, rec in sorted(merged.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            rec["sources"] = sorted(set(rec.get("sources") or []))
            rec["n_sources"] = len(rec["sources"])
            rec = ensure_min_schema(rec, default_language="ara", default_source="lv2:arabic_binary_root_lexicon", default_lemma_status="auto_brut")
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total += 1
    return total


def main() -> None:
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("--word-root-map", type=Path, default=Path("data/processed/arabic/classical/sources/word_root_map_filtered.jsonl"))
    ap.add_argument("--quran-lemmas", type=Path, default=Path("data/processed/arabic/classical/sources/quran_lemmas_enriched.jsonl"))
    ap.add_argument("--output", type=Path, default=Path("data/processed/arabic/classical/arabic_words_binary_roots.jsonl"))
    ap.add_argument("--weak-letters", type=str, default=DEFAULT_WEAK_LETTERS, help="Letters removed when forming the preferred binary root.")
    ap.add_argument("--keep-missing-root", action="store_true", help="Keep rows where `root` is missing/empty (binary_root will be empty).")
    args = ap.parse_args()

    total = build(
        word_root_map_path=args.word_root_map,
        quran_lemmas_path=args.quran_lemmas,
        out_path=args.output,
        weak_letters=str(args.weak_letters or ""),
        keep_missing_root=bool(args.keep_missing_root),
    )
    print(f"Wrote {total} records to {args.output}")


if __name__ == "__main__":
    main()
