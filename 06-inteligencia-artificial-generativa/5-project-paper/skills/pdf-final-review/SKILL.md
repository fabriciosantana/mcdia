---
name: pdf-final-review
description: Review compiled academic PDFs from LaTeX projects for final visual and presentation quality. Use when Codex is asked to inspect a generated PDF, check page breaks, tables, figures, footnotes, references, layout, readability, or delivery/submission readiness after LaTeX compilation.
---

# PDF Final Review

## Workflow

1. Identify the article directory, main `.tex` file, and expected PDF path.
2. Compile with `latexmk -pdf main.tex` from the article directory if the PDF is stale or source files changed.
3. Inspect the LaTeX log for undefined citations, undefined references, overfull boxes, table warnings, and package errors.
4. Render or visually inspect relevant PDF pages when layout matters.
5. Focus on defects that affect academic delivery: broken tables, captions separated from content, unreadable figures, bad page breaks, orphan headings, misplaced footnotes, unresolved links, and bibliography problems.
6. Fix source files when the problem is clear; otherwise report the page, symptom, and likely source file.
7. Recompile and recheck affected pages after fixes.

## Visual Checklist

- Title, author data, abstract, section headings, page numbers, and bibliography appear as expected.
- Tables and figures fit within margins and stay close to their discussion.
- Captions, notes, and legends are readable and not separated awkwardly from the object they describe.
- Footnotes and URLs do not overflow, collide, or create distracting page breaks.
- Citations and references are resolved and formatted consistently.
- Important section transitions do not start with isolated headings at the bottom of a page.
- The PDF has no obvious blank pages, clipped content, black boxes, missing glyphs, or unreadable text.

## Reporting

- Report page numbers and source files when known.
- Distinguish blocking defects from cosmetic issues.
- State whether compilation was run and whether warnings remain.
- Do not reopen content-level revision unless the visual problem reveals a substantive inconsistency.
