# Pesquisa bibliográfica adicional

Data da busca: 08/09/2026. A pesquisa foi conduzida para avaliar se a revisão sobre avaliação de RAG em discursos parlamentares do Senado Federal precisa de referências além das 52 entradas já selecionadas. O escopo foi delimitado pela pergunta da dissertação: como organizar e aplicar técnicas para avaliar recuperação documental, geração de respostas e verificabilidade das fontes em um acervo legislativo brasileiro?

## Estratégia e critérios

Foram consultados registros primários da ACL Anthology e páginas oficiais de arXiv. As buscas combinaram os termos `RAG evaluation`, `faithfulness`, `groundedness`, `citation`, `legal RAG`, `parliamentary corpus` e `LLM-as-a-judge`, restringindo a resultados de 2024–2025 quando havia literatura recente. Foram priorizados artigos com benchmark, corpus anotado, método de avaliação ou aplicação jurídica/parlamentar diretamente comparável. Foram excluídos textos apenas opinativos, duplicatas das fichas existentes e trabalhos cujo único vínculo fosse mencionar LLMs.

Os PDFs de onze fontes foram baixados e extraídos localmente; hashes e URLs estão em `adicionais/obtencao.json`. A leitura foi focal, concentrada em resumo, método, resultados e limitações. Isso é triagem bibliográfica e não declaração de leitura integral pelo pesquisador.

## Recomendação executiva

Há bibliografia adicional que merece entrar na revisão. Recomendo incorporar primeiro os cinco itens com relação direta ao protocolo da dissertação:

1. **Trautmann et al. (2024)** — benchmark de groundedness em perguntas e respostas jurídicas, comparando similaridade, NLI e LLMs; o melhor método alcança macro-F1 de 0,80 nas condições do estudo. É a ponte mais direta para a rubrica de fidelidade ao contexto em domínio de alto risco.
2. **Niu et al. (2024), RAGTruth** — corpus de quase 18 mil respostas RAG anotadas em nível de caso e de palavra, com intensidade de alucinação. Oferece uma taxonomia operacional e exemplos para a análise de erros, embora seus domínios e idiomas não sejam parlamentares.
3. **Zhang et al. (2024)** — mostra que suporte de citação precisa ser graduado em completo, parcial e ausente; nenhum avaliador automático domina todas as tarefas de correlação, classificação e recuperação. Recomendo para justificar que “tem citação” não basta como verificabilidade.
4. **Sorodoc et al. (2025), GaRAGe** — 2.366 perguntas e mais de 35 mil passagens anotadas; avalia grounding relevante e recusa quando não há evidência suficiente. Os resultados reportam, nas condições do benchmark, no máximo 60% de factualidade sensível à relevância, 58,9% de F1 de atribuição e 31% de taxa de verdadeiros positivos em deflexões. É especialmente útil para perguntas não respondíveis e insuficiência documental.
5. **Reuter et al. (2025)** — identifica *Document-Level Retrieval Mismatch* em grandes bases jurídicas e testa *Summary-Augmented Chunking*. Ajuda a fundamentar a avaliação de erros de recuperação no nível do documento, que não aparece com clareza suficiente nas referências atuais.

Recomendo incorporar em seguida, conforme espaço e desenho final:

- **Muller et al. (2025), GroUSE**: 144 testes unitários para avaliar avaliadores de respostas fundamentadas; alerta que correlação com GPT-4 é proxy incompleto e que juízes abertos podem não generalizar.
- **Salemi e Zamani (2024), eRAG**: avalia cada documento recuperado pelo desempenho downstream, aproximando a utilidade de uma passagem para a tarefa; relevante para ligar recuperação e geração, mas ainda preprint e limitado a três conjuntos.
- **Yu et al. (2024)**: survey de avaliação de RAG; bom mapa de métricas e benchmarks, mas deve permanecer apoio secundário às fontes primárias.

## Referência contextual, sem prioridade imediata

**Aires et al. (2024), ParlaMint-PT** descreve um corpus parlamentar português de 2015–2022, com codificação XML, metadados e anotação. É útil para comparar práticas de construção de corpus parlamentar em língua portuguesa, mas não é evidência de desempenho de RAG nem substitui documentação específica do Senado brasileiro.

**Gokhan e Briscoe (2025), ObliQA-MP** também é relevante para perguntas que exigem múltiplas passagens regulatórias, mas sua base é sintética e regulatória. Pode ser citada como analogia metodológica, desde que não seja apresentada como evidência parlamentar.

**Qi et al. (2024), MIRAGE** trata de atribuição de respostas com base em sinais internos do modelo. É tecnicamente interessante para verificabilidade, porém mais complexo que o protocolo previsto e não deve ser adicionado sem decisão de incorporar atribuição em nível de token.

## O que muda na lacuna

A seleção anterior já cobria RAGAS, ARES, G-Eval, ConsJudge, RAGEval, LegalBench-RAG, recuperação densa, benchmarks gerais e aplicações legislativas. A busca nova acrescenta três dimensões que estavam sub-representadas:

1. **Grounding jurídico com classificação validada**: Trautmann et al. permitem discutir detecção de trechos não sustentados em respostas jurídicas.
2. **Evidência e recusa em nível fino**: RAGTruth, GaRAGe e Zhang et al. sustentam anotações por afirmação, passagem e grau de suporte.
3. **Falha documental antes da geração**: Reuter et al. e eRAG ajudam a separar erro de documento recuperado, erro de passagem e erro de geração.

Com isso, a lacuna pode ser formulada de modo mais preciso: ainda há pouca evidência de um protocolo que combine, no mesmo acervo parlamentar brasileiro, avaliação da recuperação no nível do documento e do trecho, verificação de suporte por afirmação, tratamento explícito de insuficiência documental e validação humana independente. A lacuna não deve ser formulada como ausência de qualquer benchmark de groundedness ou de qualquer aplicação jurídica.

## Decisão sugerida para a bibliografia

Os nove registros recomendados estão em `bibliografia-adicional-candidata.bib`, separados do arquivo principal para revisão editorial. Sugiro adicionar primeiro Trautmann, Niu, Zhang, Sorodoc e Reuter às referências da dissertação e citá-los nos capítulos 2 (referencial teórico), 3 (trabalhos relacionados) e 4 (procedimentos metodológicos), após conferência das versões. Os demais podem permanecer como referências de apoio ou entrar quando o protocolo efetivamente utilizar suas ideias.

Não alterei `texto-Latex/referencias.bib` nem inseri citações no manuscrito, porque a decisão de incorporar uma fonte na argumentação deve seguir a revisão do pesquisador e a confirmação da versão bibliográfica escolhida.

## Limitações da busca

Esta foi uma busca orientada por lacunas e não uma revisão sistemática PRISMA. A ACL Anthology e o arXiv favorecem literatura de NLP; a busca não cobre exaustivamente bases de administração pública, ciência política ou bibliotecas brasileiras. Os resultados não demonstram ausência de outros trabalhos. A seleção deve ser atualizada antes da versão final, especialmente para fontes publicadas após 2025 e para estudos em português.
