# LaTeX source

Amber Anson — *Preserving Human Intent in AI-Assisted Research: A Deployment Case Study and Coordination-Stack Pilot*. AI x Epistemics Research Sprint, November 2026. Final submitted version: 8 main pages, 14 pages in total.

## Build

From this directory:

```
tectonic --keep-logs --keep-intermediates main.tex
```

Alternatively, run XeLaTeX, then BibTeX, then XeLaTeX twice. The Old Standard TT fonts and their license are included. A first Tectonic build may download ordinary TeX packages. No model APIs are used.

## About the template

`apart_sprint.sty` is a local LaTeX adaptation of the official Apart sprint template, not an official TeX class. It keeps US Letter paper, one-inch margins, the Old Standard TT body font, and the template's ruled title block and section order. The official template PDF is not redistributed here.

## Overleaf

Choose New Project > Upload Project and upload this folder as a ZIP. Set the compiler to XeLaTeX and the main document to `main.tex`.

## What is not included

This folder excludes private archives, case-level outputs, keys, and local build tooling.
