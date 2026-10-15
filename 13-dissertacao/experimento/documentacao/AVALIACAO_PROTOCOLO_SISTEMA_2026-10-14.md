# Avaliação da dissertação e do sistema experimental

## Material Passport

- Data: 2026-10-14.
- Tipo: diagnóstico interno de aderência e planejamento; análise inline, sem painel independente.
- Base: commit `3690b1111aa0ca2282bb75e6717350e2a4e9862d`, texto LaTeX, código, specs e consulta somente de leitura ao SQLite local.
- Escopo: capítulos incluídos por `texto-Latex/main.tex`, protocolo H1–H3 e fluxo operacional. Não é auditoria das fontes bibliográficas nem validação empírica das hipóteses.
- Verificação: inspeção de código, 19 testes existentes, 11 specs e reproduções sintéticas. Nenhuma chamada a modelo externo ou execução científica real.
- Resultado: protótipo funcional parcial; ainda não pronto para produzir a evidência final da dissertação.

## 1. Avaliação do texto

A introdução, o referencial e os trabalhos relacionados estabelecem uma contribuição coerente: organizar um protocolo integrado para recuperação, geração e verificabilidade em discursos parlamentares brasileiros. O sistema deve servir a esse protocolo; não é necessário transformar a pesquisa em comparação abrangente de arquiteturas ou implantação pública.

A separação das cinco dimensões e das unidades documento, trecho e afirmação está explicitada. A operacionalização H1–H3 permite derivar telas, entidades e relatórios concretos. Os capítulos de artefato, resultados, discussão e conclusão ainda contêm tarefas editoriais; isso é compatível com a etapa de qualificação, mas não caracteriza dissertação empírica concluída.

Pontos a resolver antes do congelamento do protocolo:

1. **H1:** observar casos com recuperação suficiente e resposta não verificável demonstra insuficiência da recuperação como garantia. Observar falhas nas duas camadas não prova uma condição necessária universal. Uma ocorrência na célula recuperação não pertinente/resposta verificável deve ser examinada como contraexemplo ou problema de definição. Separar verificabilidade perante o corpus, perante o contexto efetivamente fornecido e existência formal de citação. Registrar a decisão conceitual do pesquisador.
2. **H2:** explicitar as três comparações principais e o mapeamento das 12 categorias para grupos. Categorias e respondibilidade podem se sobrepor: escolher regra de associação e tratamento da dependência. Hit@5 para perguntas sem evidência de referência não deve ser calculado como zero; registrar não aplicável e analisar reconhecimento de insuficiência separadamente. Dois casos por categoria no piloto servem à calibração, não garantem precisão inferencial.
3. **H3:** alinhar a metodologia, que enfatiza acordo exato e divergências, à seção de hipóteses, que inclui kappa ponderado. Fixar pesos, unidade de pareamento, número de rodadas, tratamento de desacordo entre humanos e regra para amostras constantes. Os intervalos 0,40–0,75 e 10% são regras propostas no texto; precisam de justificativa e aprovação prévia, não de confirmação pelo software.
4. **Respondibilidade parcial:** o banco usa sim/parcial/não, enquanto a operacionalização é binária. Conservar a classificação original e definir uma decisão curatorial explícita, com limites da resposta esperada; não converter silenciosamente.
5. **Segmentação:** o texto exige tokenizador do modelo e comparação de janelas. O código usa `\S+`, isto é, unidades separadas por espaço, sob o rótulo “tokens”. Os 94.360 chunks com 160/32 são uma preparação técnica provisória, diferente da estimativa exploratória 512/64. Não substituem o protocolo de segmentação final.
6. **Temporalidade editorial:** a metodologia ainda diz que perguntas/chunks serão construídos no notebook 02. Existem agora catálogo e preparação no aplicativo, porém sem validação científica. Atualizar essa distinção depois das entregas e preservar o notebook como análise complementar, se desejado.
7. **Corpus:** preservar a separação entre texto integral e resumo substituto, exigida no texto, e a cobertura dos metadados de ano, tamanho, partido, UF e tipo de fonte. A ingestão atual não preserva tudo isso.
8. **Quadro de trabalhos relacionados:** consolidar a matriz prometida ao fim do capítulo 3, com idioma, tarefa, corpus, avaliação humana e limites de transferência. Descrições de estudos e números reportados não foram revalidados nesta auditoria.

O texto LaTeX não foi alterado: as decisões metodológicas acima ficam explícitas para deliberação antes da coleta final.

## 2. Estado constatado

| Item | Estado em 14/10/2026 |
|---|---|
| Perguntas no SQLite | 200, todas rascunho |
| Respondibilidade importada | 107 sim, 78 parcial, 15 não; todos os 200 registros têm `respondible=1` |
| Documentos com chunks | 15.726 (preparação previamente registrada) |
| Chunks no SQLite | 94.360 |
| Execuções / respostas / avaliações humanas / juiz | 0 / 0 / 0 / 0 |
| Perfis | 0 |
| Chroma local | arquivo `data/embeddings/chroma/chroma.sqlite3` ausente; suporte implementado, índice real não construído |
| Testes existentes | 19 aprovados; avisos de conexões SQLite não fechadas e depreciação |
| OpenSpec existente | 11 specs válidas sintaticamente |

Esses números descrevem o ambiente local, não resultados científicos nem conteúdo publicado no Git. Passar nos testes atuais e no validador OpenSpec não comprova aderência completa ao protocolo.

## 3. Matriz de lacunas e evidências

Caminhos abaixo relativos a `experimento/`, exceto os capítulos em `../texto-Latex/capitulos/`.

