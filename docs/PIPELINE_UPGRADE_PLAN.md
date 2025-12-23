# Pipeline Upgrade Plan (LV0→LV4)

This plan follows the work order you provided. It keeps the classical pipeline for interpretability while moving discovery to SONAR/CANINE with reproducible, cacheable artifacts. Priority order is fixed: Phase 1+2 → 3 → 4 → 5 → 7 → 6 → 8.

## Canonical outputs to preserve (no rename)
- data/processed/arabic/quran_lemmas_enriched.jsonl
- data/processed/arabic/hf_roots.jsonl
- data/processed/english/english_ipa_merged_pos.jsonl
- data/processed/wiktionary_stardict/*_filtered.jsonl
- data/processed/concepts/concepts_v3_2_enriched.jsonl
- data/processed/anchors/*.csv

## Phase 0 — Inventory + Guardrails (current step)
- Map existing ingestion scripts and outputs.
- Define schemas/contracts (see docs/SCHEMA_LV0_7.md).
- Identify where manifests/registries need to be added.

Deliverables: this file + docs/SCHEMA_LV0_7.md.

## Phase 1 — Adapters + Registry + Manifests (LV0.7 ingestion discipline)
- Adapter interface under src/ingest/adapters/.
- Adapters for: Qur’an lemmas, English IPA merged, Wiktionary filtered, concepts.
- Registry: data/processed/registry/datasets.json (name, version, adapter, outputs, counts, hashes, created_at, notes).
- Per-output manifest (*.manifest.json) with sha256, row_count, schema_version, command, git commit, timestamp, id policy.
- Stable deterministic IDs: {language}:{stage}:{source}:{normalized_lemma}:{pos_joined}:{disambiguator}; normalized_lemma = NFKC, lower, trimmed, whitespace-collapsed. Collision handling documented.

## Phase 2 — Deterministic text fields (form_text, meaning_text)
- Script to build/add form_text and meaning_text consistently.
- form_text rules: Arabic = lemma (Arab script) + translit marker; Latin scripts = lemma + optional IPA tag. No gloss here.
- meaning_text rules: prefer gloss_plain/definition in English; fallback: "<lemma> — <short definition>" with a flag; never word-only unless flagged.
- Coverage report (% rows with meaning_text).

## Phase 3 — Embedding artifacts (SONAR meaning, CANINE form)
- For each dataset JSONL: store embeddings at data/processed/embeddings/<dataset>/<model_id>/.
- Files: ids.json (ordered ids), vectors.npy (float32), meta.json (model id/hash, dim, pooling, text_field), coverage.json.
- Deterministic ordering (sorted ids). Missing text ⇒ skip but record; never misalign.

## Phase 4 — FAISS indexes + search utilities
- Build FAISS indexes per space (meaning/form).
- Store index.faiss + index_meta.json + ids.json.
- CLI tools for search: meaning (SONAR) and form (CANINE); batch vector→neighbors supported.

## Phase 5 — LV3 retrieve → rerank → annotate (no hard filters)
- Retrieve by SONAR(meaning_text) where available; rerank by CANINE(form_text).
- Add classical interpretability features (edit distance on translit/IPA, length ratio, Arabic root overlap when applicable).
- Outputs: JSONL candidates with separate signals, flags, provenance, ranks; stored under data/processed/lv3/candidates_<run_id>.jsonl + manifest.

## Phase 6 — Calibration (after labels exist)
- Label format: data/processed/review/labels.jsonl (query_id, cand_id, label, reasons, notes, reviewer, timestamp).
- Calibrator on features (sonar_cosine, canine_cosine, edit_distance_norm, length_ratio, flags). Logistic/isotonic to start.
- Output calibrated candidates + calibration report.

## Phase 7 — LV4 validation (null models + ablations)
- Structure-preserving nulls: shuffle within length bin, script family, frequency band (if available), concept/gloss cluster, Arabic binary-root bucket.
- Compute p-values/FDR for top-N; stability across seeds.
- Ablations: drop SONAR, drop CANINE, drop classical metrics (and optionally flags).
- Report: data/processed/reports/lv4_validation_<run_id>.md.

## Phase 8 — QA/Drift reports
- Per run: counts, missingness (meaning_text, ipa), embedding coverage/model IDs, candidate stats, LV4 summary, diff vs. previous run.
- Output: data/processed/reports/qa_<run_id>.md.

## Non-negotiable rules (tracking here)
- Discovery-first: no hard filtering; only flags/annotations.
- Reproducible artifacts: deterministic order, stable IDs, hashes, model version recorded.
- Separate signals retained; calibrated score is optional later.
- No hidden row-order dependency; ids.json must define vector order.
- Canonical outputs stay under data/processed/; intermediates under data/processed/_parts/ or tools outputs.

