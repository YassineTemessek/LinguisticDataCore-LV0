# Session Start (LV0)

Use this file to resume work quickly in a new terminal session.

## Current state (LV0)

- LV0 is the deterministic data core.
- Canonical outputs are per language/stage:
  - `data/processed/<language>/<stage>/sources/<source>.jsonl`
  - `data/processed/<language>/<stage>/lexemes.jsonl`
- Required row fields: `id`, `lemma`, `language`, `source`, `lemma_status`, `translit`, `ipa`.
- Arabic: if `root` exists, LV0 derives `root_norm` + `binary_root` (first 2 letters of `root_norm`).
- Arabic merge priority: Qur’an (if present) → word_root_map → HF roots.

## Arabic focus (current priority)

Goal: compare Arabic **binary roots ↔ tri-root words**, then compare Arabic tri-root to Indo‑European languages.
Chinese/Old Egyptian are later.

## Where to start

0) Read project notes: `ReadMe.txt`
1) Place raw data locally (not committed):
   - See `data/raw/README.md` for expected paths.
2) Run LV0 ingest:
   - `ldc ingest --all`
3) Validate:
   - `ldc validate --all --require-files`
4) Confirm canonical output exists:
   - `data/processed/arabic/classical/lexemes.jsonl`

## Downstream usage

LV2 (Arabic internal QA):
- Cluster: `python "scripts/cluster/cluster_by_binary_root.py"`
- QA binary vs tri-root: `python "scripts/analysis/compare_binary_vs_triroot.py"`

LV3 (Arabic ↔ Indo‑European runs):
- See `LinguisticComparison/docs/START_HERE.md` for example commands.

## Notes

- Raw and processed data are not committed by default.
- This repo should remain deterministic; model-based tools belong in LV3.

