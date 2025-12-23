from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple


@dataclass(frozen=True)
class TextFieldSpec:
    form_text: str | None
    meaning_text: str | None
    meaning_fallback: bool = False


def build_form_text(*, language: str, lemma: str, translit: str | None = None, ipa: str | None = None) -> str:
    """
    Deterministic form_text builder (scaffold).
    Arabic: include script + translit; others: lemma plus IPA if present.
    """
    lang = (language or "").lower()
    parts: list[str] = []
    if lemma:
        if lang.startswith("ar"):
            parts.append(f"AR: {lemma}")
        else:
            parts.append(lemma)
    if translit:
        parts.append(f"TR: {translit}")
    if ipa:
        parts.append(f"IPA: {ipa}")
    return " | ".join(parts).strip()


def build_meaning_text(gloss_plain: str | None, lemma: str | None = None, fallback_definition: str | None = None) -> Tuple[str | None, bool]:
    """
    Deterministic meaning_text builder (scaffold).
    - Prefer gloss_plain.
    - If missing but fallback_definition exists, use "<lemma> — <fallback_definition>" and flag meaning_fallback=True.
    - Otherwise return (None, False).
    """
    if gloss_plain and gloss_plain.strip():
        return gloss_plain.strip(), False
    if fallback_definition and fallback_definition.strip():
        base = (lemma or "").strip()
        if base:
            return f"{base} — {fallback_definition.strip()}", True
        return fallback_definition.strip(), True
    return None, False


def iter_text_fields(rows: Iterable[dict]) -> Iterable[dict]:
    """
    Given iterable of LV0 rows, yield rows with form_text / meaning_text populated when possible.
    This is a placeholder; final implementation should read from JSONL and write back deterministically.
    """
    for rec in rows:
        lang = rec.get("language", "")
        lemma = rec.get("lemma", "")
        translit = rec.get("translit") or None
        ipa = rec.get("ipa") or rec.get("ipa_raw") or None
        gloss = rec.get("gloss_plain") or rec.get("definition")
        form = build_form_text(language=lang, lemma=lemma, translit=translit, ipa=ipa)
        meaning, fallback = build_meaning_text(gloss_plain=gloss, lemma=lemma)
        rec = dict(rec)
        rec["form_text"] = form
        if meaning:
            rec["meaning_text"] = meaning
            rec["meaning_fallback"] = fallback
        yield rec


def main() -> None:
    raise SystemExit(
        "This scaffold builds deterministic form_text/meaning_text in-memory. "
        "Integrate with JSONL reader/writer before use."
    )


if __name__ == "__main__":
    main()
