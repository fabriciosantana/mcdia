# Plano de gestão e execução integral dos experimentos

## Material Passport

- Data: 2026-10-15; status: implementação E1–E6 integrada e aceitação sintética ponta a ponta concluída.
- Origem: [avaliação do protocolo e do sistema](AVALIACAO_PROTOCOLO_SISTEMA_2026-10-14.md).
- Objetivo: operar importação, curadoria, recuperação, geração, avaliação e análise no aplicativo, com SQLite como fonte operacional e Chroma como armazenamento vetorial.
- Decisões científicas pertencem ao pesquisador; o plano não modifica as hipóteses nem autoriza resultados finais.

## Sequência e critérios de passagem

| Ordem | Mudança OpenSpec | Prioridade / dependências | Resultado e condição para avançar |
|---|---|---|---|
| E1 | [versioned-corpus-management](../openspec/changes/versioned-corpus-management/proposal.md) | P0, base | Corpus, fontes e segmentações versionados no SQLite; duas janelas coexistem sem alterar IDs/textos usados na curadoria |
| E2 | [curated-question-batteries](../openspec/changes/curated-question-batteries/proposal.md) | P0, E1 | 200 perguntas reconciliadas; piloto de 24 identificado; graus e justificativas administráveis; revisão não apaga campos; congelamento preserva snapshots |
| E3 | [validated-retrieval-engine](../openspec/changes/validated-retrieval-engine/proposal.md) | P0, E1–E2 | Métricas numericamente corretas; BM25, vetorial Chroma e híbrido lexical-vetorial identificados; índice pronto e verificável |
| E4 | [managed-experiment-execution](../openspec/changes/managed-experiment-execution/proposal.md) | P0/P1, E1–E3 | Execução pelo aplicativo sem caminhos manuais; contexto congelado; tarefas persistentes; retomada explícita, custos e falhas observáveis |
| E5 | [evidence-based-evaluation](../openspec/changes/evidence-based-evaluation/proposal.md) | P0 antes da anotação, E2/E4 | Rubrica calibrada; humanos independentes; juiz com pergunta/contexto e prompt próprio; afirmações e citações rastreáveis |
| E6 | [dissertation-evidence-reporting](../openspec/changes/dissertation-evidence-reporting/proposal.md) | P1 antes da coleta final, E3–E5 | H1–H3 com casos, denominadores e intervalos; exports compiláveis; backup restaurado; aceitação ponta a ponta |

Implementação realizada em sequência E1→E2→E3→E4→E5→E6. Os módulos, telas e migrações foram integrados. A aceitação sintética repetível passou por migração legada, proveniência do piloto, curadoria, versões, três recuperadores, geração, avaliação cega, análise, exportação e restauração. O dashboard foi renderizado pelo Streamlit AppTest.

## Estado de implementação

- E1–E6: funcionalidades implementadas em código, migrações 009–015 e telas Streamlit.
- Banco operacional: migrações 009–015 aplicadas com backup pré-migração em `data/artifacts/experiment_registry-pre-versioned-corpus.sqlite3`. `PRAGMA integrity_check` retornou `ok`; 94.360 chunks foram preservados e reconciliados, 15.726 documentos legados foram registrados e as 200 perguntas continuaram no catálogo. Nenhuma resposta ou execução experimental foi perdida; não havia resultados experimentais.
- Aceitação sintética: roteiro repetível em [`scripts/acceptance_synthetic.py`](../scripts/acceptance_synthetic.py). Passaram importação integral/resumo/ausente, idempotência, coexistência e rollback de versões, importação dos 24 itens piloto por proveniência, edição e congelamento da curadoria, construção/retomada de Chroma, BM25/denso/híbrido, geração com citações válidas e desconhecidas, falha incerta e retomada, dois avaliadores cegos, juiz, adjudicação, H1–H3 com dados ausentes, compilação LaTeX e restauração de SQLite + Chroma com integridade e anonimização.
- Interface: Streamlit AppTest renderizou as abas principais sem exceções. Os serviços de domínio e os fluxos de ponta a ponta foram exercitados em base isolada; avisos de depreciação `use_container_width` não impedem execução, mas devem ser removidos em atualização futura de Streamlit.
- Os testes automatizados de software não substituem a validação científica do corpus, calibração humana da rubrica, decisão protocolar ou piloto real. Nenhuma chamada de LLM real foi feita e nenhum resultado científico foi produzido.

