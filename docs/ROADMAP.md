# LV0 Roadmap (Ordered)

LV0 is the shared data core: raw → canonical processed datasets → validated → released as per-language bundles (date versioning).

This roadmap is focused on keeping data stable and reproducible for LV2/LV3/LV4.

## Phase 0: Stabilize contracts (now)

- Freeze the canonical “lexeme row” contract (required keys + optional keys) and document it.
- Define stable file naming conventions under `data/processed/` per language/source.
- Ensure every processed file has provenance fields (source name, stage/script, and stable ids).
- For Arabic rows with a known `root`, include `root_norm` and `binary_root` (canonical: first 2 letters of the accepted root).

## Phase 1: Validation gates (must-have)

- Expand `scripts/ingest/validate_processed.py` to enforce:
  - required keys present (`id`, `lemma`, `language/lang`, `source` as applicable)
  - `translit` and `ipa` fields exist (may be empty early)
  - no empty `lemma`
  - `id` uniqueness within each file
  - consistent encoding and JSONL correctness
- Add KPI reports that are treated as “release blockers”:
  - row counts
  - missing IPA/translit rates
  - duplicates by `(language, stage, lemma)` and by `id`

## Phase 2: Per-language release bundles (date versioning)

Release format:

- Tag: `YYYY.MM.DD`
- Assets (per language): `<language>_<YYYY.MM.DD>.zip`
- Manifest: `manifest_<YYYY.MM.DD>.json` (file lists + counts + source versions)

Milestones:

- Ensure `ldc package --version YYYY.MM.DD` produces:
  - Arabic bundle (arabic + Arabic-related tables)
  - English bundle (including parts if present)
  - Greek bundle
  - Latin bundle
  - Concepts bundle (`resources/concepts`)
  - Anchors bundle (`resources/anchors`)
- Ensure `ldc fetch --release <tag|latest> --dest <path>` downloads and extracts bundles into `data/processed/...`.

## Phase 3: Dataset registry API (developer UX)

- Provide a small Python API that downstream repos can use:
  - list available datasets by `(language, stage, source)`
  - resolve canonical paths
  - load JSONL with consistent types

## Phase 4: Normalization improvements (quality)

- IPA normalization (clear policy; consistent symbols and spacing)
- Transliteration policy per script (Arabic, Greek, Syriac, etc.)
- Optional: “stage normalization” helper (LV0 keeps stage as free text but can provide canonical suggestions)

## Phase 5: Downstream integration checks

- Add “consumer smoke tests”:
  - LV2 expects Arabic bundle contains binary-root-ready tables
  - LV3 expects multilingual bundles contain lexeme tables compatible with discovery retrieval

## Open questions (to decide once contributors join)

- Which processed outputs are “required canonicals” vs “optional extras” per language?
- What’s the minimal provenance schema that all sources must include?
- Should bundle manifests include content hashes for each file?
