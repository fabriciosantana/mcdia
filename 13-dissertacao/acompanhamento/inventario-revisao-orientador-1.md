# Inventário da primeira revisão do orientador

**Data do levantamento:** 10/11/2026.  
**Orientador:** Prof. Dr. Marcelo Rodrigo Machado Pita.  
**Revisão informada pelo autor:** branch `revisao-orientador-#1`, sincronizado em `main`.

## Escopo e critérios

Este inventário consolida a leitura integral dos capítulos da dissertação, dos elementos pré e pós-textuais e dos dois arquivos de capítulos desativados em `texto-Latex/main.tex`. As evidências principais são as marcações `\pita` preservadas no texto atual.

Foram organizados **21 itens para acompanhamento** e **16 grupos de intervenções já incorporadas**. Esses totais representam unidades de acompanhamento, não a contagem de comandos LaTeX: comentários compostos foram desdobrados e comentários repetidos foram agrupados.

“Incorporado” indica que a alteração está visível no texto, não aprovação ou encerramento pelo orientador. A sincronização dos comentários em `main` não implica que as solicitações tenham sido atendidas. As indicações do que falta são interpretações de acompanhamento, sem atribuição de prioridade, prazo ou aceite pelo autor.

**Limite de rastreabilidade:** durante o levantamento, não foi possível executar a comparação completa do histórico Git por falha do ambiente. Portanto, alterações sem marcação não foram atribuídas ao orientador. A referência local de `main` consultada foi `7bd1173dcc1a5004e7b725bb442c21237c1032fd`; a referência local do branch de revisão foi `84a69ef2a9d708dd21b40f23933864f730f0c2f6`. O reflog local registra a integração deste último em `main`, mas não foi feita atualização remota das referências.

## Solicitações para acompanhamento

Os itens seguem a ordem de aparecimento no texto, não uma ordem de prioridade. As linhas correspondem à versão lida em 10/11/2026. Os links apontam para os arquivos de origem.