## Prioridade imediata

1. Revisar no aplicativo as 200 perguntas migradas e a bateria piloto de 24 itens; validar manualmente respondibilidade, referências e escopo antes de congelar uma bateria.
2. Registrar as decisões científicas ainda abertas no protocolo analítico e calibrar a rubrica com os avaliadores.
3. Executar um piloto real pequeno com limites de custo/tempo, inspecionar erros e então congelar a campanha final.

## Modelo operacional proposto

| Entidade / tela | Operações necessárias | Persistência e regra |
|---|---|---|
| Corpus e documentos | Importar, inspecionar cobertura, filtrar, arquivar | SQLite; arquivo bruto preservado como proveniência, sem edição manual cotidiana |
| Segmentações e chunks | Preparar, comparar versões, buscar, visualizar contexto | SQLite; conteúdo imutável por versão e tokenizador identificado |
| Perguntas e baterias | Criar, editar revisão, agrupar piloto/final, arquivar/restaurar | SQLite; origem e versões, sem CSV obrigatório |
| Evidências de referência | Selecionar chunk visualmente, graduar 0/1/2, justificar, revisar | SQLite; FK para versão exata, anotador e histórico |
| Índices | Configurar, estimar trabalho, construir, acompanhar, retomar, arquivar | Metadados/estado SQLite; embeddings Chroma; proteção de índices referenciados |
| Configurações e prompts | Formulários tipados, copiar versão, congelar | SQLite; credenciais só por referência a ambiente seguro |
| Experimentos e tarefas | Planejar matriz, selecionar bateria/índice, iniciar, cancelar, retomar | SQLite; cada tentativa e etapa identificadas |
| Respostas e citações | Inspecionar pergunta, contexto, resposta e links | SQLite; snapshot completo, citação separa documento e chunk |
| Avaliadores e rodadas | Cadastrar pseudônimo, distribuir amostra, anotar, adjudicar | SQLite; cegamento e notas independentes preservadas |
| Juiz | Configurar modelo/rubrica, executar rodada, comparar estabilidade | SQLite; entrada, saída, parâmetros e prompt próprios |
| Resultados e casos | Comparar, estratificar, analisar H1–H3, registrar casos críticos | SQLite; métricas por pergunta e algoritmo versionado |
| Exportação e backup | Baixar evidência, tabelas, histórico e restaurar cópia | Arquivos gerados pelo aplicativo; nunca obrigatórios para tocar a operação diária |

O sistema RAG sob avaliação compreende segmentação, índices, recuperação, contexto e geração. O gerenciador controla versões, tarefas, baterias, anotação, análises e relatórios. Manter essa separação nos serviços de domínio, com uma interface única para o usuário.

## Regras para migração

- Migrar em cópia e conferir contagens: 200 perguntas e 94.360 chunks existentes; valores atuais devem ser lidos de novo no momento da migração.
- Não alterar o Parquet congelado nem promover o conteúdo local a gold automaticamente.
- Migrar os chunks atuais como segmentação legada por espaços 160/32. Introduzir segmentação por tokenizador como outra versão e comparar conforme protocolo.
- Reconstruir proveniência integral/resumo a partir da fonte congelada e registrar reconciliação, sem atribuir equivalência entre fontes.
- Corrigir `respondible='0'` pela origem somente quando não houver revisão humana; conflitos vão para curadoria. A classe parcial continua explícita até definição protocolar.
- Importar a composição piloto por chave de origem, não por coincidência entre IDs P e D.
- Não apagar índices usados por execuções; falhas de leitura não justificam reindexação destrutiva.
- Não atualizar resultados históricos para acompanhar edições no catálogo; análises corrigidas devem referenciar versão da métrica e gold utilizado.

