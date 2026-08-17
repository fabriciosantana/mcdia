---
name: chatbot-rag-article
description: Work on the chatbot-rag academic article about a RAG chatbot for Brazilian Senate parliamentary speeches. Use when Codex is asked to revise, continue, compile, evaluate, cite, or plan improvements inside the chatbot-rag directory.
---

# Chatbot RAG Article

## Required Context

When working in `chatbot-rag/`, read:

1. `AGENTS.md`
2. `NOTAS_REVISAO.md`
3. `main.tex`
4. Affected files in `sections/`
5. `chatbot-rag.bib` when citations or references are involved
6. Open GitHub Issues for `chatbot-rag` when continuing the editorial backlog

Use this skill together with `academic-latex-review` for manuscript-quality work and with `article-action-plan` when executing or updating the GitHub issue backlog.

## Manuscript Positioning

- Treat the manuscript as a reproducible proof of concept with potential journal evolution.
- Preserve the distinction between preliminary evidence, demonstrated contribution, and open questions.
- Position the contribution as a reproducible protocol for Portuguese legislative collections only when the text and evidence support that claim.
- Distinguish what is specific to Brazilian Senate speeches from what may transfer to other legislative corpora.
- Treat the RAG system as a sociotechnical solution, not merely a technical integration.

## Methodological Priorities

- Keep objectives, success criteria, results, and conclusion aligned.
- Distinguish retrieval evaluation, generation evaluation, and human evaluation.
- Do not present LLM-judge averages as standalone proof of quality.
- Relate numerical scores to qualitative examples, variance across runs, rubrics, and human review.
- Treat divergence between LLM judge and human reading as a potentially important methodological finding.
- For journal-oriented work, prioritize target journal choice, comparative table, Design Science Research framing, propositions, descriptive statistics, visualization, and integrity declarations before large new experiments.
- Preserve the current distinction between delivery-ready proof of concept and a stronger journal-submission version that may require new experiments.
- Before adding references on RAG, legal AI, legislative corpora, or evaluation frameworks, check `chatbot-rag.bib` for existing related entries and avoid duplicating keys.

## Files and Verification

- Main file: `main.tex`.
- Sections: `sections/`.
- Bibliography: `chatbot-rag.bib`.
- PDF output: `out/main.pdf`.
- Compile from `chatbot-rag/` with `latexmk -pdf main.tex` after LaTeX edits that affect the PDF.
- Check logs for undefined citations, broken references, table issues, and warnings that affect quality.

## Plan Updates

- Use GitHub Issues as the operational backlog for future editorial work.
- Treat `NOTAS_REVISAO.md` as the consolidated local context for review history, manuscript state, editorial decisions, and the strategic map inherited from the former action plan.
- Record progress notes in the corresponding issue with files changed, verification, limitations, and next steps.
- Update `NOTAS_REVISAO.md` when the manuscript's overall state changes.
- If an action is deferred because it needs new experiments, external data, journal selection, or human annotation, record the deferral as a decision rather than silently skipping it.
