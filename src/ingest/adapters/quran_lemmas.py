from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .base import AdapterResult
from ingest.utils import ensure_pos_list, make_stable_id, write_manifest


class QuranLemmasAdapter:
    """
    Stub adapter for Quran lemmas (quranic-corpus-morphology).
    Expected input: data/processed/arabic/quran_lemmas_enriched.jsonl (already built by scripts/ingest).
    Output: LV0.7-aligned JSONL with stable IDs and manifest.
    """

    def run(self, *, input_dir: Path, output_path: Path, manifest_path: Path) -> AdapterResult:
        src_path = input_dir / "data" / "processed" / "arabic" / "quran_lemmas_enriched.jsonl"
        if not src_path.exists():
            raise FileNotFoundError(f"Missing input file: {src_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        seen: Dict[str, int] = {}
        written = 0
        with src_path.open("r", encoding="utf-8", errors="replace") as inp, output_path.open("w", encoding="utf-8") as out:
            for line in inp:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                lang = rec.get("language") or "ara-qur"
                stage = rec.get("stage") or "quranic"
                script = rec.get("script") or "Arab"
                source = rec.get("source") or "quranic-corpus-morphology"
                lemma_status = rec.get("lemma_status") or "attested"
                pos_list = ensure_pos_list(rec.get("pos"))

                # ID handling
                cur_id = rec.get("id") or ""
                if not cur_id:
                    base_disambig = seen.get(cur_id, 0)
                    while True:
                        candidate = make_stable_id(lang, stage, source, rec.get("lemma", ""), pos_list, base_disambig)
                        if candidate not in seen:
                            cur_id = candidate
                            seen[candidate] = 1
                            break
                        base_disambig += 1
                else:
                    seen[cur_id] = seen.get(cur_id, 0) + 1

                rec["id"] = cur_id
                rec["language"] = lang
                rec["stage"] = stage
                rec["script"] = script
                rec["source"] = source
                rec["lemma_status"] = lemma_status
                rec["pos"] = pos_list

                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                written += 1

        write_manifest(
            target=output_path,
            manifest_path=manifest_path,
            schema_version="lv0.7",
            generated_by="QuranLemmasAdapter",
            id_policy="lang:stage:source:normalized_lemma:pos:+disambig",
        )
        return AdapterResult(output_path=output_path, manifest_path=manifest_path, rows_written=written)
