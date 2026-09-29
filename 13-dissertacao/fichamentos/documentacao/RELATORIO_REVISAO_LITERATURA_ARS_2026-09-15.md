# Relatório de revisão da literatura — fluxo `ars-lit-review`

**Data:** 15/09/2026  
**Escopo:** dissertação sobre avaliação de sistemas RAG aplicados a discursos parlamentares brasileiros.  
**Corpus de trabalho:** `fichamentos/dados/inventario-completo.csv`, `fichamentos/fichas/*.tex`, capítulos 2 e 3 e a auditoria de 08/09/2026.

## 1. Resultado executivo

A literatura selecionada é adequada para o piloto e cobre quatro necessidades centrais do protocolo: fundamentos de RAG e recuperação; avaliação de geração e grounding; aplicações jurídico-parlamentares; e contexto institucional dos acervos legislativos. O inventário consolidado contém 60 referências: 52 provenientes do pré-projeto e oito incorporadas na busca complementar posterior. Há 58 fichamentos disponíveis e duas referências formalmente não incorporadas por falta de acesso.

A lacuna está formulada de modo defensável como **integração e adaptação contextual**: os estudos existentes oferecem técnicas ou aplicações parciais, mas não combinam, no mesmo desenho empírico, corpus parlamentar brasileiro, recuperação documental, geração, verificabilidade das citações, reconhecimento de insuficiência documental e validação humana independente.

O conjunto ainda não deve ser descrito como revisão sistemática exaustiva. O repositório documenta seleção, fichamento e auditoria, mas não preserva contagens de resultados por base de dados nem um protocolo prospectivo de busca com data e strings executadas em cada fonte. A formulação apropriada é **revisão estruturada da literatura com busca complementar e análise de cobertura**.

## 2. Estratégia e critérios registrados

### Pergunta orientadora

Em que condições um sistema RAG aplicado a discursos parlamentares brasileiros recupera evidências pertinentes, produz respostas verificáveis e reconhece insuficiência documental?

### Conceitos de busca

- RAG, retrieval-augmented generation, avaliação de RAG e LLM-as-a-judge;
- recuperação da informação, recuperação neural, embeddings, reranqueamento e grounding;
- alucinação, suporte de citação, atribuição, deflexão e perguntas não respondíveis;
- informação legislativa, discurso parlamentar, parlamento, Senado e aplicações jurídico-políticas;
- transparência, accountability, supervisão humana e governança de IA.

### Critérios de inclusão aplicados na prática

Foram mantidos trabalhos diretamente relacionados a pelo menos um componente do problema: arquitetura ou recuperação RAG; métrica, benchmark ou rubrica de avaliação; aplicação jurídico-legislativa/parlamentar; corpus de discurso parlamentar; ou fundamento metodológico usado no desenho da dissertação. Fontes fundacionais foram preservadas quando necessárias para a linhagem conceitual, mesmo sendo anteriores ao recorte recente.

Foram incorporadas, com ressalvas de versão, Geunis, de Almeida Santos, Gil, Lakatos/Marconi e Peffers. `matoshiEtAl2025parliamentRag` e `creswellPlanoClark2018mixedMethods` permanecem formalmente não incorporadas por falta de acesso.

### Limitação de rastreabilidade

O inventário permite reproduzir a seleção final e suas justificativas, mas não permite reconstruir um número de “resultados iniciais” por base. Esse campo deve ser preenchido somente se novas buscas forem executadas; não se deve inventar contagens retrospectivas.

## 3. Triagem e cobertura

| Estado | Quantidade | Interpretação |
|---|---:|---|
| Fichado — consulta focal/parcial | 50 | Ficha produzida a partir do recorte consultado; não equivale a leitura integral |
| Incorporado — fichas 46–53 e 54–58 | 8 | Fontes complementares pós-pré-projeto, centradas em avaliação de RAG |
| Não incorporado — acesso não obtido | 2 | Não usar como sustentação principal até resolver a pendência |
| **Total do inventário** | **60** | 52 do pré-projeto + 8 complementares |

### Aviso de distribuição temporal

