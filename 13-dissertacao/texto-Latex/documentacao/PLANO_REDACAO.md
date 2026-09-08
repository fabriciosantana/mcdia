# Plano de redação e pesquisa

Estado do corpus conferido em 6 de setembro de 2026, a partir da inspeção dos arquivos, das saídas salvas do notebook 01, da conferência direta do Parquet e da compilação do rascunho. A análise exploratória completa não foi reexecutada nessa conferência.

Legenda: `[x]` concluído no escopo indicado; `[~]` parcialmente concluído; `[ ]` pendente. As ações abaixo não representam aprovação de mudanças nas hipóteses ou no recorte do corpus.

## Estado atual e numeração

O documento contém nove seções principais, na ordem de inclusão em `main.tex`. Os prefixos dos arquivos preservam a organização anterior e não correspondem integralmente à numeração do documento.

| Seção | Arquivo em `capitulos/` | Estado identificado |
|---|---|---|
| 1. Introdução | `01-introducao.tex` | Texto desenvolvido, com pergunta e seis objetivos específicos; alinhamento final e sustentação da lacuna pendentes. |
| 2. Referencial teórico | `02-referencial-teorico.tex` | Texto desenvolvido e atualizado com oito fontes adicionais; revisão de coerência final pendente. |
| 3. Trabalhos relacionados | `03-trabalhos-relacionados.tex` | Comparação crítica inicial redigida com as fontes prioritárias e três referências de apoio; quadro comparativo auditável e revisão final pendentes. |
| 4. Hipóteses do estudo | `04-hipoteses-de-trabalho.tex` | H1, H2 e H3 formuladas e operacionalizadas; dimensionamento amostral e execução pendentes. |
| 5. Metodologia | `04-procedimentos-metodologicos.tex` | Constituição e análise do corpus descritas como realizadas; etapas experimentais planejadas. |
| 6. Artefato e caso empírico | `05-artefato-e-caso-empirico.tex` | Estrutura com `TODO`; já há evidências para redigir a caracterização do corpus. |
| 7. Resultados | `06-resultados.tex` | Estrutura com `TODO`; depende da execução experimental final. |
| 8. Discussão | `07-discussao.tex` | Estrutura com `TODO`; depende dos resultados e de sua interpretação. |
| 9. Considerações finais | `08-consideracoes-finais.tex` | Estrutura com `TODO`; depende das contribuições efetivamente demonstradas. |

## Próxima entrega: revisão da literatura (atualização de 08/09/2026)

- [x] Preparar fichamentos das 45 fontes acessíveis/consultadas, com uma página por referência, recorte de leitura, excertos localizados e análise crítica. Coleção em `../../fichamentos/out/main.pdf`; conteúdo editável em `../../fichamentos/fichas/`.
- [x] Expandir matriz temática e síntese de trabalho para a coleção; manter inventário das 52 entradas e proveniência das fontes.
- [~] Completar a cobertura: sete referências dependem de acesso ou confirmação de versão, descritas em `../../fichamentos/documentacao/CONTROLE_COBERTURA.md`. Fichamento focal não atesta leitura integral nem leitura do pesquisador.
- [~] Revisar as fichas com o pesquisador e aprofundar métodos/resultados das fontes centrais. Auditoria editorial concluída; falta a conferência substantiva final pelo pesquisador.
- [~] Resolver divergências de versões e metadados antes de atualizar `referencias.bib`; as cinco fontes prioritárias já foram verificadas e incorporadas, mas as demais divergências permanecem.
- [x] Incorporar as cinco fontes prioritárias aos capítulos 2 e 3 e registrar a busca complementar; não inferir lacuna apenas da seleção existente.
- [x] Incorporar GroUSE, eRAG e o survey de Yu et al. como referências de apoio; mantidas como condicionais apenas as fontes contextuais ou fora do protocolo atual (ParlaMint-PT, ObliQA-MP e MIRAGE).

A entrega bibliográfica é a prioridade imediata indicada pelo pesquisador. As etapas do corpus e do experimento abaixo permanecem necessárias.

## Sequência proposta para retomada

