from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Step:
    name: str
    tags: frozenset[str]
    cmd: list[str]
    required_all_inputs: tuple[Path, ...] = ()
    required_any_inputs: tuple[Path, ...] = ()
    outputs: tuple[Path, ...] = ()


def _iter_requested(items: Iterable[str]) -> set[str]:
    out: set[str] = set()
    for item in items:
        for part in str(item).split(","):
            part = part.strip()
            if part:
                out.add(part)
    return out


def _exists_any(paths: Iterable[Path]) -> bool:
    for p in paths:
        if p.exists():
            return True
    return False


def _file_stats(path: Path) -> dict[str, Any]:
    try:
        st = path.stat()
    except FileNotFoundError:
        return {"path": str(path), "exists": False}
    return {"path": str(path), "exists": True, "bytes": st.st_size}


def _git_commit(repo_root: Path) -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(repo_root), text=True).strip()
        return out or None
    except Exception:
        return None


def build_steps(*, python_exe: str, repo_root: Path, resources_dir: Path | None) -> list[Step]:
    scripts_dir = repo_root / "scripts" / "ingest"
    data_raw = repo_root / "data" / "raw"
    data_processed = repo_root / "data" / "processed"
    resources_root = resources_dir if resources_dir is not None else data_raw

    arabic_out = data_processed / "arabic" / "classical"
    arabic_out_intermediate = data_processed / "_intermediate" / "arabic"

    return [
        Step(
            name="wiktionary:convert_stardict",
            tags=frozenset({"wiktionary", "stardict"}),
            cmd=[
                python_exe,
                str(scripts_dir / "convert_stardict.py"),
                "--root",
                str(data_raw / "wiktionary_extracted"),
                "--out",
                str(data_processed / "wiktionary_stardict" / "raw"),
            ],
            required_all_inputs=(data_raw / "wiktionary_extracted",),
            outputs=(data_processed / "wiktionary_stardict" / "raw",),
        ),
        Step(
            name="arabic:ingest_word_root_map",
            tags=frozenset({"arabic"}),
            cmd=[
                python_exe,
                str(scripts_dir / "ingest_arabic_word_root_map.py"),
                "--input",
                str(resources_root / "arabic" / "word_root_map.csv" if resources_dir is None else (resources_root / "word_root_map.csv")),
                "--output",
                str(arabic_out_intermediate / "word_root_map.jsonl"),
            ],
            required_all_inputs=(
                (resources_root / "arabic" / "word_root_map.csv") if resources_dir is None else (resources_root / "word_root_map.csv"),
            ),
            outputs=(arabic_out_intermediate / "word_root_map.jsonl",),
        ),
        Step(
            name="arabic:clean_word_root_map",
            tags=frozenset({"arabic"}),
            cmd=[
                python_exe,
                str(scripts_dir / "clean_word_root_map.py"),
                "--input",
                str(arabic_out_intermediate / "word_root_map.jsonl"),
                "--output",
                str(arabic_out / "word_root_map_filtered.jsonl"),
            ],
            required_all_inputs=(arabic_out_intermediate / "word_root_map.jsonl",),
            outputs=(arabic_out / "word_root_map_filtered.jsonl",),
        ),
        Step(
            name="arabic:ingest_quran_morphology",
            tags=frozenset({"arabic"}),
            cmd=[
                python_exe,
                str(scripts_dir / "ingest_quran_morphology.py"),
                "--input",
                str(data_raw / "arabic" / "quran-morphology" / "quran-morphology.txt"),
                "--output",
                str(arabic_out_intermediate / "quran_lemmas.jsonl"),
            ],
            required_all_inputs=(data_raw / "arabic" / "quran-morphology" / "quran-morphology.txt",),
            outputs=(arabic_out_intermediate / "quran_lemmas.jsonl",),
        ),
        Step(
            name="arabic:ingest_hf_roots",
            tags=frozenset({"arabic"}),
            cmd=[
                python_exe,
                str(scripts_dir / "ingest_arabic_hf_roots.py"),
                "--input",
                str(
                    (resources_root / "arabic" / "arabic_roots_hf" / "train-00000-of-00001.parquet")
                    if resources_dir is None
                    else (resources_root / "arabic_roots_hf" / "train-00000-of-00001.parquet")
                ),
                "--output",
                str(arabic_out / "hf_roots.jsonl"),
            ],
            required_all_inputs=(
                (resources_root / "arabic" / "arabic_roots_hf" / "train-00000-of-00001.parquet")
                if resources_dir is None
                else (resources_root / "arabic_roots_hf" / "train-00000-of-00001.parquet"),
            ),
            outputs=(arabic_out / "hf_roots.jsonl",),
        ),
        Step(
            name="arabic:enrich_quran_translit",
            tags=frozenset({"arabic"}),
            cmd=[
                python_exe,
                str(scripts_dir / "enrich_quran_translit.py"),
                "--input",
                str(arabic_out_intermediate / "quran_lemmas.jsonl"),
                "--output",
                str(arabic_out / "quran_lemmas_enriched.jsonl"),
            ],
            required_all_inputs=(arabic_out_intermediate / "quran_lemmas.jsonl",),
            outputs=(arabic_out / "quran_lemmas_enriched.jsonl",),
        ),
        Step(
            name="arabic:build_binary_root_lexicon",
            tags=frozenset({"arabic"}),
            cmd=[
                python_exe,
                str(scripts_dir / "build_arabic_binary_root_lexicon.py"),
                "--word-root-map",
                str(arabic_out / "word_root_map_filtered.jsonl"),
                "--quran-lemmas",
                str(arabic_out / "quran_lemmas_enriched.jsonl"),
                "--output",
                str(arabic_out / "arabic_words_binary_roots.jsonl"),
            ],
            required_any_inputs=(
                arabic_out / "word_root_map_filtered.jsonl",
                arabic_out / "quran_lemmas_enriched.jsonl",
            ),
            outputs=(arabic_out / "arabic_words_binary_roots.jsonl",),
        ),
        Step(
            name="arabic:merge_classical_lexemes",
            tags=frozenset({"arabic"}),
            cmd=[
                python_exe,
                str(scripts_dir / "merge_arabic_classical_lexemes.py"),
                "--quran",
                str(arabic_out / "quran_lemmas_enriched.jsonl"),
                "--word-root-map",
                str(arabic_out / "word_root_map_filtered.jsonl"),
                "--hf-roots",
                str(arabic_out / "hf_roots.jsonl"),
                "--binary-root-lexicon",
                str(arabic_out / "arabic_words_binary_roots.jsonl"),
                "--output",
                str(arabic_out / "lexemes.jsonl"),
            ],
            required_any_inputs=(
                arabic_out / "quran_lemmas_enriched.jsonl",
                arabic_out / "word_root_map_filtered.jsonl",
                arabic_out / "hf_roots.jsonl",
                arabic_out / "arabic_words_binary_roots.jsonl",
            ),
            outputs=(arabic_out / "lexemes.jsonl",),
        ),
    ]


