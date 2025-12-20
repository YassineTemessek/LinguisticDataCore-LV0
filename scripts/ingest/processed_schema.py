from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Any, Iterable


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_IPA_STRESS_MARKS = str.maketrans({"\u02c8": "", "\u02cc": "", "'": ""})  # ˈ ˌ '

_AR_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670\u0640]")
_AR_ROOT_NORM_MAP = str.maketrans(
    {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
        "ى": "ي",
        "ؤ": "و",
        "ئ": "ي",
        "ة": "ه",
    }
)


def normalize_arabic_root(root: str) -> str:
    root = (root or "").strip()
    if not root:
        return ""
    root = _AR_DIACRITICS_RE.sub("", root)
    root = root.translate(_AR_ROOT_NORM_MAP)
    return root


def derive_binary_root(root: str) -> tuple[str, str]:
    """
    LV0 canonical Arabic binary root: first 2 chars of the normalized root.
    Returns: (binary_root, method)
    """
    root_norm = normalize_arabic_root(root)
    if len(root_norm) >= 2:
        return root_norm[:2], "first2"
    return "", "missing"


def strip_html(text: str) -> str:
    if not text:
        return ""
    text = _HTML_TAG_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text).strip()
    return text


def normalize_ipa(ipa: str) -> str:
    if not ipa:
        return ""
    ipa = ipa.strip()
    if len(ipa) >= 2 and ((ipa[0] == "/" and ipa[-1] == "/") or (ipa[0] == "[" and ipa[-1] == "]")):
        ipa = ipa[1:-1].strip()
    ipa = unicodedata.normalize("NFC", ipa)
    ipa = _WS_RE.sub("", ipa)
    ipa = ipa.translate(_IPA_STRESS_MARKS)
    return ipa


def coerce_pos_list(pos: Any) -> list[str]:
    if pos is None:
        return []
    if isinstance(pos, list):
        out: list[str] = []
        for item in pos:
            if not item:
                continue
            out.append(str(item))
        return out
    if isinstance(pos, str):
        if not pos.strip():
            return []
        return [pos.strip()]
    return [str(pos)]


def stable_id(*fields: Any, prefix: str = "lex") -> str:
    payload = "|".join("" if f is None else str(f) for f in fields)
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]  # noqa: S324
    return f"{prefix}:{digest}"


def ensure_min_schema(
    rec: dict,
    *,
    default_language: str | None = None,
    default_stage: str | None = None,
    default_script: str | None = None,
    default_source: str | None = None,
    default_lemma_status: str | None = None,
) -> dict:
    lemma = str(rec.get("lemma") or "").strip()
    rec["lemma"] = lemma

    rec["language"] = str(rec.get("language") or default_language or "").strip()
    # LV0 schema A: `stage` and `script` are not required row fields anymore.
    # Stage is represented by folder/file boundaries; script can be derived when needed.
    # We keep any provided values, but do not inject defaults.
    if "stage" in rec and rec.get("stage") is not None:
        rec["stage"] = str(rec.get("stage") or "").strip()
    if "script" in rec and rec.get("script") is not None:
        rec["script"] = str(rec.get("script") or "").strip()
    rec["source"] = str(rec.get("source") or default_source or "").strip()
    rec["lemma_status"] = str(rec.get("lemma_status") or default_lemma_status or "").strip()

    # Required (structural) fields for LV0 processed JSONL:
    # - `translit`: always present (can equal lemma for Latin-script languages)
    # - `ipa`: always present (can be empty when unknown)
    if not rec.get("translit"):
        rec["translit"] = lemma

    root = str(rec.get("root") or "").strip()
    if root:
        rec["root"] = root
        if rec["language"].startswith("ara"):
            root_norm = normalize_arabic_root(root)
            if root_norm and not rec.get("root_norm"):
                rec["root_norm"] = root_norm
            if not rec.get("binary_root"):
                binary_root, method = derive_binary_root(root)
                if binary_root:
                    rec["binary_root"] = binary_root
                rec.setdefault("binary_root_method", method)

    if ("ipa" in rec) or ("ipa_raw" in rec):
        ipa_raw = str(rec.get("ipa_raw") or rec.get("ipa") or "")
        rec.setdefault("ipa_raw", ipa_raw)
        rec["ipa"] = normalize_ipa(ipa_raw)
    else:
        rec["ipa_raw"] = ""
        rec["ipa"] = ""

    if "gloss" in rec and "gloss_html" not in rec:
        rec["gloss_html"] = rec.get("gloss", "")
    if "gloss_html" in rec and "gloss_plain" not in rec:
        rec["gloss_plain"] = strip_html(str(rec.get("gloss_html") or ""))

    if "pos" in rec:
        rec["pos"] = coerce_pos_list(rec.get("pos"))

    if not rec.get("id"):
        rec["id"] = stable_id(
            rec.get("language"),
            rec.get("source"),
            rec.get("source_ref"),
            rec.get("lemma"),
            rec.get("orthography"),
            rec.get("root"),
            rec.get("ipa") or rec.get("ipa_raw"),
            rec.get("translit"),
        )

    return rec


def iter_missing_required(rec: dict) -> Iterable[str]:
    for k in ("id", "lemma", "language", "source", "lemma_status"):
        if not rec.get(k):
            yield k
    # `translit` and `ipa` are required *fields* (must exist), but may be empty in early ingestion.
    for k in ("translit", "ipa"):
        if k not in rec:
            yield k