| ID | Localização | Resumo da solicitação | Situação observada e complemento necessário |
| --- | --- | --- | --- |
| P01 | [Introdução](../texto-Latex/capitulos/01-introducao.tex), linhas 131–133 | Escrever o parágrafo final de introdução descrevendo a organização da dissertação. | Pendente: há apenas o título e a instrução de preenchimento. Apresentar a sequência efetivamente compilada após a reorganização. |
| P02 | [Referencial teórico](../texto-Latex/capitulos/02-referencial-teorico.tex), linhas 56–58 | Detalhar o domínio legislativo: volume, granularidade documental, diversidade temática e complexidade das perguntas. | Sugestão de aprofundamento: o orientador afirma que não é uma observação de correção. Há informações dispersas em outras seções; falta articulá-las ao desafio avaliativo no argumento do referencial. |
| P03 | [Referencial teórico](../texto-Latex/capitulos/02-referencial-teorico.tex), linhas 135–136 | Explicar QA na primeira ocorrência; o orientador sugere que se trata de Question Answering. | Pendente: a sigla aparece na tabela sem definição anterior. Não consta da lista de siglas; conferir essa lista é um desdobramento editorial, não outro pedido expresso. |
| P04 | [Referencial teórico](../texto-Latex/capitulos/02-referencial-teorico.tex), linha 138 | Definir NLI na primeira ocorrência. | Pendente: a sigla aparece na tabela e na discussão dos protocolos sem definição. |
| P05 | [Referencial teórico](../texto-Latex/capitulos/02-referencial-teorico.tex), linhas 140–143; intervenção relacionada na linha 83 | Definir e uniformizar groundedness e grounding, ou adotar os correspondentes em português, em todas as ocorrências. | Parcialmente incorporado: “aderência ao contexto recuperado (groundedness)” já aparece antes da tabela. Resta conferir os demais usos e explicar grounding. A observação de que a tabela seria a primeira ocorrência já não corresponde exatamente à versão atual. |
| P06 | [Referencial teórico](../texto-Latex/capitulos/02-referencial-teorico.tex), linhas 145–146 | Explicar utilidade downstream. O orientador a interpreta como a capacidade de um documento recuperado melhorar o desempenho na geração. | Há explicação posterior no parágrafo sobre eRAG, mas falta esclarecer a primeira apresentação do termo na tabela. |
| P07 | [Referencial teórico](../texto-Latex/capitulos/02-referencial-teorico.tex), linhas 188–189 | Articular a síntese comparativa com a lacuna de pesquisa e evitar repetições. | Pendente de revisão: ambas retomam a integração de técnicas e a adaptação ao contexto parlamentar brasileiro. Diferenciar suas funções e ajustar a transição. |
| P08 | [Procedimentos metodológicos](../texto-Latex/capitulos/04-procedimentos-metodologicos.tex), linhas 31–34 | Descrever a técnica de revisão bibliográfica e técnico-normativa: fontes, critérios de inclusão e exclusão, síntese e fichamento. | Pendente: a subseção contém somente a instrução. Descrever o procedimento realmente empregado. |
| P09 | [Procedimentos metodológicos](../texto-Latex/capitulos/04-procedimentos-metodologicos.tex), linha 45 | Informar onde a versão do corpus foi publicada. | Pendente no trecho: versão e hash estão presentes, mas falta a localização de acesso à versão utilizada. |
| P10 | [Procedimentos metodológicos](../texto-Latex/capitulos/04-procedimentos-metodologicos.tex), linhas 46–47 | Disponibilizar o script de coleta e instruções de reprodução. O orientador prefere indicar onde está publicado; alternativamente, incluí-lo em apêndice. | Pendente no manuscrito. O apêndice pode conter o link do repositório e instruções de uso; não é necessário duplicar integralmente o código se essa alternativa atender à finalidade. |
| P11 | [Procedimentos metodológicos](../texto-Latex/capitulos/04-procedimentos-metodologicos.tex), linhas 50–51; [caso empírico](../texto-Latex/capitulos/05-artefato-e-caso-empirico.tex), linha 38 | Apresentar a prova de conceito antes de pressupor que o leitor a conhece. | A subseção “Prova de conceito realizada” foi criada, mas está vazia. As menções genéricas existentes não substituem sua apresentação. Contextualizar a primeira menção e distinguir a prova anterior da execução final da dissertação. |
| P12 | [Procedimentos metodológicos](../texto-Latex/capitulos/04-procedimentos-metodologicos.tex), linhas 71–80 | Avaliar o excesso de conceitos pouco claros e mover a discussão empírica para o caso estudado. | O parágrafo destacado permanece na metodologia. Explicar ou simplificar quadro de prontidão, limiares heurísticos, critérios de certificação, indexabilidade, cobertura de texto integral e duplicidade exata excedente; separar critérios metodológicos de resultados e conclusões. |
| P13 | [Procedimentos metodológicos](../texto-Latex/capitulos/04-procedimentos-metodologicos.tex), linhas 99–100 | Organizar “Técnicas de análise dos dados” em mais subseções. | Pendente: recuperação, geração, comparação de avaliadores e análise qualitativa continuam em uma sequência extensa de parágrafos. |
| P14 | [Procedimentos metodológicos](../texto-Latex/capitulos/04-procedimentos-metodologicos.tex), linhas 99–100 | Detalhar métricas de recuperação com fórmulas e referências. | Há explicações verbais e referências gerais, mas faltam fórmulas. Detalhar as métricas efetivamente adotadas, preservando as condições já previstas para uso de Precision@k e nDCG conforme os julgamentos de relevância. |
| P15 | [Procedimentos metodológicos](../texto-Latex/capitulos/04-procedimentos-metodologicos.tex), linhas 138–139 | Conferir a sobreposição entre técnicas de análise e operacionalização das hipóteses; fundir ou reorganizar quando necessário. | O deslocamento já ocorreu; a revisão de redundâncias permanece. Rubrica e unidades de análise são retomadas nas duas partes. |
| P16 | [Procedimentos metodológicos](../texto-Latex/capitulos/04-procedimentos-metodologicos.tex), linha 143 | Explicar k na operacionalização de H1. | A inserção “onde k é...” permanece incompleta após `k=5`. A explicação anterior de top-k não preenche a lacuna local. |
| P17 | [Procedimentos metodológicos](../texto-Latex/capitulos/04-procedimentos-metodologicos.tex), linha 145 | Adicionar referência para Hit@5 ou explicá-la em nota de rodapé. | A instrução permanece no texto, embora Hit@k tenha uma explicação verbal anterior. |
| P18 | [Procedimentos metodológicos](../texto-Latex/capitulos/04-procedimentos-metodologicos.tex), linha 145 | Completar a condição de refutação de H2. | Permanece “[E SERÁ REFUTADA SE...]”. A introdução já prevê rejeição por desempenho homogêneo ou inverso ao esperado, mas falta a regra correspondente na operacionalização. |
| P19 | [Procedimentos metodológicos](../texto-Latex/capitulos/04-procedimentos-metodologicos.tex), linhas 192–195 | Demonstrar viabilidade com recursos concretos e informar se estão disponíveis. | O texto enumera condições gerais. Especificar os meios efetivos relativos ao corpus, infraestrutura, avaliadores, custos e tempo, distinguindo disponibilidade de dependências ainda abertas. O orientador não exige uma plataforma específica. |
| P20 | [Caso empírico](../texto-Latex/capitulos/05-artefato-e-caso-empirico.tex), linha 22 | Explorar mais tabelas e gráficos na caracterização do corpus. | Pendente: os resultados transferidos da análise exploratória estão em prosa. O orientador não fixa quantidade ou tipos de gráfico. |
| P21 | [Considerações finais](../texto-Latex/capitulos/08-consideracoes-finais.tex), linha 17 | Preencher “Cronograma de execução”. | O título marcado está vazio. A necessidade de preenchimento é inferida da inclusão da subseção; não há comentário separado fixando formato ou datas. Existe `cronograma/cronograma.tex`, cuja atualidade e eventual reaproveitamento não foram avaliados neste inventário. |

