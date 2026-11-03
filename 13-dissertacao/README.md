# Dissertação — instruções de desenvolvimento e compilação

Este diretório contém o texto da dissertação, os fichamentos, os notebooks, os dados derivados e o cronograma. 

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

Para uma instalação completa, pode-se usar:

```bash
sudo apt install -y texlive-full
```

Em macOS, o equivalente é o TeX Live do Homebrew, que já traz `latexmk`, `biber` e todos os pacotes usados pelo projeto:

```bash
brew install texlive
```

Também funciona `brew install --cask mactex-no-gui` (MacTeX, sem os aplicativos gráficos). Para conferir a instalação:

```bash
latexmk --version | head -1
biber --version | head -1
pdflatex --version | head -1
```

A opção `accite` do estilo `biblatex-abnt` só existe na versão 4.0 ou superior do pacote. O preâmbulo de `main.tex` detecta a versão instalada e se adapta, de modo que o mesmo arquivo compila tanto em TeX Live 2023 (pacotes do Ubuntu 24.04) quanto em TeX Live 2026 (Homebrew).

## Clonagem

Para trabalhar na versão destinada ao orientador:

```bash
git clone --branch revisao-orientador-#1 \
  --single-branch \
  git@github.com:fabriciosantana/mcdia.git
cd mcdia/13-dissertacao
```

Se o acesso SSH não estiver configurado, use HTTPS:

```bash
git clone --branch revisao-orientador-#1 \
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

Sugestões do orientador devem ser feitas no branch `revisao-orientador-#1`. Depois de revisar o texto, registre as alterações com uma mensagem descritiva:

```bash
git status
git add texto-Latex
# ou adicione apenas os arquivos revisados
git commit -m "revisa texto para qualificacao"
git push
```

Evite adicionar os arquivos gerados em `texto-Latex/out/` e `texto-Latex/aux/` ao commit; eles são produtos locais da compilação.

### Marcas de revisão do orientador

`texto-Latex/config/marcadores.tex` (carregado por `main.tex`) define os marcadores em verde usados na revisão. São visuais: não alteram o conteúdo do texto.

```latex
\pita{texto revisado}
\pitacom{texto revisado}{motivo da intervenção}
\pitanota{motivo em nota de rodapé}
\begin{pitabloco} ... \end{pitabloco}   % trechos com mais de um parágrafo
```

O verde desaparece sozinho na versão de entrega (opção `entrega` em `main.tex`) e pode ser desligado a qualquer momento com `\pitacorfalse`. Não use os marcadores dentro de títulos de seção nem de legendas: o `hyperref` reprocessa esses argumentos e a cor vaza para os marcadores internos do PDF.

## Organização principal

- `texto-Latex/`: texto da dissertação e classe LaTeX;
- `fichamentos/`: fichas, fontes, inventários e sínteses bibliográficas;
- `notebooks/`: análises exploratórias e piloto experimental;
- `dados/`: dados locais, artefatos do piloto e saídas derivadas;
- `cronograma/`: cronograma em LaTeX e PDF;
- `acompanhamento/`: materiais de acompanhamento e reuniões.

O inventário bibliográfico congelado está documentado em `fichamentos/documentacao/BIBLIOGRAFIA_CONGELADA_2026-09-29.md` quando disponível na versão correspondente.
