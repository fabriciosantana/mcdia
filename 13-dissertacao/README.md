# Dissertação — instruções de desenvolvimento e compilação

Este diretório contém o texto da dissertação, os fichamentos, os notebooks, os dados derivados e o cronograma. A versão atual está preparada para revisão do orientador e corresponde a uma **versão para qualificação**, não à versão final da dissertação.

## Requisitos

Em Ubuntu ou Debian, instale Git e o TeX Live com os pacotes usados pelo projeto:

```bash
sudo apt update
sudo apt install -y \
  git \
  latexmk \
  biber \
  texlive-latex-base \
  texlive-latex-recommended \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-fonts-extra \
  texlive-lang-portuguese \
  texlive-bibtex-extra \
  texlive-pictures
```

O executável `pdflatex` é instalado pelo pacote `texlive-latex-base`. Não é necessário instalar o abnTeX: o projeto usa a classe local `texto-Latex/idp.cls`, com `biblatex` no estilo `abnt` e Biber como backend bibliográfico.

Para uma instalação completa, pode-se usar:

```bash
sudo apt install -y texlive-full
```

## Clonagem

Para trabalhar na versão destinada ao orientador:

```bash
git clone --branch revisao-orientador-qualificacao-20261001 \
  --single-branch \
  git@github.com:fabriciosantana/mcdia.git
cd mcdia/13-dissertacao
```

Se o acesso SSH não estiver configurado, use HTTPS:

```bash
git clone --branch revisao-orientador-qualificacao-20261001 \
  --single-branch \
  https://github.com/fabriciosantana/mcdia.git
```

## Compilação da dissertação

```bash
cd texto-Latex
latexmk -pdf main.tex
```

O PDF será gerado em:

```text
texto-Latex/out/main.pdf
```

Os arquivos auxiliares ficarão em `texto-Latex/aux/`. A configuração em `texto-Latex/latexmkrc` mantém essa separação automaticamente.

Para limpar arquivos auxiliares, preservando o PDF:

```bash
latexmk -c
```

Para limpar também o PDF e reconstruir tudo:

```bash
latexmk -C
latexmk -pdf main.tex
```

## Atualização e revisão

Para atualizar a cópia local:

```bash
git pull --ff-only
```

Sugestões do orientador devem ser feitas no branch `revisao-orientador-qualificacao-20261001`. Depois de revisar o texto, registre as alterações com uma mensagem descritiva:

```bash
git status
git add texto-Latex
# ou adicione apenas os arquivos revisados
git commit -m "revisa texto para qualificacao"
git push
```

Evite adicionar os arquivos gerados em `texto-Latex/out/` e `texto-Latex/aux/` ao commit; eles são produtos locais da compilação.

## Organização principal

- `texto-Latex/`: texto da dissertação e classe LaTeX;
- `fichamentos/`: fichas, fontes, inventários e sínteses bibliográficas;
- `notebooks/`: análises exploratórias e piloto experimental;
- `dados/`: dados locais, artefatos do piloto e saídas derivadas;
- `cronograma/`: cronograma em LaTeX e PDF;
- `acompanhamento/`: materiais de acompanhamento e reuniões.

O inventário bibliográfico congelado está documentado em `fichamentos/documentacao/BIBLIOGRAFIA_CONGELADA_2026-09-29.md` quando disponível na versão correspondente.
