

# 0. Overall Vision

We want to build a multi-level system that

1. Starts from the Qur’an as a self-contained semantic universe.
2. Generalizes to the entire Arabic language as a “genome” of roots and derivations.
3. Expands to cross-linguistic mapping, showing how other languages relate back to a bi-consonantal Arabic root system.

We divide this into four distinct but related research levels

 Level 1 - Qur'anic Word Meaning (Triliteral Level)
 Level 2 - Arabic Language Genome (Biconsonantal Level)
 Level 3 - Similarity Scoring & Ranked Candidate Discovery (Arabic vs other languages)
 Level 4 - Cross-Linguistic Root Mapping & Hypothesis Testing (builds on Level 3; intersects early Arabic development)

The system should be able to

 Read structured data (CSVDB) about words, roots, and contexts.
 Build numerical representations (vectors) for roots and words based on their usage.
 Discover patterns, clusters, oppositions, and semantic distances.
 Do this with minimal theological bias, focusing on the text and lexica themselves.

---

# 1. Core Linguistic Philosophy

The user adopts the theory of Dr. Muhammad Hasan Jabal

 The true original root in Arabic (especially Qur’anic Arabic) is biconsonantal (2-letter).
 The triliteral and quadriliteral roots are constructions built on top of these 2-letter nuclei by adding extra consonants and patterns.
 For practical reasons

   Level 1 will work with standard triliteral roots from existing corpora (what tools provide today).
   Level 2 will explicitly move down to 2-letter roots and try to reconstruct the deeper structure.
 This biconsonantal view is foundational and must be kept in mind in all higher-level design.

---

# 2. Level 1 - Qur'anic Word Meaning (Triliteral Level)

## 2.1. Goal

Level 1 is a Qur'an-only semantic engine: it learns meaning from how roots and lemmas are used across verses.
It produces usage clusters, root-to-root similarity distances, and candidate oppositional pairs for human review.

Build a system that

 Works only on Qur’anic text (no external tafsīr in the core computations).
 Uses standard triliteral roots (e.g. ر ج م ، ر ح م ، ج ر م ، س ل م ، ه د ي ، ض ل ل).
 Analyzes how words and roots are used across all verses.
 Computes

   Semantic distances between roots (e.g. هل “رجيم” أقرب إلى الطردالإبعاد أم إلى الرمي بالحجارة؟).
   Clusters of usage

     For a root like ر ح م → clusters for رحمة عامة، أسماء الله، سياقات خاصة، إلخ.
   Oppositional pairs explicitly indicated in the Qur’an

     مجرمين  مسلمين
     مؤمنين  فجار
     هدى  ضلال
     (and conceptual oppositions like رجيم  رحيم)

This level is basically: distributional semantics of Qur'anic words based on triliteral roots.

## 2.2. Data Sources

Level 1 depends on two synchronized sources: token-level morphology + verse text, joined by (`sura`, `ayah`).

For Level 1, we will rely on

1. Quranic Arabic Corpus – Morphology v0.4

    Provides for every token in the Qur’an

      `surah`, `ayah`, `position` (word order),
      `word_form`,
      `lemma`,
      `root` (triliteral/quadriliteral),
      part-of-speech, morphological features.
    This becomes our token-level `word_root_map`.

2. Qur’an text file

    `quran_text.csv` with

      `sura`, `ayah`, `text` (full verse, with or without diacritics).

We will build

 `word_root_map.csv` 

   `sura`, `ayah`, `position`, `word`, `lemma`, `root`, `pos`, ...
 we can join it with `quran_text.csv` on (`sura`, `ayah`).

## 2.3. Root-Based Selection (no ad-hoc regex)

To be complete and safe

 We do not rely on ad-hoc patterns like `رحمرحمرحمترحيمرحمن`.
 Instead, for any root R (e.g. ر ح م) we select

   All rows in `word_root_map` where `root == R`.
 Then we fetch corresponding verses from `quran_text`.

This guarantees

 Every occurrence of that root, in every morphological form in the Qur’an, is included in the analysis.

## 2.4. Pipeline for a Single Root (template)

For root R (e.g. ر ج م)

1. Selection step

    Filter `word_root_map` where `root == ر ج م`.
    Join with `quran_text` to get full verse text.
    Optional deduplicate if multiple words of same root occur in same verse.
    Export to `examples_rjm.csv`

      `sura`, `ayah`, `word_form`, `root`, `text_ayah`, maybe `position`.

