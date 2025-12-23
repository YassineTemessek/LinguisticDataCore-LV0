from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class AdapterResult:
    output_path: Path
    manifest_path: Path
    rows_written: int


class BaseAdapter(Protocol):
    """
    Adapter contract: turn raw sources into LV0.7 JSONL + manifest.
    Implementations should be deterministic and avoid hidden order dependence.
    """

    def run(self, *, input_dir: Path, output_path: Path, manifest_path: Path) -> AdapterResult:
        ...

