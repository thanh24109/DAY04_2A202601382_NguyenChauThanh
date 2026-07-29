---
name: citation_generator
track: core
kind: local_formatter
provider: none
requires_env: []
inputs: [title, authors, year, journal, url]
outputs: [apa, bibtex, citation_key]
side_effect: false
---
# citation_generator

Creates deterministic APA-style and BibTeX citations from paper metadata. Use
this tool when the user asks to cite a known paper or to export its metadata as
BibTeX; it does not search for missing metadata and does not access the network.

`title`, `authors`, and `year` are required. `authors` may be a display string
(for example, `"Vaswani et al."`) or a list of author names. `journal` and
`url` are optional. Author names are preserved as supplied rather than guessed
or rearranged, so callers should pass names in their desired display form.