def run_ingest(
    *,
    repo_root: Path,
    tags: set[str],
    all_steps: bool,
    resources_dir: Path | None,
    require_inputs: bool,
    fail_fast: bool,
    skip_missing_inputs: bool,
    write_manifest: bool,
) -> int:
    python_exe = sys.executable
    steps = build_steps(python_exe=python_exe, repo_root=repo_root, resources_dir=resources_dir)

    requested = set(tags)
    if all_steps:
        requested = set()

    env = os.environ.copy()
    if resources_dir is not None:
        env["LC_RESOURCES_DIR"] = str(resources_dir)

    manifest: dict[str, Any] = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(repo_root),
        "requested_tags": sorted(requested),
        "steps": [],
        "outputs": [],
    }

    any_failed = False
    for step in steps:
        if requested and not (set(step.tags) & requested):
            continue

        missing_all = [p for p in step.required_all_inputs if not p.exists()]
        missing_any = step.required_any_inputs and not _exists_any(step.required_any_inputs)
        missing = bool(missing_all) or bool(missing_any)

        if missing:
            if require_inputs and not skip_missing_inputs:
                any_failed = True
                manifest["steps"].append({"name": step.name, "status": "skipped_missing_inputs", "cmd": step.cmd})
                if fail_fast:
                    break
                continue
            if skip_missing_inputs:
                manifest["steps"].append({"name": step.name, "status": "skipped_missing_inputs", "cmd": step.cmd})
                continue

        start = time.time()
        proc = subprocess.run(step.cmd, cwd=str(repo_root), env=env, check=False)
        dur_s = round(time.time() - start, 3)
        status = "ok" if proc.returncode == 0 else "failed"
        manifest["steps"].append(
            {"name": step.name, "status": status, "returncode": proc.returncode, "duration_s": dur_s, "cmd": step.cmd}
        )
        if proc.returncode != 0:
            any_failed = True
            if fail_fast:
                break

    for out_path in [repo_root / "data" / "processed"]:
        manifest["outputs"].append(_file_stats(out_path))

    if write_manifest:
        out_dir = repo_root / "outputs" / "manifests"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_path = out_dir / f"ingest_run_{ts}.json"
        out_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return 2 if any_failed else 0
