from __future__ import annotations

from pathlib import Path

from .base import AdapterResult


class QuranLemmasAdapter:
    """
    Stub adapter for Quran lemmas (quranic-corpus-morphology).
    Expected input: data/raw/arabic/quran-morphology/.
    Output: data/processed/arabic/quran_lemmas_enriched.jsonl (LV0.7 schema).
    """

    def run(self, *, input_dir: Path, output_path: Path, manifest_path: Path) -> AdapterResult:
        # TODO: implement deterministic parsing + ID generation and write manifest.
        raise NotImplementedError("QuranLemmasAdapter.run is not implemented yet.")

