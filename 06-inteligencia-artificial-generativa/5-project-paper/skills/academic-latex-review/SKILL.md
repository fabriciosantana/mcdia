---
name: academic-latex-review
description: Review, revise, and strengthen academic manuscripts written in LaTeX. Use when Codex is asked to improve an article, section, abstract, introduction, literature review, methodology, results, discussion, conclusion, tables, figures, citations, or publication readiness in a LaTeX repository.
---

# Academic LaTeX Review

## Workflow

1. Identify the article directory and read applicable `AGENTS.md` files.
2. Read local context files such as review notes, action plans, `main.tex`, affected section files, and the `.bib` file when citations are involved.
3. Determine whether the request is editorial, argumentative, methodological, bibliographic, formatting-related, or publication-oriented.
4. Make focused edits that improve academic quality without changing the study's claims beyond its evidence.
5. If LaTeX sources changed, compile from the article directory when the change affects the PDF.
6. Report the files changed, verification performed, and any remaining risks.

## Review Modes

- If the user asks for a review, lead with concrete findings ordered by severity and cite file paths.
- If the user asks for revision or improvement, edit the manuscript directly and summarize the rationale afterward.
- If the user asks for publication readiness, evaluate fit, contribution, evidence strength, formatting, references, declarations, and reproducibility.
- If the target journal is unknown and the requested change depends on journal scope or format, ask for the target before making large structural edits.

## Academic Quality Criteria

- Clarify the problem, gap, objective, contribution, method, evidence, interpretation, and limitations.
- Ensure each section has a clear argumentative role.
- Make contributions explicit, verifiable, and proportional to the results.
- Separate empirical observation from interpretation.
- Avoid broad claims unsupported by the data.
- Use calibrated language: "the results suggest", "in this experiment", "preliminary evidence", or stronger claims only when justified.
- Treat literature review as a critical argument, not a catalog of references.
- Position the manuscript against closely related work by corpus, method, evaluation, scope, and artifact availability.
- Preserve negative, ambiguous, or limiting results when they matter to rigor.
- Check whether introduction, objectives, methodology, results, discussion, and conclusion remain aligned after edits.
- Check whether the abstract matches the final manuscript, including method, corpus, main results, contribution, and central limitation.
- Prefer changes that improve argumentative force, methodological transparency, or evidentiary discipline over purely stylistic polishing.

## Citation and Bibliography Checks

- Before adding citations, inspect the article `.bib` file for existing entries.
- Prefer peer-reviewed work, strong surveys, proceedings, institutional reports, and official sources.
- Verify preprint publication status when relevant to submission.
- Do not remove citations or methodological notes without a reason.
- When adding or changing citation keys, confirm the keys exist in the `.bib` file.

## LaTeX Practices

- Preserve the existing file organization and macros.
- Keep edits scoped to affected sections unless consistency requires cross-section changes.
- Recompile with `latexmk -pdf main.tex` from the article directory when PDF output may change.
- Inspect logs for undefined citations, broken references, table issues, and significant warnings.

## Definition of Done

- The changed text states no claim stronger than the evidence supports.
- Cross-section consistency was checked for the affected claim, term, method, or result.
- Citation keys introduced or changed are present in the `.bib` file.
- Compilation was run or the reason for not compiling was reported.
- Remaining limitations or editorial decisions are explicit.
