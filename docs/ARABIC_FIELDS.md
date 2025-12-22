# Arabic Fields (LV0)

This document defines the LV0 canonical fields used for Arabic lexeme rows and downstream consumers (LV2/LV3).

## Core fields

- `lemma` (string, required): the surface form as provided by the source.
- `language` (string, required): `ara` / `ara-qur` / etc.
  - Quranic Arabic (`ara-qur`) is treated as an independent language (limited to Quran vocabulary), and its processed outputs live under `data/processed/quranic_arabic/`.
- `stage` (folder/file level): stage is represented by dataset boundaries (folder/file naming), not required in each row.
- `script` (optional): can be omitted; downstream can infer when needed.
- `source` (string, required): dataset/source identifier.
- `id` (string, required): stable row id.
- `translit` (string, required): transliteration (can equal `lemma` when no romanization is needed).
- `ipa` (string, required): IPA string (can be empty when unknown).

## Root-derived fields

These fields exist when the row has a known (widely accepted) Arabic root.

- `root` (string): the accepted root as provided by the source (commonly 3 letters, sometimes 4).
- `root_norm` (string): a lightly normalized form of `root` used for stable downstream logic.
  - Removes Arabic diacritics and tatweel.
  - Normalizes common variants (e.g., `أ/إ/آ/ٱ → ا`, `ى → ي`, `ة → ه`, `ؤ → و`, `ئ → ي`).
- `binary_root` (string): **first 2 letters** of `root_norm`.
  - Example: `كتب` → `كت`
  - If `root_norm` has fewer than 2 characters, `binary_root` is omitted/empty.
- `binary_root_method` (string): currently `first2` (or `missing` when not derivable).

## Notes

- LV0 treats `stage` as free text, but once a label is used in published outputs it should remain stable.
- LV0 does not attempt deeper linguistic reinterpretations in the canonical layer; it keeps derivations simple and reproducible.