2. Encoding (context representations)

    For each verse in `examples_rjm.csv`

      Start with a simple bag-of-words representation

        `CountVectorizer` on `text_ayah`.
      Later: bag-of-roots-by-verse (using root columns) and stronger encoders if needed.

3. Clustering (usage families)

    Apply an unsupervised clustering algorithm (e.g. KMeans) on verse vectors

      e.g. `k = 2` or `k = 3` to see major types of usage.
    For each cluster

      list verses,
      show "central" verse (closest to cluster centroid),
      show most frequent words/roots in that cluster.

4. Interpretation (human-in-the-loop)

    A human analyst (Yassine) reads cluster outputs

      ex for ر ج م

        cluster 1 contexts of threat  expulsion (لأرجمنك واهجرني)
        cluster 2 guess  talk without knowledge (رجماً بالغيب)
    The analyst then writes an interpretation

      e.g. core meaning ~ “forceful projection  expulsion  casting away”.

All of this without telling the machine in advance that "rjm = expel".
We let the distribution of contexts speak first.

## 2.5. Oppositional Pairs (root-level contrasts)

We also want to study pairs of roots which are

 Explicitly contrasted in the Qur'an
 Or conceptually opposite in your theory.

For a pair of roots (A, B)

1. Build two datasets

    `examples_rootA.csv` (all verses where `root == A`)
    `examples_rootB.csv` (all verses where `root == B`)

2. Merge them into one table

    sura  ayah  text_ayah  root_label 
    ----  ----  ---------  ---------- 
    19    46    ...        رجم        
    18    22    ...        رجم        
    1     3     ...        رحم        
    ...   ...   ...        رحم        

3. Vectorize (same `CountVectorizer` across all verses).

4. Compute

    A centroid vector for A

      mean of vectors for `root_label == A`
    A centroid vector for B

      mean of vectors for `root_label == B`
    Cosine similarity/distance between centroids.

5. Visualize

    Use PCA or UMAP to project all verse vectors to 2D.
    Plot

      red points for root A verses,
      blue points for root B verses.
    See how separated or overlapping they are.

6. Interpret

    If AB are supposed to be opposites (مجرمينمسلمين, هدىضلال)

      We expect their clusters to be distinct in semantic space.
    If AB are phonetically related but semantically opposed (رحيمرجيم)

      We see whether their context clouds are near or far.

This gives a numeric + visual reflection of the Qur'anic semantic balance.

## 2.6. Expected Outputs (Level 1)

Root-centric artifacts:

 Per-root extracted verse tables (auditable examples with `sura`, `ayah`, `position`).
 Per-root cluster reports (usage families + representative verses).
 Root-to-root similarity tables (neighbors, distances).
 Candidate oppositional-pair reports (metrics + 2D plots).

---

# 3. Level 2 - Arabic Language Genome (Biconsonantal Level)

## 3.1. Goal

Level 2 builds the Arabic-side "genome": a large, versioned root/lexeme registry with definitions and patterns that can feed Level 3 scoring.
It formalizes the `root3 -> root2` mapping so it can be audited and improved over time.

Move from Qur'an-only and triliteral roots to a much larger view

 Entire Arabic lexicon (classical, mainly).
 Focus on

   2-letter deep roots (your theoretical nuclei),
   and how 3-letter and 4-letter roots grow from them.

At this level, we're less about specific Qur'anic verses and more about

 How does Arabic as a system generate words from core consonantal nuclei

We want to be able to

 For each 2-letter root (e.g. ر ج ، ر ح ، ك ت ، ض ر …)

   Find which 3-letter roots share it (رجم، رجع، رحم، رحب، كتب، كتم… إلخ).
   Study the family of words in big lexica for each root.
   Extract shared semantic “axes” (core meanings).

## 3.2. Data Sources

Here we shift to large lexicons and root-derivative lists:

1. Arabic Roots and Derivatives (Taj al-‘Arūs DB)

    Gives root -> large set of derivatives (vocalized/unvocalized).
    Over 10,000 roots; 142k records.
    Under CC BY-SA license, typically as MySQL dump.

2. Ten Dictionaries for Arabic Language - Roots & Derivations dataset

    Aggregates data from 10 classical dictionaries.
    Includes

      root,
      derived words,
      definitions and morphological pattern info,
      big word-root corpus (~720k pairs + prefixes/suffixes/patterns).

3. arabic-roots (Hugging Face dataset)

    A neat table of

      Arabic root,
      Description/definition,
      Source lexicon.

