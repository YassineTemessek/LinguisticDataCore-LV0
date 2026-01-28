from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Add src to path so we can import adapters
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT / "src"))

from ingest.adapters.quran_lemmas import QuranLemmasAdapter
from ingest.adapters.english_ipa import EnglishIPAAdapter
from ingest.adapters.wiktionary_filtered import WiktionaryFilteredAdapter
from ingest.adapters.concepts import ConceptsAdapter


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", type=Path, default=REPO_ROOT)
    ap.add_argument("--output-dir", type=Path, default=REPO_ROOT / "data" / "processed" / "canonical")
    ap.add_argument("--manifest-dir", type=Path, default=REPO_ROOT / "outputs" / "manifests" / "adapters")
    args = ap.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.manifest_dir.mkdir(parents=True, exist_ok=True)

    # 1. Quran Lemmas
    print("Running QuranLemmasAdapter...")
    q_adapter = QuranLemmasAdapter()
    q_adapter.run(
        input_dir=args.input_dir,
        output_path=args.output_dir / "quranic_arabic" / "lexemes.jsonl",
        manifest_path=args.manifest_dir / "quranic_arabic_lexemes.manifest.json"
    )

    # 2. English IPA
    print("Running EnglishIPAAdapter...")
    e_adapter = EnglishIPAAdapter()
    e_adapter.run(
        input_dir=args.input_dir,
        output_path=args.output_dir / "english" / "modern" / "lexemes.jsonl",
        manifest_path=args.manifest_dir / "english_modern_lexemes.manifest.json"
    )

    # 3. Wiktionary Filtered (Latin as example)
    print("Running WiktionaryFilteredAdapter (Latin)...")
    w_adapter = WiktionaryFilteredAdapter()
    w_adapter.run(
        input_dir=args.input_dir,
        input_file_name="Latin-English_Wiktionary_dictionary_stardict_filtered.jsonl",
        output_path=args.output_dir / "latin" / "old" / "lexemes.jsonl",
        manifest_path=args.manifest_dir / "latin_old_lexemes.manifest.json"
    )
    
    # 4. Concepts
    print("Running ConceptsAdapter...")
    c_adapter = ConceptsAdapter()
    c_adapter.run(
        input_dir=args.input_dir,
        output_path=args.output_dir / "concepts" / "concepts_v3_2.jsonl",
        manifest_path=args.manifest_dir / "concepts_v3_2.manifest.json"
    )

    print("Success. Canonical outputs in:", args.output_dir)


if __name__ == "__main__":
    main()
