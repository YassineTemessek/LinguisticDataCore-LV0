"""
Merge Arabic (classical) processed sources into a single canonical lexeme table.

Inputs (default):
  - data/processed/arabic/classical/quran_lemmas_enriched.jsonl
  - data/processed/arabic/classical/word_root_map_filtered.jsonl
  - data/processed/arabic/classical/hf_roots.jsonl
  - data/processed/arabic/classical/arabic_words_binary_roots.jsonl

Output (default):
  - data/processed/arabic/classical/lexemes.jsonl

Notes:
  - This is a *canonical convenience* file: LV0 keeps source-specific files too.
  - De-dupe key: (lemma, root_norm). For rootless rows, key is (lemma, "").
  - `translit` and `ipa` fields exist on every output row (may be empty).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from processed_schema import ensure_min_schema


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _has_text(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _best_status(a: str, b: str) -> str:
    rank = {"gold": 4, "silver": 3, "auto": 2, "auto_brut": 1}
    ra = rank.get((a or "").strip(), 0)
    rb = rank.get((b or "").strip(), 0)
    return a if ra >= rb else b


def _merge_list_field(dst: dict[str, Any], src: dict[str, Any], key: str) -> None:
    cur = dst.get(key)
    nxt = src.get(key)
    if not nxt:
        return
    if cur is None:
        dst[key] = [nxt] if not isinstance(nxt, list) else list(nxt)
        return
    if not isinstance(cur, list):
        cur = [cur]
    if isinstance(nxt, list):
        cur.extend(nxt)
    else:
        cur.append(nxt)
    # de-dupe preserving order
    seen: set[str] = set()
    out: list[Any] = []
    for item in cur:
        s = str(item)
        if s in seen:
            continue
        seen.add(s)
        out.append(item)
    dst[key] = out


def _pick(dst: dict[str, Any], src: dict[str, Any], key: str) -> None:
    if dst.get(key):
        return
    v = src.get(key)
    if v is None or v == "" or v == []:
        return
    dst[key] = v


@dataclass(frozen=True)
class SourceFile:
    path: Path
    tag: str


def merge_sources(sources: list[SourceFile], *, out_path: Path) -> dict[str, int]:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    merged: dict[tuple[str, str], dict[str, Any]] = {}
    rows_in = 0

    for src in sources:
        if not src.path.exists():
            continue
        for rec in iter_jsonl(src.path):
            rows_in += 1
            lemma = str(rec.get("lemma") or "").strip()
            if not lemma:
                continue
            root_norm = str(rec.get("root_norm") or rec.get("root") or "").strip()
            key = (lemma, root_norm)

            cur = merged.get(key)
            if cur is None:
                cur = {
                    "lemma": lemma,
                    "language": str(rec.get("language") or "ara").strip() or "ara",
                    "source": "lv0:arabic:classical:lexemes",
                    "source_ref": f"merge:{lemma}|{root_norm}",
                    "lemma_status": str(rec.get("lemma_status") or "auto_brut"),
                    "sources": [],
                    "source_refs": [],
                }
                merged[key] = cur

            cur["lemma_status"] = _best_status(str(cur.get("lemma_status") or ""), str(rec.get("lemma_status") or ""))
            _merge_list_field(cur, {"sources": src.tag}, "sources")
            if _has_text(rec.get("source_ref")):
                _merge_list_field(cur, {"source_refs": str(rec.get("source_ref"))}, "source_refs")

            # Prefer canonical root-derived fields when present.
            for k in ("root", "root_norm", "binary_root", "binary_root_method", "binary_root_first2", "binary_root_weakless_first2"):
                _pick(cur, rec, k)

            # Prefer translit/ipa
            for k in ("translit", "ipa", "ipa_raw"):
                _pick(cur, rec, k)

            # Gloss/definition-like fields
            for k in ("gloss_plain", "gloss_html", "definition"):
                _pick(cur, rec, k)

            # POS and example fields
            _merge_list_field(cur, rec, "pos")
            _pick(cur, rec, "pos_tag")
            _pick(cur, rec, "example_surface")

    wrote = 0
    with out_path.open("w", encoding="utf-8") as out_f:
        for (lemma, root_norm), rec in sorted(merged.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            # Cleanup: compact lists
            rec["sources"] = sorted(set(rec.get("sources") or []))
            rec["source_refs"] = sorted(set(rec.get("source_refs") or []))
            rec["n_sources"] = len(rec["sources"])
            rec = ensure_min_schema(rec, default_language="ara", default_source="lv0:arabic:classical:lexemes", default_lemma_status="auto_brut")
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            wrote += 1

    return {"rows_in": rows_in, "rows_out": wrote}


def main() -> None:
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("--quran", type=Path, default=Path("data/processed/arabic/classical/quran_lemmas_enriched.jsonl"))
    ap.add_argument("--word-root-map", type=Path, default=Path("data/processed/arabic/classical/word_root_map_filtered.jsonl"))
    ap.add_argument("--hf-roots", type=Path, default=Path("data/processed/arabic/classical/hf_roots.jsonl"))
    ap.add_argument("--binary-root-lexicon", type=Path, default=Path("data/processed/arabic/classical/arabic_words_binary_roots.jsonl"))
    ap.add_argument("--output", type=Path, default=Path("data/processed/arabic/classical/lexemes.jsonl"))
    args = ap.parse_args()

    sources = [
        SourceFile(path=args.quran, tag="quranic-corpus-morphology"),
        SourceFile(path=args.word_root_map, tag="word_root_map.csv"),
        SourceFile(path=args.hf_roots, tag="arabic_roots_hf"),
        SourceFile(path=args.binary_root_lexicon, tag="lv0:arabic_binary_root_lexicon"),
    ]
    stats = merge_sources(sources, out_path=args.output)
    print(f"Wrote {stats['rows_out']} rows to {args.output} (scanned={stats['rows_in']})")


if __name__ == "__main__":
    main()