These can be unified into

 `root_lexicon.csv` 

   `root_triliteral`, `lexeme`, `pattern`, `dictionary_source`, definition snippet, ...
 Later, we will introduce

   `root2` (biconsonantal base),
   mapping from `root_triliteral` -> `root2`.

## 3.3. Introducing the Biconsonantal Layer

Key requirement: the `root3 -> root2` mapping must be explicit, versioned, and traceable (no hidden heuristics inside downstream scoring).

Your core idea:
Each triliteral root is a "construction" from a 2-letter root.

System-wise, we will:

1. Define a function or mapping

    For each 3-letter root (e.g. ر ج م)

      assign a 2-letter core (e.g. ر ج).
    This can start heuristic (first two consonants, or hand-edited mapping).
    Later, refine using phonological + semantic constraints and keep a changelog for mapping updates.

2. Add a column to `root_lexicon`

    root2  root3  lexeme  definition  pattern  source 
    -----  -----  ------  ----------  -------  ------ 
    ر ج    رجم    رجم     ...         فَعَلَ   Taj    
    ر ج    رجع    رجع     ...         فَعَلَ   Lisān  
    ر ح    رحم    رحم     ...         فَعَلَ   Taj    
    ر ح    رحب    رحب     ...         ...      ...    

3. Now we can do Level 2 analyses

    For each `root2`

      gather all `root3` and their lexemes.
    Build

      co-occurrence of lexemes across dictionaries,
      embedding of lexeme definitions (using LLM later),
    cluster lexemes by meaning.

The aim

 Find, for each 2-letter root, a central semantic nucleus that explains its derived 3-letter families,
 and see how different 3-letter forms "rotate" that core meaning.

The algorithms will be similar to Level 1 (vectors + clustering), but

 Data = lexicon entries, not Qur'anic verses.
 Context = definitions + derivational families + patterns.

## 3.4. Expected Outputs (Level 2)

Canonical artifacts:

 A unified root/lexeme registry (definitions + patterns + provenance).
 A versioned `root3 -> root2` mapping + coverage metrics.
 Per-`root2` family summaries (clusters, core semantic axes, representative lexemes).

---

# 4. Level 3 - Similarities between Arabic and other languages (Similarity scoring engine)

## 4.1. Goal

Build a reproducible, discovery-first pipeline that can

 Ingest multilingual sources into canonical, machine-readable tables (JSONL) with a shared minimal schema.
 Compare Arabic lexemes (and their root/lemma metadata) against other languages using multiple similarity views.
 Use tracked concepts + lemma anchors as a shared semantic index (to keep comparisons interpretable and auditable).
 Produce ranked candidates for human review, with separate component scores:

   `orthography_score`  shape/spelling echoes (including consonant skeleton views)
   `sound_score`        IPA/phonetic similarity
   `combined_score`     configurable blend for ranking

LV3 is high-throughput and recall-oriented by design: it should surface candidates, then let humans and stricter rules filter them.
It does not attempt to prove historical directionality; that belongs to Level 4.

