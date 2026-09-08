# Fichamentos da revisão da literatura

Atualizado em 08/09/2026: **53 fichas de uma página**, nove páginas de matriz temática e duas de síntese (64 páginas). Das 52 entradas selecionadas em `texto-Latex/referencias.bib`, sete permanecem pendentes de acesso ou confirmação de versão. Consulte [o controle de cobertura](CONTROLE_COBERTURA.md).

A coleção foi preparada com assistência de IA. Cada ficha distingue contribuição interpretativa, excertos literais, natureza da evidência, limitações e aproveitamento proposto. A leitura é frequentemente focal: livros, revisões e relatórios extensos não são apresentados como integralmente lidos. A leitura dos textos-fonte pelo pesquisador não foi registrada; ele declarou leitura dos três fichamentos-piloto.

## Editar e compilar

O conteúdo final está nos arquivos **`fichas/*.tex`** e `sintese/*.tex`. Altere esses arquivos e recompile; o PDF é um produto da compilação. `main.tex` define o formato e a ordem. `fichas/modelo.tex` permanece como modelo vazio, fora da compilação.

Execute dentro de `fichamentos/`:

```bash
latexmk -pdf main.tex
```

O `latexmkrc` direciona auxiliares para `aux/` e o PDF para [out/main.pdf](out/main.pdf). Não é necessário ter os PDFs-fonte para compilar. O corpo das fichas usa 11 pontos, entrelinha 1,05 e margens laterais de 19 mm; a matriz usa 10 pontos.

## Evidência e rastreabilidade

- `inventario.csv` e `inventario.json`: situação das 52 referências, recortes e arquivos.
- `fontes/manifesto.json`: versões consultadas, URLs, hashes e escopos.
- `fontes/*.preflight.json`: inspeção estrutural dos PDFs; não certifica conteúdo científico.
- `fontes/lote-*-excertos.json`: cotejo literal, normalizando espaços, ligaturas e hifenização de linhas.
- `fontes/obtencao-*.json`: tentativas de obtenção, inclusive falhas.
- `fontes/pesquisa-bibliografica-adicional-2026-09-08.md`: relatório da busca adicional e critérios de incorporação.
- `fontes/bibliografia-adicional-candidata.bib`: candidatas adicionais separadas da bibliografia principal.
- `lote-01-dados.json` e `lote-02-dados.json`: notas estruturadas da preparação, preservadas como histórico; **não são fonte de regeneração automática**. Ajustes editoriais finais podem existir apenas no `.tex`.

Excertos são curtos e seletivos, no idioma original; não constituem transcrição extensa de todos os argumentos. Localizadores permitem retomar o contexto. A síntese relaciona temas sem presumir equivalência entre experimentos, descrições institucionais e ensaios conceituais.

NDAA e Viola et al. foram consultados por extração web do PDF oficial, sem PDF local. A nota local de Viola registra apenas o cotejo e a proveniência, não o texto integral. Para fontes com inspeção estrutural indisponível, usam-se âncoras textuais; o piloto IPU conserva páginas também conferidas visualmente.

## Antes da redação final

Confirmar versões bibliográficas, aprofundar as fontes centrais e revisar as interpretações. As cinco fontes prioritárias da busca adicional foram incorporadas a `texto-Latex/referencias.bib`; nove candidatas permanecem em `fontes/bibliografia-adicional-candidata.bib` para decisão posterior. As sete pendências impedem declarar cobertura integral. A coleção não constitui revisão sistemática exaustiva, e seus argumentos não são resultados experimentais da dissertação.
