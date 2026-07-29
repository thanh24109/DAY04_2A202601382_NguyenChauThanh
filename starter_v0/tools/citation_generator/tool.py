from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence
from typing import Any


def _clean(value: Any) -> str:
    """Convert a metadata value to a compact, single-line string."""
    return " ".join(str(value).split()) if value is not None else ""


def _author_names(authors: str | Sequence[str]) -> list[str]:
    if isinstance(authors, str):
        value = _clean(authors)
        if not value:
            return []
        # Semicolons and the BibTeX `and` separator are unambiguous. Commas are
        # intentionally preserved because they may represent "Family, Given".
        return [name.strip() for name in re.split(r"\s*;\s*|\s+and\s+", value) if name.strip()]
    return [name for item in authors if (name := _clean(item))]


def _apa_authors(names: list[str]) -> str:
    if len(names) < 2:
        return names[0] if names else ""
    if len(names) == 2:
        return f"{names[0]}, & {names[1]}"
    return f"{', '.join(names[:-1])}, & {names[-1]}"


def _with_terminal_punctuation(value: str) -> str:
    return value if value.endswith((".", "!", "?")) else f"{value}."


_BIBTEX_ESCAPES = str.maketrans({
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "%": r"\%",
    "&": r"\&",
    "#": r"\#",
    "_": r"\_",
})


def _bibtex_escape(value: str) -> str:
    return value.translate(_BIBTEX_ESCAPES)


def _citation_key(first_author: str, year: str, title: str) -> str:
    author = first_author.split(",", 1)[0] if "," in first_author else first_author.split()[-1]
    if author.casefold() in {"al.", "al", "et"}:
        author = first_author.split()[0]
    title_words = re.findall(r"[A-Za-z0-9]+", unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode())
    title_word = next((word for word in title_words if word.casefold() not in {"a", "an", "the"}), "paper")
    raw_key = f"{author}{year}{title_word}"
    ascii_key = unicodedata.normalize("NFKD", raw_key).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9_:-]", "", ascii_key) or "paper"


def citation_generator(
    title: str,
    authors: str | Sequence[str],
    year: int | str,
    journal: str = "",
    url: str = "",
) -> dict[str, Any]:
    """Generate APA-style and BibTeX citations without external services."""
    clean_title = _clean(title)
    names = _author_names(authors)
    clean_year = _clean(year)
    clean_journal = _clean(journal)
    clean_url = _clean(url)

    missing = [
        field
        for field, value in (("title", clean_title), ("authors", names), ("year", clean_year))
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required citation metadata: {', '.join(missing)}")

    author_text = _with_terminal_punctuation(_apa_authors(names))
    apa_parts = [f"{author_text} ({clean_year}).", _with_terminal_punctuation(clean_title)]
    if clean_journal:
        apa_parts.append(_with_terminal_punctuation(clean_journal))
    apa = " ".join(apa_parts)
    if clean_url:
        apa += f" {clean_url}"

    key = _citation_key(names[0], clean_year, clean_title)
    fields = [
        ("title", clean_title),
        ("author", " and ".join(names)),
        ("year", clean_year),
    ]
    if clean_journal:
        fields.append(("journal", clean_journal))
    if clean_url:
        fields.append(("url", clean_url))
    bibtex_fields = ",\n".join(
        f"  {name} = {{{_bibtex_escape(value)}}}" for name, value in fields
    )
    bibtex = f"@article{{{key},\n{bibtex_fields}\n}}"

    return {
        "tool": "citation_generator",
        "apa": apa,
        "bibtex": bibtex,
        "citation_key": key,
    }
