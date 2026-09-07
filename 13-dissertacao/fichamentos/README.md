# Fichamentos-piloto

Documento independente da dissertação, com cinco páginas A4: três fichas (uma por referência), matriz comparativa e síntese temática. Revisado em 7 de setembro de 2026 para revisão do pesquisador e ajuste do formato com o orientador. O conteúdo foi preparado com assistência de IA; O pesquisador declarou ter lido os fichamentos; não declarou leitura dos textos-fonte.

## Arquivos e compilação

- `main.tex`: modelo visual e ordem das fichas.
- `fichas/01-ares.tex`, `02-kamerraad.tex` e `03-ipu.tex`: conteúdo editável.
- `fichas/modelo.tex`: ficha vazia para duplicar; não integra o PDF-piloto.
- `sintese/01-matriz.tex`: comparação estruturada das três referências.
- `sintese/02-sintese.tex`: síntese temática e questões para a continuidade da revisão.
- `out/main.pdf`: PDF compilado.
- `fontes/manifesto.json`: URLs, hashes, escopos de consulta e resultados da inspeção estrutural.
- `fontes/*.preflight.json`: diagnósticos estruturais dos PDFs de origem.

Execute a partir da pasta `fichamentos/`:

```bash
latexmk -pdf main.tex
```

O `latexmkrc` local direciona auxiliares para `aux/` e o PDF para `out/`. Não compilar com `latexmk -cd` a partir da pasta superior sem carregar explicitamente esse arquivo de configuração. Dependências: TeX Live com os pacotes declarados em `main.tex`, especialmente `newtxtext`, `geometry`, `microtype`, `fancyhdr`, `lastpage` e `hyperref`. Os PDFs de origem não são necessários para compilar.

## Escolhas do piloto

Fonte de corpo de 11 pontos, entrelinha de 1,05, margens laterais de 19 mm, títulos discretos em azul escuro e links clicáveis. Cada ficha distingue a contribuição interpretada, fragmentos extrativos em inglês e a análise proposta para a dissertação. Não foram produzidas traduções que pudessem ser confundidas com transcrições literais.

As fichas contêm excertos curtos e seletivos, não um resumo extrativo extenso de todos os argumentos. As páginas e seções permitem retomar o contexto das passagens. A área inferior registra o escopo consultado nesta preparação e reserva espaço para observações. “Leitura do texto-fonte pelo pesquisador: não registrada” não significa que o pesquisador não tenha lido o texto; significa que não houve declaração de leitura desses textos-fonte nesta sessão.

## Fontes e versões consultadas

1. **ARES:** PDF publicado pela ACL. Consulta das seções 1–7, páginas impressas 338–346, incluindo método, resultados e limitações. Apêndices não fichados. Metadados: https://aclanthology.org/2024.naacl-long.20/.
2. **KamerRaad:** conteúdo do preprint `arXiv:2404.17597v1`, páginas 1–4; referência da publicação conferida na Springer. Não houve comparação integral com o texto publicado. Os localizadores dos excertos são os do preprint, não os da edição Springer.
3. **IPU:** edição de dezembro de 2024; consulta da introdução (p. 3) e do caso 024 (p. 150–151). O relatório tem 172 páginas de arquivo; a ficha é deliberadamente parcial. Texto conferido também na extração do portal da IPU. O download direto retornou HTTP 403; a cópia local foi obtida no portal oficial do Senado neerlandês, com URL registrada no manifesto.

Os PDFs e suas extrações de trabalho estão disponíveis localmente em `fontes/`, mas são ignorados pelo Git. Os diagnósticos e o manifesto preservam a identificação dos arquivos.

## Divergência bibliográfica identificada

A entrada `rogiersEtAl2024kamerraad` em `../texto-Latex/referencias.bib` registra **Bram Kang** e **p. 503–519**. O preprint identifica **Bo Kang**, e a página editorial confirma **Bo Kang** e **p. 409–412**. O piloto usa os metadados conferidos. A bibliografia da dissertação não foi alterada.

Fonte da conferência: https://link.springer.com/chapter/10.1007/978-3-031-70371-3_30.

## Integridade e limites da conferência

A inspeção estrutural ARS retornou `PASS` para ARES e KamerRaad. Para a cópia da IPU, retornou `UNAVAILABLE`, com avisos do parser sobre referências internas do PDF. Esse estado permanece registrado, sem conversão em aprovação estrutural. As páginas impressas 3 e 151 e seus excertos foram conferidos visualmente na renderização, além do confronto com a extração do portal da IPU. Isso verifica as passagens usadas, sem certificar a estrutura integral do arquivo.

A verificação final abrange contagem de páginas, correspondência dos nove excertos com as passagens de origem, ausência de avisos de transbordamento na compilação e inspeção visual das três fichas. O piloto não constitui revisão sistemática nem certificação de completude da bibliografia.

## Revisão de 7 de setembro de 2026

Separados método, contribuição e resultado/orientação; distinguida a ressalva da fonte da análise crítica; explicitados destino e uso na dissertação. O bloco extrativo passou a se chamar “Excertos-chave”, pois contém fragmentos seletivos, não um resumo extenso. Mantidos o idioma original e os excertos já conferidos. Acrescentadas matriz comparativa e síntese temática com localizadores, sem inferir lacunas pela contagem de trabalhos ou pela leitura parcial. Nenhuma alteração nas hipóteses ou na bibliografia da dissertação.

## Pontos para avaliar com o orientador

- Os três fragmentos extrativos são suficientes ou é preferível reduzir outros campos para ampliar esse bloco?
- O texto em inglês deve permanecer sozinho ou vir acompanhado de tradução identificada?
- O aproveitamento específico de cada ficha e a síntese temática estão suficientemente distintos?
- O corpo de 11 pontos e o espaço de anotações funcionam bem na leitura impressa?

Para ampliar o documento, copie `fichas/modelo.tex`, preencha o conteúdo e inclua o arquivo em `main.tex` com uma quebra de página. A contagem total no rodapé é automática. Se uma ficha exceder uma página, revise a seleção e a concisão do conteúdo antes de reduzir a fonte.