| ID | Requisito do texto/usuário | Evidência no sistema | Risco / prioridade | Entrega |
|---|---|---|---|---|
| L01 | Recall e Hit distintos; nDCG graduado | `retrieval.py::_metrics` calcula Recall pela primeira evidência; IDCG usa `[1]` quando não há graus | Resultado incorreto, P0 | E3 |
| L02 | Bateria incluindo não respondíveis | `question_bank.py::save_catalog_question` usa `bool('0')`; checkbox “Utilizável” representa respondibilidade | Erro de construto, P0 | E2 |
| L03 | Curadoria auditável e conjunto de referência | dashboard não envia graus nem categorias secundárias ao salvar; salvamento os zera; validação só verifica texto/categoria/status | Perda de anotação, P0 | E2 |
| L04 | Comparar segmentações sem perder evidências | `corpus.py::prepare_documents` apaga por hash e usa `documento:posição` sem versão; fonte alterada com mesmo ID pode colidir | Evidências órfãs ou substituídas, P0 | E1 |
| L05 | Corpus e metadados institucionais | ingestão usa resumo como fallback sem marcar fonte textual; preserva apenas quatro metadados | Estratificação e suficiência comprometidas, P0 | E1 |
| L06 | Gestão SQLite e fluxo sem arquivos | recuperação e geração ainda recebem JSONL; geração pode usar outro arquivo e ignora IDs ausentes | Contexto irreproduzível, P0 | E1/E4 |
| L07 | BM25, vetorial e híbrida | `rank_documents` combina BM25 com TF-IDF; calcula ambos mesmo em execução só BM25 | Comparação mal identificada e desperdício, P0 | E3 |
| L08 | Índice persistente reprodutível | Chroma guarda vetores, mas busca usa matriz completa NumPy; primeiro carregamento não remapeia retorno por ID; exceção genérica leva a tentativa de exclusão da coleção | Risco de atribuição e reindexação, P0 | E3 |
| L09 | Parâmetros e rastreabilidade | `k=10` fixo; perfil aplica essencialmente método; gerador guarda hash, sem prompt completo/temperatura/top-p/uso | Configuração nominal diferente da efetiva, P0 | E4 |
| L10 | Julgar aderência, completude e citações | `judge_response` recebe apenas resposta, não pergunta/contexto; grava hash da geração como se fosse do juiz | Julgamento sem evidência, P0 | E5 |
| L11 | Verificabilidade por afirmação | geração registra chunk como `document_id`, `chunk_id` ausente; não há afirmações e suporte graduado | H1 não operacionalizada, P0 | E4/E5 |
| L12 | Humanos independentes e calibrados | tela mostra modelo e avaliações anteriores; avaliador é texto livre; sem amostragem, rodadas ou adjudicação | Independência não assegurada, P0 antes da avaliação | E5 |
| L13 | Pareamento humano–juiz e H3 | join cru multiplica avaliações/rodadas; kappa constante retorna 1 | Pseudorreplicação e acordo indefinido apresentado como perfeito, P0 | E5/E6 |
| L14 | H1, H2, H3 e intervalos | bootstrap isolado, sem análise por pergunta/grupo/hipótese; exporta basicamente recuperação | Evidência insuficiente para redação, P1 | E6 |
| L15 | Operação confiável pelo aplicativo | chamadas síncronas; sem tarefas persistentes, retomada, orçamento ou política de repetição | Falhas/custos sem controle, P1 | E4 |
| L16 | Catálogo piloto e administração | não há bateria 24 versionada no SQLite, restauração de arquivadas ou seleção visual de relevância | Trabalho manual e mistura de conjuntos, P1 | E2 |
| L17 | Histórico imutável | curadoria de execução pode alterar referências após métricas calculadas | Métricas e referência divergem, P0 | E2/E4 |
| L18 | Validação da interface | `tests/test_dashboard.py` só testa parse de JSON | Fluxos quebrados passam na suíte, P0 | Todas |

## 4. Reproduções sintéticas

Sem chamadas externas, com corpus fictício e SQLite temporário:

- Referências `{a,b,c}`, ranking `[a,b,x]`: implementação retorna Recall@1=1, Recall@5=1; pela definição da própria dissertação deveriam ser 1/3 e 2/3. Hit permanece 1.
- Mesmo caso sem graus explícitos: nDCG@5=1,6309297535714575. A normalização está incorreta; esse resultado não pode sustentar comparação experimental.
- Salvar `respondible='0', answerability='nao', status='validada'`, sem referências ou justificativa: registro é aceito e retorna `respondible=True`.
- `_weighted_kappa([2,2],[2,2])` retorna 1; o denominador é zero. Deve retornar não estimável, mantendo acordo exato=1 em campo separado.

A ordenação inicial do retorno Chroma, a perda de anotações ao editar e a falta de controle de versões foram identificadas por inspeção; não se presume que já tenham produzido resultados científicos. Não existem execuções no banco local.

## 5. Parecer operacional

Pode-se usar o ambiente para inspeção do corpus e desenvolvimento. Antes da curadoria definitiva, estabilizar versões dos chunks, preservar anotações e corrigir respondibilidade. Antes do piloto de recuperação, corrigir métricas e recuperadores. Antes da avaliação humana/automática, congelar contexto e rubrica e concluir o fluxo de avaliações independentes.

O plano e os critérios de passagem estão em `PLANO_GESTAO_INTEGRAL_EXPERIMENTOS.md`. As seis mudanças OpenSpec permanecem propostas, com tarefas abertas; nenhuma funcionalidade planejada é declarada implementada.