1. Redigir a caracterização do corpus na seção 6, com base nas evidências verificadas, explicitando casa legislativa, tipos de autor, cobertura textual e proveniência.
2. Recuperar a execução integral do notebook 01 e conferir novamente os artefatos derivados.
3. Desenvolver o quadro de trabalhos relacionados e documentar a sustentação da lacuna.
4. Fechar os critérios das hipóteses e o protocolo experimental antes de implementar e executar o notebook 02.
5. Redigir resultados, discussão e considerações finais conforme as evidências forem produzidas.

## Fase 1 — consolidação do desenho

- [~] Conferir metadados institucionais. Título, subtítulo e orientador (Prof. Dr. Marcelo Rodrigo de Souza Pita) estão preenchidos em `config/dados.tex`, assim como o ano de 2027; área, linha de pesquisa, data de defesa e banca permanecem pendentes. Preenchimento não equivale à confirmação do calendário.
- [~] Revisar alinhamento entre pergunta, objetivo geral, seis objetivos específicos, hipóteses e matriz metodológica. A metodologia distingue etapas realizadas e planejadas; o alinhamento final depende do protocolo e da avaliação humana.
- [x] Definir, para H1, H2 e H3, observações necessárias, medidas e regras de interpretação. Foram operacionalizados os contrastes de recuperação/verificabilidade, complexidade e concordância humano--LLM, preservando a possibilidade de qualificação por categoria.
- [ ] Explicitar como a construção e a avaliação do protocolo concretizam o enquadramento em Design Science Research, retomando a observação do orientador.
- [ ] Explicitar os critérios de inclusão do corpus: há 14.438 registros com `Casa = Senado Federal` e 1.291 com `Casa = Congresso Nacional`; por tipo de autor, são 13.290 registros de senadores, 365 de deputados e 2.074 de autores externos. Não excluir registros nem alterar o recorte sem decisão documentada.
- [ ] Distinguir período consultado (01/02/2019 a 31/01/2023) e intervalo observado dos registros (01/02/2019 a 10/01/2023).
- [~] Definir a versão final do protocolo, os baselines e os critérios de sucesso. BM25, recuperação vetorial e híbrida já estão previstos; faltam configurações, quantidade e distribuição das perguntas, regras de relevância e tratamento das perguntas não respondíveis.
- [ ] Definir uma referência de avaliação que permita comparação justa entre diferentes segmentações, preservando a ligação entre evidência, trecho e pronunciamento.
- [~] Definir rubrica, plano e dimensionamento da avaliação humana, piloto, independência dos julgamentos, tratamento de divergências e análise de concordância. A rubrica 0--2, as cinco dimensões e o piloto estão definidos; faltam dimensionar a amostra e recrutar os avaliadores.
- [x] Atualizar e documentar a revisão de literatura. Há 53 fichamentos, matriz temática, síntese e quadro comparativo; permanecem pendentes a revisão com o pesquisador e o aprofundamento dos estudos centrais.

## Fase 2 — congelamento e execução

- [x] Conferir a identidade binária e os totais básicos do corpus local. O SHA-256 corresponde ao registrado em `DECISOES.md`: `e09cfc4793e5394be440906320c7d3008cda5a52b90bbc85bf47446362406af1`. Foram confirmados 15.729 registros únicos, 30 colunas, 15.039 textos integrais, 687 resumos substitutos e três registros sem conteúdo utilizável.
- [~] Consolidar a análise exploratória do notebook 01. Existem saídas salvas e tabelas exportadas, mas a versão atual contém `HF_TOKEN=` sem valor, impedindo sua execução integral; as saídas anteriores não comprovam a execução do código atual.
- [ ] Corrigir a célula de carregamento e compatibilizar a procura local com `dados/data/full/discursos_2019-02-01_2023-01-31.parquet`, sem inserir credenciais no código.
- [ ] Registrar versões das dependências e reexecutar integralmente o notebook 01, conferindo tabelas e notas com as novas saídas.
- [ ] Refinar a interpretação da cobertura de partido e UF: as 2.074 ausências coincidem com autores externos; ambos os campos estão preenchidos entre senadores e deputados. Distinguir ausência e possível não aplicabilidade antes de caracterizar deficiência dos metadados ou revisar o quadro de prontidão.
- [ ] Conferir a proveniência e a necessidade dos dois CSVs de prontidão atualmente idênticos: `prontidao_rag.csv` e `prontidao_dados_experimentacao_rag.csv`.
- [ ] Implementar o notebook 02, atualmente apenas planejado, com construção efetiva de trechos e comparação da recuperação. As estimativas de chunking do notebook 01 não são resultados experimentais.
- [ ] Congelar código experimental, configurações, perguntas e conjunto de referência. O congelamento do corpus não encerra o congelamento do experimento.
- [ ] Registrar versões, hashes, modelos, prompts, parâmetros, sementes aplicáveis e datas das execuções experimentais.
- [ ] Executar piloto e registrar mudanças previamente ao experimento principal.
- [ ] Executar recuperação e baselines sob os mesmos dados, perguntas e critérios de relevância; posteriormente executar geração e avaliações, mantendo as camadas analíticas separadas.
- [ ] Concluir avaliação humana e análise de concordância.

