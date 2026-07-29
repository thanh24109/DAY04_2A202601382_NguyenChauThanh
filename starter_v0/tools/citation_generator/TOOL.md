---
name: citation_generator
track: core
kind: local_formatter
provider: none
requires_env: []
inputs: [title, authors, year, journal, url, style]
outputs: [apa, bibtex, vancouver]
side_effect: false
---

# citation_generator

Generates formatted citations from paper metadata. Supports APA, BibTeX, and Vancouver styles.

Use when the user asks for a citation, reference, or bibliography entry for a paper. Requires at minimum a title and authors. If year or journal are missing, the tool will still generate a partial citation.

Do NOT use this for searching papers — use `papers` for that. Call this only after the user explicitly requests a citation format.