## Decisões a fechar no protocolo

Registrar no aplicativo, antes de congelar a bateria final:

- Política de respondibilidade parcial, elegibilidade e tratamento de gold incompleto.
- Unidades e limites da verificabilidade em H1 e tratamento dos contraexemplos.
- Grupos e três contrastes de H2, sobreposição entre categorias e pergunta não respondível fora do denominador de Hit.
- Tipo de ganho para nDCG, grau que define relevância/suficiência, tratamento de duplicatas e não julgados; precisão com ranking curto.
- Tokenizador, janelas candidatas e critérios para escolher a configuração final.
- Tamanho/composição da amostra humana e número efetivo de avaliadores, cegamento, adjudicação e rubrica com exemplos.
- Pesos de kappa, rodada comparada, política de agregação humana e de repetição do juiz.
- Limites de custo, tempo e número de repetições; configuração final não será escolhida apenas por conveniência pós-resultado.

Essas decisões não bloqueiam a construção dos formulários e das validações; bloqueiam o congelamento científico quando ainda indefinidas.

## Aceitação integral

Em ambiente de teste isolado, com os serviços e a interface renderizada e sem editar CSV/JSON:

1. Importar um corpus pequeno com texto integral, resumo e ausência textual; verificar cobertura.
2. Criar duas segmentações; preservar a primeira após gerar a segunda.
3. Criar bateria com perguntas respondíveis, parcialmente respondíveis e não respondíveis; justificar decisões e graus, congelar versão.
4. Construir índice Chroma com cliente falso determinístico; reutilizar embeddings; interromper um lote e retomar explicitamente.
5. Executar BM25, denso e híbrido sobre a mesma bateria; conferir resultados de referência calculados à mão.
6. Gerar respostas com cliente falso; verificar prompt, contexto e citações, incluindo uma citação inválida.
7. Aplicar rubrica por dois avaliadores sem revelar notas ou modelo; adjudicar sem apagar os julgamentos originais.
8. Executar duas rodadas do juiz com contexto e comparar pares explicitamente escolhidos, sem duplicar amostra.
9. Gerar relatórios H1–H3 com casos faltantes e amostras constantes tratados corretamente.
10. Exportar tabelas, compilá-las em LaTeX mínimo e restaurar backup em ambiente limpo, conciliando IDs, hashes e métricas.

O roteiro sintético passou e verifica o comportamento do sistema, mas não valida empiricamente a dissertação nem substitui navegação humana de usabilidade. Próxima sequência: revisar e validar curadoria → calibrar e documentar decisões → piloto real limitado → congelamento final → campanha final. Revisões decorrentes do piloto não devem ser apresentadas como escolhas anteriores ao piloto.

## Atualização editorial depois das entregas

- Metodologia: distinguir corpus congelado, preparação legada, protocolo final, bateria curada e execução efetiva; substituir a obrigação operacional do notebook 02 pelo aplicativo, se essa decisão for mantida.
- Artefato e caso: descrever SQLite/Chroma, versões e dados de execução efetivamente registrados.
- Resultados: preencher bateria, recuperação, geração, humano/juiz e erros somente a partir de evidências elegíveis.
- Discussão: interpretar H1–H3 sem transformar regras de decisão ou médias em certificação institucional.
- Considerações finais: responder aos objetivos apenas com evidências produzidas, preservando limites do caso.

Estimativas de prazo devem ser feitas após detalhar E1 e validar o esforço de migração. A ordem e os critérios de aceitação são mais confiáveis neste momento que prometer datas para as seis entregas.

## Acompanhamento da implementação

Por orientação do pesquisador, o planejamento será acompanhado exclusivamente pelas seis mudanças OpenSpec locais, sem criação de issues no GitHub. Cada mudança contém proposta, desenho, requisitos com cenários de aceitação e tarefas pendentes. Atualizar as tarefas conforme a implementação e arquivar a mudança somente após verificar seus critérios de aceitação.
