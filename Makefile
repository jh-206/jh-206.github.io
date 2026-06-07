CV_REPO := /Users/hirschij/Documents/Projects/Jonathon-Hirschi-CV
CV_BUILD := /private/tmp/jh-cv-build
CV_PDF := assets/cv/Jonathon-Hirschi-CV.pdf

.PHONY: help cv render site

help:
	@echo "Available targets:"
	@echo "  make cv      Compile the CV PDF and copy it into the website"
	@echo "  make render  Regenerate index.html from data/profile.yml"
	@echo "  make site    Run cv and render"

cv:
	mkdir -p $(CV_BUILD)
	latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=$(CV_BUILD) $(CV_REPO)/main.tex
	mkdir -p assets/cv
	cp $(CV_BUILD)/main.pdf $(CV_PDF)

render:
	python3 scripts/render_site.py

site: cv render