## Intervenções já incorporadas

Estas entradas registram o que o orientador alterou ou declarou ter movido. Não representam automaticamente novas tarefas de reescrita.

| ID | Intervenção identificada | Localização | Situação e complemento |
| --- | --- | --- | --- |
| I01 | Expansão de LLM como Large Language Model na abertura. | Introdução, linha 5. | Redação incorporada. |
| I02 | Transferência de “Hipóteses de trabalho” para a introdução. | Introdução, linhas 89–102; `main.tex`. | Incorporada; o arquivo autônomo de hipóteses está desativado. |
| I03 | Transferência da operacionalização das hipóteses para a metodologia. | Introdução, linha 104; metodologia, linhas 136–149. | Incorporada; conferir sobreposição conforme P15. |
| I04 | Identificação da subseção “Justificativa da pesquisa”. | Introdução, linha 125. | Título marcado e texto presentes. |
| I05 | Precisão da exposição sobre Transformer, alinhamento, remissão à figura do pipeline e reranqueamento ou reclassificação. | Referencial, linhas 15–31. | Ajustes incorporados. |
| I06 | Explicitação das três camadas complementares: recuperação documental, geração e julgamento das respostas. | Referencial, linhas 37–43. | Redação incorporada, preservando distinção analítica e articulação. |
| I07 | Incorporação dos trabalhos relacionados ao referencial teórico. | Referencial, linhas 103–105; `main.tex`. | Incorporada; o arquivo autônomo permanece desativado. |
| I08 | Melhor apresentação da seleção dos estudos, da tabela comparativa e das transições para sistemas e protocolos. | Referencial, linhas 107–111 e 148–150. | Redação incorporada; termos pendentes em P03–P06. |
| I09 | Ajuste da exposição de Reuter et al.: erro documental, apresentação de SAC e ressalva sobre transferência para outros domínios. | Referencial, linhas 160–165. | Redação incorporada. Este registro resume a intervenção, sem constituir nova verificação bibliográfica do estudo citado. |
| I10 | Ajustes locais de redação e coesão: “as técnicas de avaliação”, “Considerando essa literatura”, “este trabalho”, “Esta dissertação”, julgamentos humanos “com análise de erros” e estudos “no idioma inglês”; itálico em grounding e corpus. | Referencial, linhas 74, 82–83, 107–109, 157, 184 e 198. | Incorporados; a uniformização conceitual é acompanhada em P05. |
| I11 | Ajustes no título e na apresentação da metodologia, destaque de “Técnicas de análise exploratória de dados”, enumeração explícita de métricas e remissões a “Esta seção”. | Metodologia, linhas 1–4, 57 e 105; caso empírico, linha 3; resultados, linha 3. | Alterações visíveis. A expressão “Até o presente momento da, foram concluídas” ficou incompleta; conferir a redação é observação deste levantamento, não outro pedido do orientador. |
| I12 | Remoção das menções a “Notebook 01” e “Notebook 02”, privilegiando a descrição do que foi feito. | Metodologia, linhas 65–66 e 85. | Remoções declaradas e visíveis na prosa. Isso não impede a disponibilização de código para reprodução, solicitada em P10. |
| I13 | Transferência de números, resultados e conclusões da AED para o caso empírico. | Metodologia, linhas 68–69; caso empírico, linhas 15–20. | Transferência visível, mas incompleta quanto ao parágrafo de prontidão (P12). |
| I14 | Criação de subseção própria para a matriz de opções metodológicas, com apresentação de sua função e caráter preliminar. | Metodologia, linhas 151–158. | Incorporada, com tabela presente. |
| I15 | Alteração dos títulos para “Sistema RAG e o acervo de discursos parlamentares” e “Resultados preliminares”. | Caso empírico e resultados, linha 1 de cada arquivo. | Títulos incorporados. A prova de conceito é acompanhada em P11. |
| I16 | Adequação dos títulos finais: contribuições “até o momento”, limitações “identificadas” e próximos passos “da pesquisa”. | Considerações finais, linhas 5, 9 e 13. | Títulos incorporados; os conteúdos permanecem como esqueleto. O cronograma é acompanhado em P21. |