**DISTRIBUTIONAL_SKEW_ADVISORY**

- **Dimensão:** distribuição temporal.
- **Concentração:** 2024–2025 = 31/60 referências (51,7%); 2023–2025 = 39/60 (65%).
- **Interpretação:** há concentração recente, mas ela não alcança o limiar de 70% para um alerta forte. Ela é compatível com a rápida evolução da avaliação de RAG.
- **Resposta de busca:** manter fontes fundacionais de 2004–2021 e não ampliar a busca temporal sem uma lacuna conceitual específica.

Não foi emitido alerta quantitativo para geografia, método ou estrato de venue porque esses metadados não estão completos e não devem ser inferidos a partir dos títulos ou da afiliação aparente.

## 4. Bibliografia anotada e matriz temática

As anotações individuais estão nas 58 fichas em `fichamentos/fichas/`. Cada ficha registra contribuição, resumo extrativo, limitações e uso proposto. A matriz abaixo consolida a função das fontes no argumento; “alta” significa boa adequação ao claim indicado, não uma classificação universal de prestígio.

| Grupo de fontes | Fontes representativas | Tema/claim coberto | Método ou evidência | Adequação |
|---|---|---|---|---|
| Fundamentos de RAG | Lewis et al.; Gao et al.; Gao et al.; Gupta et al. | Arquitetura, pipeline e dependência entre recuperação e geração | Artigo fundacional, surveys e revisão técnica | Alta para definição e delimitação |
| Recuperação | Manning et al.; Karpukhin et al.; Thakur et al.; Nie et al. | Pertinência, recuperação densa, embeddings e benchmarks | Livro, benchmark e surveys | Alta para métricas e desenho do pipeline |
| Avaliação geral | ARES; RAGAS; RAGEval; HELM | Separação entre recuperação, geração, correção e completude | Frameworks e benchmarks | Alta, com calibração local |
| Grounding e alucinação | Trautmann et al.; RAGTruth; GaRAGe; Ji et al. | Fidelidade ao contexto, erro em nível de afirmação e recusa | Benchmarks anotados e survey | Alta para a rubrica e análise de erros |
| Verificabilidade | Zhang et al.; LegalBench-RAG; eRAG | Suporte graduado de citações e utilidade downstream | Benchmark jurídico e métodos de avaliação | Alta, sem reduzir verificabilidade à presença de citação |
| Meta-avaliação | ConsJudge; GroUSE; G-Eval | Consistência e limites de LLM-as-a-judge | Estudos de juiz e testes unitários | Alta para comparar juiz e avaliadores humanos |
| Recuperação em nível de documento | Reuter et al. | Mismatch entre documento correto e trecho semanticamente próximo | Estudo empírico jurídico | Alta como hipótese de erro a testar |
| Aplicações jurídico-políticas | RAGAR; LexDrafter; Talk to the NDAA; KamerRaad; LegisSearch; World Avatar | Variedade de tarefas, corpora e arquiteturas | Sistemas aplicados e demonstrações | Média: contextualiza, mas não forma benchmark comum |
| Parlamento e discurso | Skubic/Fiser; Blanco; Martello/Viola; Bandeira/Bernardes | Natureza do acervo, organização e uso institucional | Revisão, estudo de corpus e organização do conhecimento | Alta para contextualização brasileira/institucional |
| Governança | IPU; WFD; Bender et al.; Bommasani et al. | Transparência, supervisão, riscos sociotécnicos | Diretrizes e textos conceituais | Média/alta para justificativa institucional |
| Desenho de pesquisa | Hevner et al.; Peffers et al.; Gil; Lakatos/Marconi | DSR, projeto, métodos e desenho metodológico | Textos metodológicos | Alta para desenho; versões consultadas têm ressalvas |

## 5. Lacunas identificadas

