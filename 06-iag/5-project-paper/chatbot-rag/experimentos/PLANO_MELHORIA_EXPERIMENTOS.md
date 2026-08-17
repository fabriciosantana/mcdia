# Plano de melhoria dos experimentos para submissao a periodico de alto rigor

Este documento define uma rodada futura de experimentos para fortalecer a evidencia empirica do artigo sobre chatbot RAG aplicado a discursos parlamentares do Senado Federal. O objetivo e transformar a avaliacao atual, hoje adequada como prova de conceito reprodutivel, em um desenho experimental mais robusto, auditavel e defensavel para submissao a revista de qualidade e prestigio academico.

## Objetivo geral

Avaliar, com maior rigor metodologico, se o pipeline RAG proposto melhora a recuperacao, a geracao e a verificabilidade de respostas sobre discursos parlamentares em comparacao com alternativas baselines, identificando tambem limites, falhas recorrentes, sensibilidade de configuracao e confiabilidade dos instrumentos de avaliacao.

## Principios de desenho experimental

- Separar explicitamente avaliacao da recuperacao, avaliacao da geracao, avaliacao automatizada por LLM juiz e avaliacao humana independente.
- Comparar o sistema proposto contra baselines relevantes, e nao apenas contra ele mesmo em rodadas repetidas.
- Construir um conjunto de perguntas e evidencias de referencia auditavel, com criterios claros de inclusao, categorias, respostas esperadas e documentos relevantes.
- Reportar desempenho por tipo de pergunta, e nao apenas por media agregada.
- Tratar divergencias entre avaliadores humanos e LLM juiz como achados metodologicos.
- Preservar artefatos, configuracoes, versoes, prompts, hashes e resultados brutos para reproducibilidade.
- Interpretar os resultados como evidencia graduada: viabilidade, ganho relativo, robustez, limite ou falha, conforme o caso.

## Estado atual e lacunas a superar

A versao atual do artigo ja distingue recuperacao, geracao, avaliacao por LLM juiz e inspecao humana/manual. Tambem registra tres rodadas automatizadas com 20 perguntas, estudos de caso manuais, analise de estabilidade, teste de sensibilidade com juiz alternativo e ameacas a validade.

Para uma submissao mais forte, ainda faltam:

- baseline lexical ou sem RAG;
- baseline com LLM sem recuperacao documental;
- metricas formais de recuperacao;
- bateria ampliada e balanceada de perguntas;
- gold standard de documentos ou chunks relevantes;
- anotacao humana independente, com medida de concordancia;
- estudo de ablacao de metadados, chunking, top-k, prompt e reranqueamento;
- avaliacao estatistica com intervalos de confianca, variacao por categoria e comparacoes pareadas;
- protocolo completo de reproducibilidade.

## Questoes de pesquisa da nova rodada

1. Em que medida o pipeline RAG recupera documentos ou chunks relevantes para diferentes tipos de perguntas sobre discursos parlamentares?
2. Em que medida as respostas geradas sao factualmente corretas, fundamentadas nas fontes recuperadas e adequadamente calibradas quanto a incerteza?
3. O pipeline RAG apresenta ganho empirico em relacao a baselines lexicais, semanticos simples e LLM sem RAG?
4. Quais componentes do pipeline mais afetam o desempenho: metadados, tamanho de chunk, overlap, top-k, prompt, embedding ou reranqueamento?
5. Qual e o grau de concordancia entre avaliacao humana independente e avaliacao por LLM juiz?
6. Quais tipos de pergunta geram maior risco de erro: numericas, comparativas, multifocais, multietapas, autoria cruzada, desambiguacao ou evidencia negativa?
7. Quais partes do protocolo parecem transferiveis para outros acervos legislativos e quais dependem do corpus da 56a Legislatura?

## Desenho experimental proposto

### Fase 0 - Congelamento do corpus e da configuracao

Antes da nova rodada, congelar uma versao experimental do corpus, da base vetorial, do prompt e das configuracoes.

Artefatos esperados:

- manifesto do corpus usado;
- hash dos arquivos de entrada;
- versoes de scripts, modelos, embeddings, Open WebUI e ChromaDB;
- parametros de chunking e ingestao;
- prompt operacional;
- configuracao da knowledge base;
- data e identificador da rodada.

Essa fase evita que resultados posteriores fiquem ambiguos por mudancas silenciosas na base ou na configuracao.

### Fase 1 - Bateria ampliada de perguntas

Substituir a bateria atual de 20 perguntas por um conjunto balanceado de, no minimo, 80 a 120 perguntas. Para uma versao mais ambiciosa, mirar 150 a 200 perguntas, desde que haja capacidade de anotacao humana.

Categorias recomendadas:

- factual simples;
- foco no autor;
- desambiguacao de autoria;
- evidencia negativa ou pergunta nao respondivel;
- comparacao entre autores;
- comparacao temporal;
- pergunta numerica;
- sintese tematica;
- pergunta multietapas;
- autoria cruzada;
- controle de escopo;
- estresse de recuperacao;
- pergunta ampla ou multifocal;
- pergunta de verificacao de citacao ou fonte.

Cada pergunta deve registrar:

- identificador estavel;
- texto da pergunta;
- categoria principal;
- categorias secundarias, quando houver;
- grau esperado de dificuldade;
- se a pergunta e respondivel no corpus;
- resposta esperada ou criterio de resposta aceitavel;
- documentos ou chunks relevantes;
- observacoes de escopo e riscos de avaliacao.

### Fase 2 - Gold standard de recuperacao

Criar um gold standard para avaliar recuperacao independentemente da geracao. Para cada pergunta, pelo menos dois avaliadores devem indicar os documentos, discursos ou chunks considerados relevantes.

Campos minimos:

- `question_id`;
- `source_id` ou identificador do discurso;
- `chunk_id`, quando aplicavel;
- relevancia binaria ou graduada;
- trecho de evidencia;
- justificativa curta;
- avaliador;
- status apos adjudicacao.

Medidas recomendadas:

- `Hit@k`;
- `Recall@k`;
- `Precision@k`;
- `MRR`;
- `nDCG@k`;
- cobertura de fontes relevantes;
- diversidade de fontes recuperadas;
- taxa de recuperacao de fonte incorreta.

Essa etapa e essencial porque uma resposta aparentemente boa pode ocorrer apesar de recuperacao fraca, e uma recuperacao boa pode ser desperdicada por uma geracao inadequada.

### Fase 3 - Protocolo de anotacao humana

Criar diretrizes de anotacao para avaliacao humana independente das respostas geradas. O ideal e usar dois ou tres avaliadores, com etapa inicial de calibracao e adjudicacao posterior.

Dimensoes de avaliacao:

- corretude factual;
- aderencia ao contexto recuperado;
- fidelidade as fontes;
- completude proporcional a pergunta;
- precisao de autoria;
- precisao numerica, quando aplicavel;
- qualidade da citacao ou referencia documental;
- calibracao da incerteza;
- abstencao adequada em perguntas nao respondiveis;
- ausencia de alucinacao;
- utilidade para consulta assistida.

Procedimento recomendado:

1. Elaborar manual de anotacao com exemplos positivos, negativos e limitrofes.
2. Realizar piloto com 10 a 15 perguntas.
3. Medir concordancia inicial.
4. Ajustar rubrica e instrucoes.
5. Executar anotacao cega e independente.
6. Calcular concordancia interavaliadores.
7. Adjudicar divergencias.
8. Preservar divergencias relevantes como evidencias qualitativas.

Medidas possiveis:

- Cohen's kappa, se houver dois avaliadores;
- Krippendorff's alpha, se houver mais avaliadores ou escalas ordinais;
- percentual de concordancia por criterio;
- matriz de confusao entre categorias de julgamento.

### Fase 4 - Sistemas comparados e baselines

Avaliar o pipeline proposto em comparacao com alternativas que ajudem a isolar o valor do RAG.

Sistemas minimos:

- RAG atual com Open WebUI, metadados e prompt operacional;
- LLM sem RAG, respondendo apenas com conhecimento parametrico e instrucao de cautela;
- busca lexical, por exemplo BM25 ou equivalente;
- recuperacao vetorial sem geracao, avaliando apenas documentos retornados;
- RAG com prompt simplificado.

