# LaTeX Codespace

Este workspace vem preparado para editar e compilar projetos LaTeX no Codespaces.

## O que esta configurado

- Devcontainer com TeX Live via `apt`
- `latexmk`, `pdflatex` e `biber`
- Extensao `LaTeX Workshop` recomendada no VS Code
- Build em `out/` para manter a raiz mais limpa

## Como usar

1. Reabra o projeto no container.
2. Edite o `main.tex` existente ou crie seu proprio arquivo `.tex`.
3. Salve o arquivo para compilar automaticamente, ou rode a task `LaTeX: Build current file`.

## Compilar o projeto `chatbot-rag`

Para compilar o artigo em `/workspaces/latex/chatbot-rag`, use:

```bash
cd /workspaces/latex/chatbot-rag
latexmk -pdf -interaction=nonstopmode main.tex
```

O PDF final sera gerado em:

```bash
out/main.pdf
```
