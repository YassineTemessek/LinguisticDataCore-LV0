"""
Adapter registry scaffolding for LV0.7 ingestion.

Each adapter exposes a `run(input_dir: Path, output_path: Path, manifest_path: Path, **kwargs)`
that writes LV0.7 JSONL rows and a manifest. Adapters must:
 - produce deterministic IDs (see docs/SCHEMA_LV0_7.md)
 - preserve required fields (`id, lemma, language, stage, script, source, lemma_status`)
 - avoid hidden reliance on row order (manifest includes hash and row_count)
"""

from .base import AdapterResult, BaseAdapter  # noqa: F401
from .quran_lemmas import QuranLemmasAdapter  # noqa: F401
from .english_ipa import EnglishIPAAdapter  # noqa: F401
from .wiktionary_filtered import WiktionaryFilteredAdapter  # noqa: F401
from .concepts import ConceptsAdapter  # noqa: F401