1. **Integração de dimensões:** os trabalhos frequentemente isolam recuperação, geração, atribuição ou recusa; faltam protocolos que as avaliem juntas em um acervo parlamentar real.
2. **População e idioma:** a maior parte dos benchmarks é geral, jurídica em inglês ou voltada a outra jurisdição. O Senado brasileiro e o português parlamentar permanecem pouco representados.
3. **Unidade de avaliação:** respostas inteiras podem esconder erro de documento, trecho, afirmação ou citação. A dissertação precisa registrar essas unidades separadamente.
4. **Insuficiência documental:** benchmarks recentes tratam deflexão e recusa, mas a adaptação a perguntas legislativas não respondíveis ainda precisa ser operacionalizada e validada localmente.
5. **Validação do avaliador:** correlação agregada de um juiz não garante detecção de contradição, falta de evidência ou irrelevância. A comparação com avaliação humana e testes de casos-limite é necessária.
6. **Reprodutibilidade institucional:** aplicações jurídico-parlamentares usam corpora, metadados e tarefas heterogêneos; ainda falta um protocolo que explicite corpus, jurisdição, pergunta, recuperação, geração, citação e participação humana em conjunto.

Essas lacunas são inferências de cobertura do corpus selecionado e dos capítulos, não afirmações de que nenhuma outra publicação exista. A redação deve manter “escassez” ou “pouca integração”, evitando “inexistência”.

## 6. Uso recomendado por seção da dissertação

| Seção | Fontes prioritárias | Função |
|---|---|---|
| Referencial teórico: LLM/RAG | Vaswani; Lewis; Gao; Gupta; Manning; Karpukhin; Thakur | Definir arquitetura, recuperação e pipeline |
| Referencial teórico: acervo legislativo | Bandeira/Bernardes; Skubic/Fiser; Blanco; Martello/Viola; IPU; WFD | Justificar especificidade institucional e parlamentar |
| Referencial teórico: avaliação | ARES; RAGAS; RAGEval; HELM; Yu; Ji | Delimitar dimensões, métricas e riscos |
| Trabalhos relacionados | Trautmann; RAGTruth; Zhang; GaRAGe; Reuter; eRAG; GroUSE; ConsJudge; LegalBench-RAG | Comparar unidade, tarefa, grounding, recusa e avaliação humana |
| Metodologia | Hevner; Peffers; Gil; Lakatos/Marconi | Sustentar o desenho e a documentação, com as edições consultadas explicitadas |
| Discussão | Toda a matriz, com ênfase em Trautmann, GaRAGe, Reuter e GroUSE | Interpretar transferibilidade, limites e casos-limite |

## 7. Decisões editoriais e próximos passos

- **Concluído nesta rodada:** revisar os capítulos 2 e 3; não há chaves ausentes nem citações das três referências contextuais não verificadas.
- Não transformar a rubrica de cinco dimensões em “padrão da literatura”. Apresentá-la como síntese operacional, com a dimensão de insuficiência documental explicitamente adaptada ao contexto parlamentar.
- Nas fontes centrais, conservar qualificadores como “nas condições do estudo” para números de Trautmann, GaRAGe, ARES e demais benchmarks.
- **Concluído nesta rodada:** aprofundar ARES, RAGAS, ConsJudge, LegalBench-RAG, Trautmann, RAGTruth, Zhang, GaRAGe e Reuter; as fichas agora registram controle explícito de uso e limites de transferência.
- Manter Matoshi e Creswell registrados como não incorporados. Conferir na redação final as ressalvas de edição de Gil, Lakatos/Marconi e Geunis.
- Se uma nova rodada de busca for realizada, registrar data, base, string, filtros, resultados iniciais e motivo de inclusão/exclusão; anexar os resultados ao inventário em vez de substituir silenciosamente o corpus atual.

## 8. Julgamento do fluxo ARS

**Cobertura temática:** adequada para o piloto, com lacunas nomeadas.  
**Estratégia reproduzível:** parcial; a seleção final é rastreável, mas faltam logs prospectivos de bases e contagens de busca.  
**Bibliografia anotada:** adequada para as 58 fichas existentes.  
**Matriz de literatura:** adequada em nível temático; pode ser refinada depois da leitura integral das fontes centrais.  
**Prontidão para redação:** suficiente para consolidar o piloto e a revisão dos capítulos; insuficiente para declarar revisão exaustiva ou fechar a versão final sem resolver as pendências metodológicas e de acesso.