## Conferência de cobertura e duplicações

- **Introdução:** pedidos e intervenções cobertos por P01 e I01–I04.
- **Referencial teórico:** comentários cobertos por P02–P07 e intervenções por I05–I10.
- **Procedimentos metodológicos:** comentários e lacunas cobertos por P08–P19 e intervenções por I03 e I11–I14.
- **Sistema RAG e acervo:** coberto por P11, P20, I11, I13 e I15.
- **Resultados preliminares:** marcações cobertas por I11 e I15. Os demais TODOs não foram atribuídos ao orientador.
- **Discussão:** leitura integral; sem marcações de revisão do orientador identificadas.
- **Considerações finais:** marcações cobertas por P21 e I16.
- **Resumo, abstract e lista de siglas:** lidos, sem marcações do orientador identificadas. A ausência de QA e NLI na lista contextualiza P03–P04, sem criar pedidos adicionais.
- **Apêndices e anexo:** lidos, sem marcações identificadas. O pedido de documentar a coleta está na metodologia (P10). O anexo está desativado em `main.tex`.
- **Dedicatória, agradecimentos e epígrafe:** lidos; elementos opcionais desativados, sem marcações de revisão identificadas.
- **Configuração e arquivo principal:** lidos para conferir metadados, significado dos marcadores e sequência efetivamente incluída.
- **Antigo arquivo de trabalhos relacionados:** lido integralmente. Os comentários de QA, NLI, groundedness/grounding e downstream, nas linhas 31–42, repetem P03–P06. As intervenções repetidas no referencial foram contabilizadas uma vez.
- **Antigo arquivo de hipóteses:** lido integralmente e desativado na compilação. A referência vigente para as hipóteses é a introdução; para a operacionalização, a metodologia.

## Limites de atribuição

Os TODOs sem marcação do orientador não foram convertidos em solicitações atribuídas a ele. Títulos marcados e vazios foram identificados como estruturas propostas, com necessidade de preenchimento inferida, sem inventar exigências de formato ou conteúdo.

Este inventário não altera a dissertação, não verifica resultados empíricos nem audita referências científicas. A decisão de atendimento e o encerramento de cada item permanecem com o autor e o orientador.