Sistemas desejaveis:

- RAG hibrido lexical + vetorial;
- RAG com reranqueador;
- RAG com outro embedding;
- RAG com outro modelo gerador;
- RAG com outro LLM juiz;
- RAG com top-k variado.

Os baselines devem ser simples, transparentes e reprodutiveis. O objetivo nao e vencer todos os sistemas possiveis, mas demonstrar ganho relativo, custo metodologico e limites da proposta.

### Fase 5 - Estudos de ablacao

Executar ablacoes para estimar o impacto de componentes do pipeline.

Ablacoes prioritarias:

- com metadados completos versus sem metadados;
- chunk grande versus chunk medio versus chunk pequeno;
- com overlap versus sem overlap;
- top-k baixo, medio e alto;
- prompt completo versus prompt minimo;
- com citacao obrigatoria versus sem citacao obrigatoria;
- com reranqueamento versus sem reranqueamento, se viavel.

Resultados esperados:

- identificar quais componentes realmente contribuem para recuperacao e geracao;
- evitar atribuir todo ganho ao RAG de forma generica;
- orientar simplificacao ou fortalecimento do pipeline;
- produzir evidencias sobre decisoes de design.

### Fase 6 - Avaliacao por LLM juiz

Manter a avaliacao por LLM juiz, mas rebaixar seu papel para instrumento auxiliar calibrado contra avaliacao humana.

Procedimento recomendado:

- usar rubrica explicita e versionada;
- avaliar as mesmas respostas julgadas por humanos;
- comparar LLM juiz e avaliadores humanos;
- testar pelo menos dois modelos juizes;
- variar a ordem ou o formato de apresentacao em amostra de sensibilidade;
- analisar casos em que o LLM juiz atribui nota alta a resposta humanamente inadequada;
- analisar casos em que o LLM juiz e mais severo que humanos.

Medidas recomendadas:

- correlacao de Spearman entre notas humanas e automaticas;
- diferenca media absoluta entre avaliadores;
- taxa de falso positivo de qualidade;
- taxa de falso negativo de qualidade;
- concordancia por categoria de pergunta;
- analise qualitativa de divergencias.

### Fase 7 - Analise estatistica

Reportar resultados com cautela estatistica, evitando depender apenas de medias.

Analises recomendadas:

- media, mediana, desvio padrao e intervalo interquartil por sistema;
- intervalo de confianca por bootstrap;
- comparacoes pareadas entre sistemas por pergunta;
- efeito por categoria de pergunta;
- distribuicao de erros por tipo;
- analise de estabilidade entre rodadas;
- analise de sensibilidade por modelo e configuracao;
- visualizacoes de dispersao e variacao, nao apenas tabelas agregadas.

Quando houver multiplas comparacoes, registrar cautela interpretativa e evitar conclusoes fortes sobre diferencas pequenas.

### Fase 8 - Analise qualitativa dos erros

Selecionar casos representativos para leitura qualitativa profunda.

Classes de erro esperadas:

- recuperacao de fonte irrelevante;
- recuperacao parcial;
- mistura indevida de autores;
- extrapolacao alem do contexto;
- resposta correta com citacao fraca;
- citacao correta com resposta incompleta;
- erro numerico;
- falha de abstencao;
- resposta formalmente plausivel, mas fora do escopo documental;
- divergencia entre avaliacao humana e LLM juiz.

O manuscrito deve apresentar poucos exemplos, mas bem escolhidos, conectando cada exemplo ao argumento metodologico.

### Fase 9 - Reprodutibilidade e ciencia aberta

Organizar a nova rodada para permitir auditoria externa.

Artefatos recomendados:

- conjunto de perguntas;
- gold standard de recuperacao;
- diretrizes de anotacao;
- respostas brutas por sistema;
- julgamentos humanos anonimizados, quando aplicavel;
- julgamentos por LLM juiz;
- scripts de execucao;
- scripts de analise;
- arquivo de configuracao por rodada;
- manifesto de versoes;
- hashes de corpus, prompts e resultados;
- tabelas finais em formato aberto;
- figuras geradas a partir de scripts.

