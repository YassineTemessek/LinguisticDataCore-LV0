# LinguisticDataCore (LV0) 📦

![level](https://img.shields.io/badge/level-LV0-6f42c1)
![license](https://img.shields.io/badge/license-MIT-blue)

LV0 is the shared **data core**: it turns raw sources into **canonical processed datasets** (JSONL/CSV), validates them, and ships **per-language release bundles**.

All higher levels should *consume* LV0 outputs instead of re-ingesting data independently.

## Project map 🧭

- LV0 (this repo): `https://github.com/YassineTemessek/LinguisticDataCore-LV0`
- LV2 (Arabic decoding & clustering): `https://github.com/YassineTemessek/Arabic-s-Words-decoding-LV2`
- LV3 (cross-language discovery pipeline): `https://github.com/YassineTemessek/LinguisticComparison`
- LV4 (theory & validation blueprint): `https://github.com/YassineTemessek/OriginOfLanguagesLvl4`

## What LV0 produces ✅

- Canonical processed tables: `data/processed/` (local, not committed by default)
- Manifests & QA outputs: `outputs/`
- Release assets: `outputs/release_assets/` (per-language zip bundles + manifest JSON)

Arabic (not exhaustive) typically includes:

- Quranic Arabic (`ara-qur`, Quran-only):
  - `data/processed/quranic_arabic/sources/quran_lemmas_enriched.jsonl`
  - `data/processed/quranic_arabic/lexemes.jsonl`
- Arabic (general, `ara`):
  - `data/processed/arabic/classical/sources/word_root_map_filtered.jsonl`
  - `data/processed/arabic/classical/sources/hf_roots.jsonl`
  - `data/processed/arabic/classical/lexemes.jsonl` (canonical merged file ready for LV2/LV3)

## Quickstart 🚀

Install (editable):

- `python -m pip install -e .`
- CLI: `ldc --help`

Build locally:

1) Put raw sources under `data/raw/` (see `scripts/ingest/` for expected layout per source).
2) Build processed outputs: `ldc ingest --all`
3) Validate: `ldc validate --all --require-files`
4) Package per-language bundles (date versioning `YYYY.MM.DD`): `ldc package --version 2025.12.19`

Consume releases (downstream):

- `ldc fetch --release latest --dest ./`

## Docs 📚

- Roadmap (ordered): `docs/ROADMAP.md`
- Arabic fields (root + binary root): `docs/ARABIC_FIELDS.md`

## Contact 🤝

For collaboration: `yassine.temessek@hotmail.com`
