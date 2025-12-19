# LinguisticDataCore (LV0)

LV0 is the shared **data core** for the project: it turns raw sources into **canonical processed datasets** (JSONL/CSV) with validation, manifests, and release packaging.

All higher levels (LV2/LV3/LV4) should *consume* LV0 processed outputs instead of re-ingesting data independently.

## What LV0 produces

- Canonical processed tables under `data/processed/` (local, not committed by default)
- Build manifests under `outputs/manifests/`
- Release assets under `outputs/release_assets/` (per-language zip bundles + manifest JSON)

## Install (package)

This repo is also a pip package:

- `python -m pip install -e .`

After install, the CLI entrypoint is:

- `ldc --help`

## Quickstart (build locally)

1) Put raw datasets under `data/raw/` (see `scripts/ingest/` for expected layout per source).
2) Build processed outputs:

- `ldc ingest --all`

3) Validate:

- `ldc validate --all --require-files`

4) Package per-language bundles (date versioning):

- `ldc package --version 2025.12.19`

## Quickstart (consume releases)

Downstream repos can fetch LV0 release bundles instead of rebuilding:

- `ldc fetch --release latest --dest ./`

This extracts into the destination so `data/processed/...` exists.

## Docs

- `docs/ROADMAP.md`
