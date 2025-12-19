from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

DEFAULT_OWNER = "YassineTemessek"
DEFAULT_REPO = "LinguisticDataCore-LV0"


def _get_json(url: str) -> dict:
    req = Request(url, headers={"Accept": "application/vnd.github+json"})
    with urlopen(req, timeout=60) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


def _download(url: str, dest_path: Path) -> None:
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"Accept": "application/octet-stream"})
    with urlopen(req, timeout=180) as resp:  # noqa: S310
        with dest_path.open("wb") as fh:
            shutil.copyfileobj(resp, fh)


def fetch_release(*, repo_root: Path, release: str, dest: Path) -> None:
    """
    Fetch and extract LV0 per-language zip assets from GitHub Releases.

    Extraction target is `dest` (usually a consuming repo root), creating `data/processed/...` etc.
    """
    owner = DEFAULT_OWNER
    repo = DEFAULT_REPO

    if release == "latest":
        rel = _get_json(f"https://api.github.com/repos/{owner}/{repo}/releases/latest")
    else:
        rel = _get_json(f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{release}")

    assets = rel.get("assets") or []
    if not assets:
        raise RuntimeError(f"No release assets found for {owner}/{repo} release={release!r}.")

    dest = dest.resolve()
    downloaded: list[Path] = []
    for asset in assets:
        name = asset.get("name") or ""
        if not name.endswith(".zip"):
            continue
        url = asset.get("browser_download_url")
        if not url:
            continue
        out_path = repo_root / "outputs" / "downloads" / name
        _download(str(url), out_path)
        downloaded.append(out_path)

    if not downloaded:
        raise RuntimeError(f"No .zip assets found for {owner}/{repo} release={release!r}.")

    for zip_path in downloaded:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(dest)
