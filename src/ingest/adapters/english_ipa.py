from __future__ import annotations

from pathlib import Path

from .base import AdapterResult


class EnglishIPAAdapter:
    """
    Stub adapter for English IPA merged dataset.
    Expected input: data/raw/english/... (ipa-dict, cmudict).
    Output: data/processed/english/english_ipa_merged_pos.jsonl (LV0.7 schema).
    """

    def run(self, *, input_dir: Path, output_path: Path, manifest_path: Path) -> AdapterResult:
        # TODO: implement deterministic parsing + ID generation and write manifest.
        raise NotImplementedError("EnglishIPAAdapter.run is not implemented yet.")

