# Pipeline Modernization Review (Friend PDF → Action Plan)

This document is a working synthesis of:
- The PDF you received: **“Modernizing the LinguisticComparison Pipeline” (Dec 2025)**.
- Your stated direction for the LV0→LV4 project.
- A concrete “best-practice” plan for making the system reliable and reusable across many raw sources and languages.

It is written so you can confirm we’re aligned before we compare “my plan” vs. your friend’s full plan.

---

## 1) What Your Friend’s PDF Proposes (My Reading)

### 1.1 Core shift (LV3)
- Replace the classical LV3 pipeline (IPA extraction → edit distance → n-grams → concept buckets → hand weights) with **neural embeddings**:
  - **SONAR** for *semantic similarity* (cross-lingual meaning space).
  - **CANINE** for *form similarity* (character-level patterns, any script).
- Use **cosine similarity** as the scoring primitive.
- Use **FAISS** nearest-neighbor search for scalable retrieval; concept registry becomes optional.
- Keep the classical pipeline as an **on-demand interpretability / sanity-check track**, not the production path.

### 1.2 Ripple effects (LV0/LV2/LV4)
- **LV0** becomes responsible for **precomputing and versioning embeddings** (expensive compute once, cached for all consumers).
- **LV2** (Arabic clustering) keeps its clustering algorithm but swaps similarity signals:
  - Form: CANINE (instead of char-gram Jaccard).
  - Meaning: SONAR over gloss/definitions (instead of token Jaccard).
- **LV4** null models become easier: build baselines by **shuffling embeddings / random pairing** instead of elaborate phonotactic null models.

### 1.3 Proto-reconstruction (optional “Part Three”)
- After LV3 discovery + LV4 validation, project embeddings into **MMS‑VITS** latent space to generate **audible proto-forms**.
- This is framed as a future research direction, not required to modernize LV0–LV4.

---

## 2) What I Understand *You* Want (Current Intent)

### 2.1 Project structure (levels)
- **LV0 (data core):** ingest raw sources → produce canonical processed datasets with stable schema and per-language release bundles.
- **LV2 (Arabic decoding/clustering):** cluster Arabic by **binary root** first; meaning comes later.
- **LV3 (cross-language discovery):** move to SONAR/CANINE as main engine; keep classical pipeline as backup/interpretability.
- **LV4 (theory/validation):** validate candidates (null models, chronology locks remain manual).

### 2.2 Language coverage goals
- Treat **Quranic Arabic** as an independent language (Quran-only vocabulary) separate from general Arabic.
- Keep **general Arabic** in LV0.
- Add **German** and other **eastern Indo-European** languages as sources are provided.
- Include additional Semitic targets (you mentioned Akkadian, Syriac, Old Hebrew) and bundle them.

### 2.3 Your current “form vs meaning” choices
- **Form signals:**
  - Arabic: compare primarily using **transliteration**.
  - Other languages: compare using **lemma + IPA**.
- **Meaning:** not decided yet; you want to focus on binary-root clustering first.
- **SONAR:** you suggested embedding **the word itself**.

---

## 3) What I Think Is Best (Concrete Plan)

The modernization is good, but it **does not replace LV0 polishing**. In practice, embeddings *amplify* whatever quality (or noise) LV0 emits.

### 3.1 Principle: treat “form text” and “meaning text” as separate first-class artifacts
For each lexeme row LV0 should be able to produce:
- **Form representation** (what the word “is”):
  - `lemma` (native script)
  - `translit` (if applicable)
  - `ipa` (if available)
- **Meaning representation** (what the word “means”):
  - `gloss_plain` / `definition` (preferably consistent language, e.g. English)
  - optional concept tags later (not required for search if embeddings + FAISS work well)

Then:
- **CANINE** should embed the *form representation* (or a canonical “form_text” field).
- **SONAR** should embed the *meaning representation* (or a canonical “meaning_text” field).

This keeps the system multipurpose:
- You can use CANINE without meanings (LV2 early stage).
- You can use SONAR once you have gloss/definition sources (LV3 discovery).

### 3.2 Recommendation on SONAR “word-only” embeddings
Embedding only the word string is usually weak cross-lingually (little context, ambiguity, script effects).

Best practice:
- Use SONAR primarily on **gloss/definition text** (or “`<lemma> — <short definition>`”).
- If you still want SONAR(word) as a signal, keep it as a **secondary** feature, not the main semantic signal.

### 3.3 LV2: binary-root-first, then refine
Your LV2 approach is valid:
1) **Bucket by binary root** (fast, deterministic).
2) Inside each bucket:
   - Start with **CANINE(form)** to split/merge candidates based on shape/morphology patterns.
   - Later add **SONAR(meaning)** when LV0 supplies reliable meanings (gloss/definition).
3) Keep classical metrics to explain “why” when reviewing merges.

### 3.4 LV3: retrieval + rerank (the stable pattern)
Recommended LV3 flow:
1) Retrieve candidates by **SONAR(meaning)** (FAISS top‑K).
2) Rerank/filter by **CANINE(form)** (+ optional classical checks).
3) Only then do heavier validation (LV4 null models / chronology locks).

This avoids “semantic-only” false positives and “form-only” false positives.

### 3.5 LV0: what “primary polishing” should mean
To support many raw file types and languages, LV0 should standardize:
- **Raw layout convention**: `data/raw/<language>/<source>/...` + a small `source.toml` (or YAML) describing parsing rules and output targets.
- **Adapters**: CSV/TSV/JSONL/JSON/XML/Parquet/StarDict → canonical JSONL rows.
- **Provenance**: always include `source`, `source_ref`, stable `id`, and minimal required fields.
- **Registry + manifests**: LV0 outputs a registry listing datasets by `(language, stage, source)` with counts/hashes, plus embedding metadata when present.

### 3.6 Embeddings as LV0 outputs (aligned with the PDF)
When you’re ready, LV0 should output embeddings alongside lexemes, versioned:
- Example: `data/processed/<dataset>/lexemes.jsonl`
- Example: `data/processed/<dataset>/embeddings/sonar.npy` and `.../canine.npy`
- Example: `outputs/manifests/<dataset>_<date>.json` includes:
  - model id + dim
  - row alignment strategy (must match stable IDs)
  - hashes for reproducibility

---

## 4) Summary: How This Differs From Your Friend’s Plan

Your friend’s PDF focuses on LV3 modernization and describes LV0 embedding precompute at a high level.

My plan adds two practical clarifications:
1) **Meaning embeddings should usually come from gloss/definition text**, not word-only strings.
2) LV0 needs a **format-agnostic ingestion framework** (configs + adapters + registry) so “any raw data we provide” reliably becomes the same processed layout.

Everything else is compatible: SONAR/CANINE main engine, classical pipeline preserved for interpretability, LV0 as the central cache, LV2 improved via embeddings, LV4 baselines via embedding null models.

---

## 5) Decisions You Need to Confirm (So We Don’t Drift)

1) For LV3 “meaning”: do you want to standardize on **English gloss/definitions** as the primary meaning text (when available)?
2) For LV2 Arabic: should CANINE run on **Arabic translit**, **Arabic script**, or **a combined form_text** (`lemma || translit`)?
3) For “languages from raw”: do you want LV0 to:
   - auto-discover sources by folder layout only, or
   - require a small `source.toml` per dataset (recommended for reproducibility)?
4) Do you want to pursue the MMS‑VITS proto-audio part now, or keep it explicitly “future work” until LV0–LV4 are stable?