## 4.2. Data Sources (typical)

 Arabic morphology/lexica (Qur'anic morphology, roots tables, word-root mappings).
 Multilingual dictionaries (e.g., Wiktionary-derived exports / StarDict conversions).
 IPA backbones and transliteration layers where available.
 Concept registry + anchor tables (tracked reference assets).

## 4.3. Expected Outputs

 Canonical processed tables (for matching): `data/processed/...`
 Ranked lead lists (top candidates per concept, with component scores + provenance)
 QA/KPI reports (coverage, missing IPA/POS rates, duplicates, etc.)
 Run manifests (what ran, inputs used, row counts) to keep results reproducible

---

# 5. Level 4 - Cross-Linguistic Root Mapping (Hypothesis testing)

## 5.1. Goal

Generalize and test the Level 2 hypothesis

 The 2-letter Arabic root system is a deep structural substrate that relates to other languages (ancient and modern).

Level 4 takes the ranked candidates discovered in Level 3 and applies stricter constraints:

 Phonological correspondence rules (explicit, testable mappings).
 Semantic constraints (concept-level consistency, not just string similarity).
 Provenance + negative evidence (we record failures, not only successes).

We want to

 Map Arabic 2-letter roots to potential cognates  echoes in

   Other Semitic languages,
   “Indo-European” families (according to your hypothesis),
   Possibly further.

We will treat Arabic 2-letter roots as

 “base codes” that might have

   phonological transformations,
   semantic drifts,
   orthographic echoes in other languages.

## 5.2. Data Sources

At Level 4, we need

 Multilingual etymological databases,
 Corpora with root-like information in other Semitic languages,
 Phonological correspondence tables (e.g. common consonant shifts).

This is further down the roadmap, but conceptually

 For each Arabic `root2`

   Use phonological mapping rules (e.g. ج ↔ g  k  y in other languages),
   search candidate cognates,
   compare meanings (from dictionaries),
   cluster and test the hypothesis under explicit constraints (and record failures as well as successes).

The tools may look similar (tables, embeddings, clustering), but the standards are stricter: Level 4 is where we move from discovery to hypothesis testing.

---

# 6. Shared Technical Stack and Principles

Regardless of level, the system relies on

## 6.1. Programming and Tools

 Language Python.
 Core libraries

   `pandas` – tables, CSV manipulations.
   `numpy` – numerical operations.
   `scikit-learn` – vectorization, clustering (KMeans, DBSCAN, etc.), PCA.
   `matplotlib`  `plotly` – plotting.
 Optionally later

   `transformers` – if we use contextual embeddings or LLMs for definitions.
   `umap-learn` – for better manifold projections.

## 6.2. Representation

 At Level 1

   Verses → vectors (bag-of-words, or bag-of-roots).
   Roots → centroids of verse vectors.
 At Level 2

   Lexemes → vectors (from definitions + pattern features).
   Roots → centroids over derivative lexemes.
   Root2 → centroids over Root3 families.
 At Level 3

   Cross-lingual words → embeddings from multilingual models or aligned spaces.

## 6.3. Bias Control

Especially for Level 1

 No tafsīr or human commentary is fed into the core numeric pipeline.
 Only Qur’anic text and morphological info (root, pos) are used in Level 1 computations.
 External lexica are used in Level 23 as lexical evidence, but

   You (the human) remain the ultimate interpreter of meaning,
   The system provides patterns, not theology.

---

# 7. Short Summary to the "Learning Machine"

You (the machine) are being asked to help with a four-phase research program

1. Phase 1 – Qur’anic semantic map (triliteral)

    Input

      Qur’an text + full root analysis for every word (from Quranic Arabic Corpus).
    Task

      Build vector representations of verses and roots,
      Cluster usages for each root,
      Compute distances and oppositions between roots (especially known Qur’anic oppositional pairs).
    Constraint

      No external tafsīr; rely only on Qur’anic distribution and root tags.

2. Phase 2 - Arabic genome (biconsonantal)

    Input

      Large lexical root–derivative datasets from classical dictionaries.
    Task

      Introduce a 2-letter root layer,
      Group triliteral roots under 2-letter nuclei,
      Extract central semantic cores for each 2-letter root via clustering over definitions and derivations.
      Export a graph view (nodes/edges) for visual exploration and later GraphRAG-style augmentation.

## Implementation note (local folders)

- LV2 workspace: `C:\AI Projects\Arabic-s-Words-decoding-LV2\`
  - Goal: build processed Arabic tables that maximize word/lemma coverage with known roots and derive a `binary_root` key for regrouping.

3. Phase 3 - Similarity scoring & ranked candidate discovery (LV3)

    Input

      Arabic lexeme/root layers from Phase 1-2,
      Multilingual dictionaries + IPA/transliteration resources,
      Tracked concept registry + lemma anchors.
    Task

      Build canonical processed tables (shared schema) from multilingual sources,
      Generate ranked cross-language similarity candidates across multiple views (orthography + sound),
      Produce leads + QA/KPI reports and keep runs reproducible (manifests).

4. Phase 4 - Cross-linguistic root mapping & hypothesis testing (LV4)

    Input

      Arabic root2 system from Phase 2,
      Multilingual etymological and lexical data.
    Task

      Find phonological and semantic echoes of Arabic root2 units in other languages,
      Test mappings under explicit correspondence rules and semantic constraints (and record failures),
      Explore whether cross-linguistic patterns can be explained through the Arabic bi-root system.

At every stage, your main operations are

 Select the relevant data (verses  words  roots  definitions).
 Encode them as vectors (using basic or advanced encoders).
 Cluster  compare them (to discover structure proximity, opposition, families).
 Expose the patterns back to the human analyst, who then interprets them conceptually and spiritually.

This is the roadmap. From here, we can refine each phase into concrete scripts, schemas, and experiments one by one.
