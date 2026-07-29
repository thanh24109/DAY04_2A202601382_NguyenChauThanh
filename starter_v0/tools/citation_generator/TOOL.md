---
name: citation_generator
track: core
kind: local_formatter
requires_env: []
inputs: [title, authors, year, venue, url, style]
outputs: [apa, ieee, bibtex, requested_style]
side_effect: false
---
# citation_generator

Formats bibliographic metadata already supplied by the user or returned by
another tool as APA, IEEE, BibTeX, or all three. It does not search for missing
paper metadata and does not verify bibliographic facts.
