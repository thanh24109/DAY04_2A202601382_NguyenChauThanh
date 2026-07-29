from __future__ import annotations

import re
from typing import Any


def _clean(text: str) -> str:
    """Strip extra whitespace and normalize."""
    return " ".join(str(text).strip().split())


def _parse_authors(authors: Any) -> list[str]:
    """Accept authors as list or comma-separated string."""
    if isinstance(authors, list):
        return [_clean(a) for a in authors if a]
    raw = str(authors or "")
    # Split on semicolons or "and" keyword first, then fall back to commas
    if ";" in raw:
        parts = raw.split(";")
    elif " and " in raw.lower():
        parts = re.split(r"\s+and\s+", raw, flags=re.IGNORECASE)
    else:
        parts = raw.split(",")
        # If every part looks like a name fragment, rejoin pairs (Last, First)
        # Heuristic: if there are an even number of short fragments, pair them
        if len(parts) > 2 and all(len(p.strip()) < 25 for p in parts):
            paired: list[str] = []
            i = 0
            while i < len(parts):
                # Detect "Last, First" pattern: next chunk has no comma and is short
                if i + 1 < len(parts) and re.match(r"^\s*[A-Z]", parts[i + 1]):
                    paired.append(f"{parts[i].strip()}, {parts[i+1].strip()}")
                    i += 2
                else:
                    paired.append(parts[i].strip())
                    i += 1
            return [p for p in paired if p]
    return [_clean(p) for p in parts if p.strip()]


def _apa_author_list(authors: list[str]) -> str:
    """Format author list for APA: Last, F. M., & Last, F. M."""
    formatted: list[str] = []
    for author in authors:
        parts = author.strip().split(",")
        if len(parts) >= 2:
            last = parts[0].strip()
            first_parts = parts[1].strip().split()
            initials = ". ".join(p[0].upper() for p in first_parts if p) + "."
            formatted.append(f"{last}, {initials}")
        else:
            # Try "First Last" format
            words = author.strip().split()
            if len(words) >= 2:
                last = words[-1]
                initials = ". ".join(w[0].upper() for w in words[:-1] if w) + "."
                formatted.append(f"{last}, {initials}")
            else:
                formatted.append(author.strip())

    if not formatted:
        return "Unknown Author"
    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) <= 20:
        return ", ".join(formatted[:-1]) + ", & " + formatted[-1]
    # 21+ authors: list first 19, ellipsis, last author
    return ", ".join(formatted[:19]) + ", ... " + formatted[-1]


def _bibtex_key(authors: list[str], year: str, title: str) -> str:
    """Generate a short BibTeX cite key: LastnameYEAR_firstword."""
    last = "Unknown"
    if authors:
        first_author = authors[0].split(",")[0].strip()
        last = re.sub(r"[^A-Za-z]", "", first_author.split()[-1] if first_author.split() else "Unknown")
    first_word = re.sub(r"[^A-Za-z]", "", (title or "").split()[0]) if title else "paper"
    return f"{last}{year}_{first_word.lower()}"


def _build_url(url: str, arxiv_id: str) -> str:
    if url:
        return url.strip()
    if arxiv_id:
        return f"https://arxiv.org/abs/{arxiv_id.strip()}"
    return ""


def generate_citation(
    title: str = "",
    authors: Any = "",
    year: Any = "",
    venue: str = "arXiv preprint",
    url: str = "",
    arxiv_id: str = "",
) -> dict[str, Any]:
    """
    Generate academic citations in APA, BibTeX, and plain formats.

    Args:
        title:    Full paper title (required).
        authors:  Author names as string or list (required).
        year:     Publication year, e.g. 2017 (required).
        venue:    Journal, conference, or "arXiv preprint" (optional).
        url:      URL to the abstract page (optional).
        arxiv_id: arXiv paper ID like "1706.03762" (optional).

    Returns:
        dict with keys: tool, apa, bibtex, plain, inputs_used
    """
    try:
        title_clean = _clean(title)
        year_str = str(year).strip() if year else "n.d."
        venue_clean = _clean(venue) if venue else "arXiv preprint"
        paper_url = _build_url(url, arxiv_id)
        arxiv_id_clean = arxiv_id.strip() if arxiv_id else ""

        author_list = _parse_authors(authors)
        if not author_list:
            author_list = ["Unknown Author"]
        if not title_clean:
            return {
                "tool": "citation_generator",
                "error": "missing_title",
                "message": "title is required to generate a citation.",
            }

        # ── APA 7th edition ────────────────────────────────────────────────
        apa_authors = _apa_author_list(author_list)
        apa_title = title_clean  # sentence case kept as-is (model can downcase if needed)
        if venue_clean.lower().startswith("arxiv"):
            apa_venue = f"arXiv preprint arXiv:{arxiv_id_clean}" if arxiv_id_clean else "arXiv preprint"
        else:
            apa_venue = f"*{venue_clean}*"
        apa = f"{apa_authors} ({year_str}). {apa_title}. {apa_venue}."
        if paper_url:
            apa += f" {paper_url}"

        # ── BibTeX ──────────────────────────────────────────────────────────
        bib_key = _bibtex_key(author_list, year_str, title_clean)
        bib_author_field = " and ".join(author_list)
        entry_type = "article" if not venue_clean.lower().startswith("arxiv") else "misc"
        bibtex_lines = [
            f"@{entry_type}{{{bib_key},",
            f"  author    = {{{bib_author_field}}},",
            f"  title     = {{{title_clean}}},",
            f"  year      = {{{year_str}}},",
        ]
        if venue_clean.lower().startswith("arxiv"):
            bibtex_lines.append(f"  howpublished = {{arXiv preprint arXiv:{arxiv_id_clean}}},") if arxiv_id_clean else None
        else:
            bibtex_lines.append(f"  journal   = {{{venue_clean}}},")
        if paper_url:
            bibtex_lines.append(f"  url       = {{{paper_url}}},")
        bibtex_lines.append("}")
        bibtex = "\n".join(line for line in bibtex_lines if line is not None)

        # ── Plain text ───────────────────────────────────────────────────────
        short_authors = author_list[0].split(",")[0].strip() if author_list else "Unknown"
        if len(author_list) > 1:
            short_authors += " et al."
        plain = f"{short_authors} ({year_str}). {title_clean}."
        if venue_clean and not venue_clean.lower().startswith("arxiv"):
            plain += f" {venue_clean}."

        return {
            "tool": "citation_generator",
            "apa": apa,
            "bibtex": bibtex,
            "plain": plain,
            "inputs_used": {
                "title": title_clean,
                "authors": author_list,
                "year": year_str,
                "venue": venue_clean,
                "url": paper_url,
                "arxiv_id": arxiv_id_clean,
            },
        }

    except Exception as exc:
        return {
            "tool": "citation_generator",
            "error": type(exc).__name__,
            "message": str(exc),
        }
