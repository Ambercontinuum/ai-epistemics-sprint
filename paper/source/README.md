# Editable LaTeX paper draft

Amber Anson ? Preserving Human Intent in AI-Assisted Research: A Deployment Case Study and Coordination-Stack Pilot.

Working draft for PI review, not an approved submission. Eight main pages, one reference page and five appendix pages in the checked PDF.

Build from this directory: `tectonic --keep-logs --keep-intermediates main.tex`.
Alternatively run XeLaTeX, BibTeX, then XeLaTeX twice. Local Old Standard TT fonts and their license are included. A first Tectonic build may download ordinary TeX packages; no model APIs are used.

`apart_sprint.sty` is a local LaTeX adaptation of the official Apart sprint Google Doc/PDF, not an official TeX class. It preserves US Letter, one-inch margins, Old Standard TT body, ruled title/author block and section organization. The title is 18pt for a balanced two-line setting. Official template PDF is included for comparison.

Confirm author details, interpretations, disclosures and release permissions before submission. Draft notices remain deliberate. This bundle excludes private archives, case-level outputs, keys, private source paths and local build tooling. Public release still requires Amber's approval.

## Overleaf

Use New Project > Upload Project and upload the complete ZIP. Select XeLaTeX as compiler and main.tex as the main document. Uploading only main.tex omits its local style, fonts and bibliography.

Revision: Table 3 includes exact agreement; Appendix E contains all ten pairs across seven fields in strict and fence-normalized variants. The isolated sandbox is explicitly not independently reviewed.

Final revision (2026-11-16): Claude became lead drafting model at the PI's explicit assignment and added the role-boundary row to Table 1, a related future-work sentence, an all-pairs context sentence in Section 4.2, and LLM-usage disclosure; it also tightened Section 4.2 and Section 5 to keep the main text within eight pages. Because Claude is now an author of this text, its earlier review approval is not independent review of these revisions. Final PI approval is still required.
