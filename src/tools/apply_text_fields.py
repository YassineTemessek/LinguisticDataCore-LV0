from __future__ import annotations

import argparse
import json
from pathlib import Path

from features.build_text_fields import iter_text_fields


def main() -> None:
    ap = argparse.ArgumentParser(description="Add form_text / meaning_text to a JSONL (writes new file).")
    ap.add_argument("input", type=Path, help="Input JSONL (LV0 rows).")
    ap.add_argument("output", type=Path, help="Output JSONL (enriched).")
    args = ap.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with args.output.open("w", encoding="utf-8") as out_f:
        for rec in iter_text_fields(_iter_jsonl(args.input)):
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1
    print(f"Wrote {count} rows to {args.output}")


def _iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


if __name__ == "__main__":
    main()
