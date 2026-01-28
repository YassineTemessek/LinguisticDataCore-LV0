# Raw Data Flow (Resources -> LV0 Raw -> LV0 Processed)

This repo consumes raw datasets from the project-wide Resources folder.
Use junctions/hardlinks under data/raw to avoid duplicating large files.

Flow summary:
1. Update raw datasets under Resources/.
2. Run scripts/setup_raw_links.ps1 to create links into data/raw.
3. Run ldc ingest ... to generate data/processed outputs.

Notes:
- data/raw should stay thin; do not copy large datasets.
- data/processed is the canonical output for downstream levels.
