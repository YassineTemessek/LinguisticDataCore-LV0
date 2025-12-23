from __future__ import annotations

from pathlib import Path

from .base import AdapterResult


class ConceptsAdapter:
    """
    Stub adapter for concepts dataset (e.g., concepts_v3_2_enriched).
    Expected input: data/processed/concepts/concepts_v3_2_enriched.jsonl or raw upstream.
    Output: LV0.7-aligned JSONL with manifest.
    """

    def run(self, *, input_dir: Path, output_path: Path, manifest_path: Path) -> AdapterResult:
        # TODO: implement deterministic parsing + ID generation and write manifest.
        raise NotImplementedError("ConceptsAdapter.run is not implemented yet.")

