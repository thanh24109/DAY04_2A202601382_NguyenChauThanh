from __future__ import annotations

from typing import Any


def citation_generator(
    title: str = "",
    authors: str = "",
    year: str = "",
    journal: str = "",
    url: str = "",
    style: str = "apa",
) -> dict[str, Any]:
    title = str(title).strip() or "Untitled"
    authors = str(authors).strip() or "Unknown"
    year = str(year).strip() or "n.d."
    journal = str(journal).strip() or ""
    url = str(url).strip() or ""

    apa = _format_apa(title, authors, year, journal, url)
    bibtex = _format_bibtex(title, authors, year, journal, url)
    vancouver = _format_vancouver(title, authors, year, journal, url)

    return {
        "tool": "citation_generator",
        "title": title,
        "authors": authors,
        "year": year,
        "journal": journal,
        "style": style,
        "apa": apa,
        "bibtex": bibtex,
        "vancouver": vancouver,
    }


def _format_apa(title: str, authors: str, year: str, journal: str, url: str) -> str:
    journal_part = f"*{journal}*" if journal else ""
    url_part = f" {url}" if url else ""
    return f"{authors} ({year}). {title}. {journal_part}.{url_part}"


def _format_bibtex(title: str, authors: str, year: str, journal: str, url: str) -> str:
    key = title.split()[0].lower() if title.split() else "ref"
    lines = [
        f"@article{{{key},",
        f"  title = {{{title}}},",
        f"  author = {{{authors}}},",
        f"  year = {{{year}}},",
    ]
    if journal:
        lines.append(f"  journal = {{{journal}}},")
    if url:
        lines.append(f"  url = {{{url}}},")
    lines.append("}")
    return "\n".join(lines)


def _format_vancouver(title: str, authors: str, year: str, journal: str, url: str) -> str:
    journal_part = f" {journal}" if journal else ""
    url_part = f". Available from: {url}" if url else ""
    return f"{authors}. {title}.{journal_part}. {year}.{url_part}"
