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

After pulling CV changes from Overleaf, update the website PDF and homepage with:

```sh
cd /Users/hirschij/Documents/Projects/jh-206.github.io
make site
```

Then review, commit, and push the website changes:

```sh
git status
git add assets/cv/Jonathon-Hirschi-CV.pdf index.html
git commit -m "Update CV PDF"
git push
```

Useful commands:

```sh
make cv      # compile and copy the CV PDF
make render  # regenerate index.html
make site    # compile/copy CV and regenerate index.html
```
