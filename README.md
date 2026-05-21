# GitHub Pages Website

Project directory: `jh-206.github.io`

This repository is for building a personal GitHub Pages website.

## User Info

* Main public username: `jh-206`
* Alternative Alderaan/CU Denver supercomputing cluster username: `jonathonHir`

## Getting Started

1. Keep project notes and instructions in this repository.
2. Add website files here as we decide on the structure.
3. Use `AGENTS.md` for Codex guidance that should carry forward.
4. Build the README over time as the project becomes clearer.

## CV Workflow

The CV source lives outside this repository in `Documents/Projects/Jonathon-Hirschi-CV`.

The website publishes the compiled PDF at `assets/cv/Jonathon-Hirschi-CV.pdf`.

1. Update the CV source from Overleaf.
2. Compile `main.tex` to a PDF.
3. Copy the PDF to `assets/cv/Jonathon-Hirschi-CV.pdf`.
4. Run `python3 scripts/render_site.py`.
5. Commit and push the website changes.
