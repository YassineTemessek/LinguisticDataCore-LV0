# LV0.7 Schema (Canonical Processed JSONL Rows)

Applies to all processed lexeme tables produced by adapters and used for embeddings. Each row is one JSON object.

## Required fields
- `id` (string): stable, deterministic (see ID policy below)
- `lemma` (string)
- `language` (string): ISO 639 code (e.g., ara, ara-qur, eng, grc, lat, deu, etc.)
- `stage` (string): e.g., quranic, classical, modern, proto, unknown
- `script` (string): ISO 15924 (e.g., Arab, Latn, Grek, Hebr, Cyrl, etc.)
- `source` (string): dataset name + version identifier
- `lemma_status` (string): e.g., attested, reconstructed, variant, uncertain

## Optional/normalized fields
- `ipa_raw`, `ipa` (string): raw IPA and normalized IPA (strip wrappers, normalize spacing/stress)
- `pos` (list of strings)
- `gloss_html`, `gloss_plain` (string)
- `form_text` (string): canonical text for CANINE embeddings (deterministic rules)
- `meaning_text` (string): canonical text for SONAR embeddings (deterministic rules)
- Additional provenance: `source_ref`, `sources`, `n_sources`, etc., as already used.

## form_text rules (deterministic)
- Arabic:
  - Base: Arabic-script lemma.
  - If translit is available, append with a clear marker, e.g., `AR: <lemma> | TR: <translit>`.
  - If IPA exists, append `| IPA: <ipa>` optionally (short).
- Latin-script languages:
  - Base: lemma.
  - If IPA exists, append `| IPA: <ipa>`.
- Never include gloss/definition in form_text.
- Keep spacing/casing consistent; avoid language-specific punctuation in the marker strings.

## meaning_text rules (deterministic)
- Prefer `gloss_plain` in English (or the project’s chosen pivot language).
- If gloss exists: `"<gloss_plain>"`.
- If gloss missing but concept/definition exists: `"<lemma> — <short_definition_or_concept>"` and set a flag in coverage (not stored on row).
- If nothing exists, leave empty; do not fall back silently to word-only.

## ID policy (deterministic)
Recommended pattern (documented per adapter):
`{language}:{stage}:{source}:{normalized_lemma}:{pos_joined}:{disambiguator}`

- `normalized_lemma`: NFKC, lowercased, trimmed, whitespace collapsed.
- `pos_joined`: POS tags joined with `+` (or `_`), empty if none.
- `disambiguator`: integer suffix if collisions occur; increment deterministically by sorted input order.
- Collision handling must be documented in adapter manifest; never drop/merge silently.

## Manifests (per output)
For every JSONL produced, write a sibling `<file>.manifest.json` containing:
- `file`: path
- `sha256`: hash
- `row_count`
- `schema_version`: "lv0.7"
- `generated_by`: command or script path + args
- `git_commit`: if available
- `timestamp_utc`
- `id_policy`: short description (e.g., pattern above)

## Embedding alignment contract
- Embedding files must include `ids.json` (ordered list of ids) and `vectors.npy` aligned 1:1.
- Order must be deterministic: sorted by `id` unless explicitly documented otherwise.
- `meta.json` records model name/id/hash, dim, pooling, text_field used, created_at, source file hashes.
- `coverage.json` records counts of embedded rows vs. skipped rows (missing text, etc.).

## Registry (datasets)
- `data/processed/registry/datasets.json` lists each dataset with: name, version, adapter, outputs, counts, hashes, created_at, notes.
- Adapters must record their ID policy and any collision handling notes here.

## Examples
```json
{
  "id": "ara-qur:quranic:quranic-corpus:كتب:verb:1",
  "lemma": "كتب",
  "language": "ara-qur",
  "stage": "quranic",
  "script": "Arab",
  "source": "quranic-corpus-morphology:v1",
  "lemma_status": "attested",
  "ipa": "kataba",
  "pos": ["verb"],
  "gloss_plain": "to write",
  "form_text": "AR: كتب | TR: kataba | IPA: kataba",
  "meaning_text": "to write"
}
```

