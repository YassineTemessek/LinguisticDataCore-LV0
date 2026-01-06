# LV0 Raw Data (Not Committed)

This folder is where contributors place **raw source datasets** locally before running `ldc ingest`.

Raw data is intentionally **not committed** to Git by default (size/licensing/provenance).

## Recommended layout

Use a consistent dataset folder structure:

- `data/raw/<source>/<language>/<stage>/...`

Examples (Arabic, classical):

- `data/raw/arabic/quran-morphology/quran-morphology.txt`
- `data/raw/arabic/word_root_map.csv`
- `data/raw/arabic/arabic_roots_hf/train-00000-of-00001.parquet`

## Arabic source checklist (optional)

- Quran morphology: `data/raw/arabic/quran-morphology/quran-morphology.txt`
- Word root map: `data/raw/arabic/word_root_map.csv`
- HF roots: `data/raw/arabic/arabic_roots_hf/train-00000-of-00001.parquet`

## Notes

- `stage` is treated as a dataset boundary in LV0 (folder/file level), not a required per-row field.
- After ingest, LV0 writes per-source processed files under `data/processed/<language>/<stage>/sources/` and a merged canonical `lexemes.jsonl`.
