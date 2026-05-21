# AGENTS.md

## Scope

This `jh-206.github.io` repository is a top-level Codex project for building and maintaining a personal GitHub Pages website.

Its main purpose is to hold shared instructions, project context, durable notes, and website files that Codex can use over time.

---

## File Edit Gate

* Do NOT modify any files by default.
* Wait for explicit user instruction before changing any file.
* Do NOT infer permission to edit files from requests to read, review, summarize, analyze, inspect, explain, extract, or respond to material.
* If the request is ambiguous, remain read-only and stop after reporting findings.
* Only treat a request as edit permission when the user clearly asks to create, modify, rewrite, patch, update, or delete specific files or project content.

---

## Workspace Rules

* Keep project files organized and easy to inspect.
* Do NOT move files between directories unless explicitly asked.
* Do NOT make edits outside this project directory unless explicitly asked.
* Keep commits confined to the correct repository.
* Treat this directory as shared context for the website project.

---

## Shared Context

* Use this directory for shared Codex instructions and high-level project context.
* Keep durable project memory in explicit files that collaborators can inspect and edit.
* Prefer short, factual updates over long narrative notes.
* Record decisions and current priorities here when that context should be useful later.

---

## Editing Style

* Be concise by default.
* Prefer short, direct wording over setup, repetition, or unnecessary framing.
* Make small, reviewable changes.
* When uncertain, ask or stop rather than guessing.

---

## Command Style

* When giving shell commands for work in this project, prefer commands relative to the project root directory.
* Do NOT default to absolute paths when a project-root-relative command is sufficient.
* Assume commands are run from the project root unless otherwise stated.
* Use absolute paths or `git -C` only when needed to avoid ambiguity.

---

## Git Discipline

* Before any commit, check the actual repo state with `git status`.
* Before Codex commits, it must check whether the intended changes are staged or unstaged and give the user a working command to review the actual diff in the correct repository before committing.
* Do not assume the current directory; use explicit paths or `git -C` when needed.
* Stage only the intended files; do not use broad staging commands unless verified safe.
* If the user asks to commit and the intended scope is clear, make the commit instead of only suggesting commands.
