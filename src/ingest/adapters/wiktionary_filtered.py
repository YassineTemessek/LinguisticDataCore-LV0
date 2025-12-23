from __future__ import annotations

from pathlib import Path

from .base import AdapterResult


class WiktionaryFilteredAdapter:
    """
    Stub adapter for Wiktionary stardict filtered outputs (Latin/Greek/Arabic/Hebrew/etc.).
    Expected input: data/processed/wiktionary_stardict/*_filtered.jsonl (or raw/enriched sources).
    Output: LV0.7-aligned filtered JSONL with manifest.
    """

    def run(self, *, input_dir: Path, output_path: Path, manifest_path: Path) -> AdapterResult:
        # TODO: implement deterministic parsing + ID generation and write manifest.
        raise NotImplementedError("WiktionaryFilteredAdapter.run is not implemented yet.")

