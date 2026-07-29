from __future__ import annotations

import re
import unicodedata
from typing import Any


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def _author_list(authors: str) -> list[str]:
    normalized = re.sub(r"\s+(?:and|&)\s+", ";", _clean(authors), flags=re.IGNORECASE)
    return [author.strip() for author in normalized.split(";") if author.strip()]


def _bibtex_key(authors: list[str], year: str, title: str) -> str:
    first_author = authors[0] if authors else "unknown"
    surname = first_author.split(",")[0] if "," in first_author else first_author.split()[-1]
    first_title_word = next(iter(re.findall(r"[A-Za-z0-9]+", title)), "work")
    raw = f"{surname}{year or 'nd'}{first_title_word}"
    folded = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Za-z0-9_-]", "", folded) or "citation"


def _bibtex_escape(value: str) -> str:
    return value.replace("\\", "\\textbackslash{}").replace("{", "\\{").replace("}", "\\}")


def citation_generator(
    title: str = "",
    authors: str = "",
    year: str | int = "",
    venue: str = "",
    url: str = "",
    style: str = "all",
) -> dict[str, Any]:
    title = _clean(title)
    author_text = _clean(authors)
    year_text = _clean(year)
    venue = _clean(venue)
    url = _clean(url)
    style = _clean(style).lower() or "all"

    missing_fields = [
        field
        for field, value in (("title", title), ("authors", author_text), ("year", year_text))
        if not value
    ]
    if missing_fields:
        return {
            "tool": "citation_generator",
            "error": "missing_metadata",
            "missing_fields": missing_fields,
            "message": "Provide title, authors, and year before generating a citation.",
        }
    if style not in {"apa", "ieee", "bibtex", "all"}:
        return {
            "tool": "citation_generator",
            "error": "invalid_style",
            "message": "style must be one of: apa, ieee, bibtex, all",
        }

    author_items = _author_list(author_text)
    apa_authors = ", ".join(author_items) if author_items else author_text
    apa = f"{apa_authors} ({year_text}). {title}."
    if venue:
        apa += f" {venue}."
    if url:
        apa += f" {url}"

    ieee_authors = ", ".join(author_items) if author_items else author_text
    ieee = f'{ieee_authors}, "{title},"'
    if venue:
        ieee += f" {venue},"
    ieee += f" {year_text}."
    if url:
        ieee += f" [Online]. Available: {url}"

    key = _bibtex_key(author_items, year_text, title)
    bibtex_fields = [
        f"  title = {{{_bibtex_escape(title)}}}",
        f"  author = {{{_bibtex_escape(' and '.join(author_items) or author_text)}}}",
        f"  year = {{{_bibtex_escape(year_text)}}}",
    ]
    if venue:
        bibtex_fields.append(f"  booktitle = {{{_bibtex_escape(venue)}}}")
    if url:
        bibtex_fields.append(f"  url = {{{_bibtex_escape(url)}}}")
    bibtex = "@misc{" + key + ",\n" + ",\n".join(bibtex_fields) + "\n}"

    citations = {"apa": apa, "ieee": ieee, "bibtex": bibtex}
    requested = citations if style == "all" else {style: citations[style]}
    return {
        "tool": "citation_generator",
        "requested_style": style,
        **requested,
    }