## Fase 3 — capítulos empíricos

- [x] Fechar a seção 3 (Trabalhos relacionados) com quadro comparativo inicial por corpus/domínio, foco de avaliação e transferência para o Senado; revisar e ampliar os campos na versão final.
- [~] Atualizar a seção 5 (Metodologia) conforme os procedimentos forem efetivamente realizados. Constituição e análise exploratória do corpus já foram incorporadas; conferir a reprodução do notebook e preservar o caráter prospectivo das etapas experimentais.
- [ ] Redigir a caracterização do corpus na seção 6 (Artefato e caso empírico), sem duplicar a descrição dos procedimentos metodológicos.
- [ ] Completar a seção 6 com arquitetura, preparação documental, configuração final e evolução em relação à prova de conceito, usando apenas configurações confirmadas.
- [ ] Apresentar observações, inclusive negativas, na seção 7 (Resultados), com base na execução final congelada.
- [ ] Interpretar achados, hipóteses e ameaças à validade na seção 8 (Discussão), distinguindo evidência técnica e implicações institucionais.
- [ ] Responder à pergunta e aos objetivos na seção 9 (Considerações finais), limitando as contribuições ao que tiver sido demonstrado.
- [ ] Preencher os apêndices com protocolo, bateria e conjunto de referência, rubrica e instrumentos finais.

## Fase 4 — fechamento

- [~] Redigir resumo e abstract depois de concluir os capítulos. O resumo atual é provisório e não apresenta resultados; o abstract permanece como marcador de redação.
- [x] Conferir as chaves bibliográficas da versão inspecionada: 52 entradas, 44 chaves citadas, nenhuma chave citada ausente e nenhuma chave duplicada. As oito entradas não citadas permanecem como material bibliográfico disponível.
- [~] Verificar externamente metadados bibliográficos e suporte das citações às afirmações. Auditoria dos capítulos 2 e 3 concluída; permanecem confirmações editoriais das referências metodológicas pendentes. A conferência de chaves não valida existência, conteúdo ou atualidade das fontes.
- [ ] Preencher ficha catalográfica e dados de banca.
- [~] Conferir o atendimento às anotações do orientador. Já existem diagrama de componentes, data na fonte da figura, lista de siglas e distinção entre `top-k` e `top-p`; permanece pendente a conferência integral das intervenções e de sua justificativa.
- [ ] Revisar figuras, tabelas, quadros, fontes e chamadas no texto; incluir o parágrafo introdutório da seção 1 antes da primeira subseção, conforme a regra editorial local.
- [ ] Sincronizar as referências à numeração e ao estado editorial em `MAPA_FONTES.md` e `AGENTS.md`; este plano passa a usar a ordem atual de `main.tex`, sem renomear os arquivos.
- [x] Compilar o rascunho inspecionado: `latexmk -pdf main.tex` gerou `out/main.pdf` com 47 páginas e sem referências indefinidas no log final.
- [ ] Tratar os avisos remanescentes de diagramação (`Overfull hbox`) e de localização do `biblatex` (`brazilian-abnt-abnt.lbx`), respeitando a regra de não alterar `idp.cls`, e conferir visualmente o PDF.
- [ ] Compilar com a opção `entrega` e ler o PDF integralmente.
