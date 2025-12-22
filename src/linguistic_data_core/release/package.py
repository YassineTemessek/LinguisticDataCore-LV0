from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class LanguageBundle:
    lang: str
    patterns: tuple[str, ...]


LANGUAGE_BUNDLES: tuple[LanguageBundle, ...] = (
    LanguageBundle(lang="quranic_arabic", patterns=("data/processed/quranic_arabic/**",)),
    LanguageBundle(lang="arabic", patterns=("data/processed/arabic/**", "data/processed/wiktionary_stardict/**Arabic**")),
    LanguageBundle(lang="english", patterns=("data/processed/english/**", "data/processed/_parts/english_*/**")),
    LanguageBundle(lang="greek", patterns=("data/processed/wiktionary_stardict/**Greek**",)),
    LanguageBundle(lang="latin", patterns=("data/processed/wiktionary_stardict/**Latin**",)),
    LanguageBundle(lang="german", patterns=("data/processed/wiktionary_stardict/**German**", "data/processed/german/**")),
    LanguageBundle(lang="hebrew", patterns=("data/processed/wiktionary_stardict/**Hebrew**", "data/processed/hebrew/**")),
    LanguageBundle(lang="syriac", patterns=("data/processed/wiktionary_stardict/**Syriac**", "data/processed/syriac/**")),
    LanguageBundle(lang="akkadian", patterns=("data/processed/wiktionary_stardict/**Akkadian**", "data/processed/akkadian/**")),
    LanguageBundle(lang="concepts", patterns=("resources/concepts/**",)),
    LanguageBundle(lang="anchors", patterns=("resources/anchors/**",)),
    # Optional: include any locally-provided raw sources (not committed by default).
    LanguageBundle(lang="raw_sources", patterns=("data/raw/**",)),
)


def _iter_files(repo_root: Path, patterns: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for pat in patterns:
        for p in repo_root.glob(pat):
            if p.is_file():
                files.append(p)
    # de-dupe
    uniq: dict[str, Path] = {}
    for p in files:
        uniq[str(p)] = p
    return sorted(uniq.values(), key=lambda x: str(x))


def package_language_bundles(*, repo_root: Path, version: str) -> None:
    out_dir = repo_root / "outputs" / "release_assets" / version
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, object] = {
        "version": version,
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "bundles": {},
    }

    for bundle in LANGUAGE_BUNDLES:
        files = _iter_files(repo_root, bundle.patterns)
        zip_path = out_dir / f"{bundle.lang}_{version}.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                rel = f.relative_to(repo_root)
                zf.write(f, arcname=str(rel))
        manifest["bundles"][bundle.lang] = {
            "zip": str(zip_path.name),
            "files": [str(p.relative_to(repo_root)) for p in files],
            "file_count": len(files),
        }

    (out_dir / f"manifest_{version}.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