Se houver submissao a periodico, avaliar deposito em Zenodo, OSF ou repositorio institucional, conforme politica editorial.

## Criterios de sucesso

A nova rodada deve ser considerada satisfatoria para fortalecer o artigo se entregar:

- comparacao com pelo menos dois baselines;
- avaliacao formal da recuperacao;
- avaliacao humana independente em amostra suficientemente documentada;
- medida de concordancia entre anotadores;
- analise de divergencia entre humano e LLM juiz;
- resultados por categoria de pergunta;
- estudo de pelo menos tres ablacoes prioritarias;
- artefatos versionados e reprodutiveis;
- discussao clara de limites e ameacas a validade.

Para um periodico de maior prestigio, a meta ideal e acrescentar:

- bateria com 150 ou mais perguntas;
- tres avaliadores humanos;
- avaliacao com dois modelos geradores e dois modelos juizes;
- baseline hibrido lexical-vetorial;
- intervalos de confianca e testes pareados;
- deposito publico formal dos artefatos.

## Estrutura recomendada de arquivos

```text
chatbot-rag/experimentos/
  PLANO_MELHORIA_EXPERIMENTOS.md
  protocolo/
    protocolo_experimental.md
    annotation_guidelines.md
    rubric_humana.md
    rubric_llm_juiz.md
  dados/
    perguntas_v2.csv
    gold_standard_recuperacao.csv
    manifest_corpus.json
  configs/
    rag_atual.yaml
    baseline_sem_rag.yaml
    baseline_bm25.yaml
    ablation_metadata_off.yaml
  resultados/
    runs/
    julgamentos_humanos/
    julgamentos_llm/
  analise/
    metricas_recuperacao.csv
    metricas_geracao.csv
    divergencias.md
    figuras/
```

## Portoes de decisao

- Gate 0: protocolo aprovado antes de executar a rodada.
- Gate 1: bateria de perguntas e gold standard revisados.
- Gate 2: piloto concluido com revisao das rubricas.
- Gate 3: execucao completa dos sistemas e baselines.
- Gate 4: anotacao humana concluida e concordancia calculada.
- Gate 5: analise estatistica e qualitativa fechada.
- Gate 6: secao de experimentos, discussao, conclusao e declaracoes revisadas no manuscrito.

## Sequencia operacional sugerida

1. Atualizar a issue #12 como guarda-chuva da nova rodada experimental.
2. Criar issues filhas para protocolo, perguntas, gold standard, anotacao humana, baselines, ablacoes, analise estatistica e revisao do manuscrito.
3. Escrever o protocolo experimental antes de gerar novos resultados.
4. Montar a bateria ampliada de perguntas.
5. Construir gold standard de recuperacao.
6. Executar piloto com pequena amostra.
7. Ajustar rubricas e configuracoes.
8. Rodar sistemas e baselines.
9. Conduzir anotacao humana independente.
10. Comparar humanos, LLM juiz e resultados automaticos.
11. Atualizar tabelas, figuras e texto do artigo.
12. Revisar ameacas a validade e limites de generalizacao.

## Impacto esperado no artigo

Com essa rodada, a secao de experimentos deixara de sustentar apenas uma demonstracao de viabilidade e passara a oferecer evidencia comparativa sobre qualidade de recuperacao, qualidade de geracao, contribuicao relativa dos componentes do pipeline e confiabilidade dos metodos de avaliacao. Isso aumenta a chance de enquadrar o trabalho como contribuicao metodologica reprodutivel para sistemas RAG em acervos legislativos, em vez de apenas como relato de implementacao.

## Observacao editorial

Este plano nao exige executar novos testes imediatamente. Ele deve orientar a proxima rodada empirica e impedir que o manuscrito seja ajustado de modo fragmentado antes de haver uma base experimental mais completa. Depois da execucao, sera necessario revisar resumo, introducao, metodologia, experimentos, discussao, conclusao, declaracoes de ciencia aberta e artefatos publicos.
