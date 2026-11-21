criteria_parallel_conflicts: []
[REVIEW-TARGET-BINDING v1]
target_review_id=qualification-dissertacao-2026-11
consumer_id=external_panel
role=R1
context_ref=context.json
context_sha256=358b5370cead2090411589c48f05a3aa5234d12ef291f9d9d6ecb414ac21b320
resolved_digest=6f675cd7c2eed7118e7d5f65c5e9073367d48f17a8a92797d5df181e6e8ed70e
selected_criterion_ids=["broad.claim-evidence-alignment","broad.limitation-calibration","broad.method-evidence-alignment","broad.submission-traceability"]
[/REVIEW-TARGET-BINDING]

contract_role: methodology
## Dimension Scores

### D1: methodology_rigor
score: block
trigger: "Lacuna reparável no protocolo, nos controles, na validade da mensuração ou na análise que impeça executar uma comparação central defensável ou sustentar um resultado central já declarado, exigindo revisão substantiva antes da continuidade ou aceitação dessa inferência."
block_class: repairable

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: block
trigger: "Salto inferencial central reparável, incluindo conclusão apresentada como demonstrada sem evidência correspondente, confusão entre construtos de avaliação ou generalização além do desenho, que exija reformular a argumentação principal ou acrescentar suporte empírico."
block_class: repairable

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

### Identidade, escopo e calibração

Peer Reviewer 1: especialista em métodos mistos e avaliação de RAG. Parecer sobre a metodologia do manuscrito integral compilado, incluindo apêndices, conferido contra os arquivos LaTeX atuais. Confiança geral: 4/5, pela análise direta do desenho e das regras; os dados brutos e os sistemas não foram reexecutados. Calibration Status: `NOT_CALIBRATED`. O compromisso de Fase 1 permanece inalterado. Não foram consultados pareceres dos outros papéis.

O objeto é uma dissertação em qualificação. A ausência dos resultados do experimento principal é compatível com esse estágio. Os bloqueios reparáveis dizem respeito à validade das regras prospectivas e à definição de comparações centrais; não exigem apresentar resultados ainda inexistentes. Não identifico defeito metodológico demonstravelmente irremediável nem achado Critical.

### Juízos vinculados aos critérios

Fonte dos quatro critérios: ARS Review Criteria Framework, conforme manifesto e Target Criteria Brief fornecidos; aplicação geral ao campo, sem requisitos institucionais específicos do IDP. Os critérios são aplicáveis ao manuscrito, com a limitação de que somente os aspectos metodológicos são examinados.

| Critério | Juízo | Âncora | Fundamentação e incerteza | Incidência |
|---|---|---|---|---|
| broad.claim-evidence-alignment, v1.0 | PARTLY_MEETS | text: §3.4, p.38, "H1 será corroborada quando houver pelo menos um caso documentado" | A separação entre piloto e experimento é adequada, mas a regra de H1 não demonstra a necessidade enunciada; W1. Não há resultados principais para avaliar. | Sim, D3. |
| broad.limitation-calibration, v1.0 | MEETS | text: §6.5, p.52, "os achados não estabelecem desempenho para outros acervos, modelos ou ambientes" | Limites de configuração, rubrica, independência e generalização são explícitos. Há uma inconsistência localizada sobre a inspeção preliminar, W8. | Sim, favorável à calibração das alegações atuais. |
| broad.method-evidence-alignment, v1.0 | PARTLY_MEETS | absence: §§3.2.3–3.4 e apêndices A–C — expected regras completas para comparações, aplicação da rubrica e adjudicação das hipóteses; checked protocolo metodológico, configuração experimental, apêndices e remissões | Há componentes apropriados, mas permanecem lacunas substantivas de mensuração, comparabilidade e inferência; W1–W6. | Sim, D1. |
| broad.submission-traceability, v1.0 | PARTLY_MEETS | text: §3.2.2, p.31, "O código de coleta, as dependências e um comando de execução encontram-se no Apêndice 7.4." | Versão, hash e código favorecem rastreabilidade; a remissão não corresponde ao apêndice E e os instrumentos principais ainda estão vazios. Acesso remoto não foi auditado. | Consultiva; não fundamenta bloqueio isoladamente. |

### Avaliação sintética

O desenho organiza componentes adequados para estudar avaliação de RAG: corpus congelado, recuperação com referência documental, rubrica de respostas, julgamento humano, comparação com juiz automatizado e análise de erros. A documentação distingue corretamente as execuções de viabilidade da investigação principal. Os valores elevados produzidos pelo juiz não são convertidos em evidência de qualidade, e as mudanças de hashes impedem que rodadas diferentes sejam apresentadas como replicações controladas. Essa disciplina sustenta a credibilidade do diagnóstico preliminar.

A revisão necessária concentra-se na passagem desse desenho geral para regras que possam decidir as hipóteses. H1 pode ser corroborada pela regra proposta mesmo diante de um contraexemplo à necessidade. A comparação de segmentações altera a própria unidade de referência, sem regra para preservar comparabilidade. H2 depende de uma nota global cuja aplicação às recusas adequadas ainda não está definida, e seu plano de incerteza não identifica a unidade de reamostragem. H3 requer uma referência humana operacional e critérios completos para classificar concordância e erros. Falta também separar o uso da bateria no desenvolvimento de seu uso avaliativo.

São problemas corrigíveis antes da execução principal. A qualificação pode apreciar o projeto sem resultados finais, mas precisa enxergar um protocolo suficientemente determinado para que resultados desfavoráveis, inconclusivos e contraditórios recebam tratamento previamente definido.

### S1: Proveniência documental e distinção entre fontes

**Evidence Anchor**: dataset: §3.2.2, pp.30–31; corpus discursos_2019-02-01_2023-01-31.parquet, revisão v1.1.1, SHA-256 e09cfc4793e5394be440906320c7d3008cda5a52b90bbc85bf47446362406af1; Tabela 3, p.44.

A versão congelada, o identificador documental e a URL oficial permitem construir uma cadeia de auditoria. Distinguir 15.039 textos integrais, 687 resumos e três registros inutilizáveis impede pressupor equivalência entre fontes de cobertura diferente. Isso é uma força de desenho, sem constituir auditoria independente do arquivo remoto.

### S2: Limites das evidências preliminares explicitados

**Evidence Anchor**: text: §3.4, p.38, "As rodadas do experimento de viabilidade não serão usadas para corroborar ou refutar H1–H3".

O texto registra ausência de relevância validada, de comparação controlada e de julgamento humano independente; também expõe a dependência gerador–juiz e as diferenças de hashes. As conclusões dos capítulos 5 e 6 permanecem, em geral, proporcionais à viabilidade demonstrada.

### S3: Métricas condicionadas à informação disponível

**Evidence Anchor**: text: §3.3.1, p.35, "itens não julgados não serão interpretados automaticamente como irrelevantes".

O protocolo distingue relevância de suficiência, prevê conjuntos de evidências complementares, explicita profundidade de MRR e evita interpretar perguntas não respondíveis como falhas de recuperação de evidência existente. Esses cuidados são apropriados, embora a implementação da referência precise das definições de W2.

### S4: Vínculo entre medições e diagnóstico qualitativo

**Evidence Anchor**: text: §3.3.5, p.37, "Cada caso será vinculado à pergunta, aos documentos recuperados, à resposta e aos julgamentos".

A cadeia proposta permite investigar se o erro começou na recuperação, no uso do contexto ou na atribuição da fonte. Isso oferece um ponto real de integração entre medidas quantitativas e exame qualitativo, a ser operacionalizado como indicado em W7.

### W1: A regra de H1 não testa a necessidade afirmada

**Severity**: Major
**Evidence Anchor**: text: §3.4, p.38; 03-procedimentos-metodologicos.tex:149, "H1 será corroborada quando houver pelo menos um caso documentado"; §1.3, p.14, "é condição necessária, mas não suficiente".
**Confidence**: 5 — análise lógica direta da regra decisória.

Encontrar recuperação pertinente/não verificável demonstra um contraexemplo à suficiência. Encontrar não pertinente/não verificável não demonstra necessidade. A regra admite corroborar H1 mesmo se também houver não pertinente/verificável, célula incompatível com a necessidade enunciada. Além disso, o indicador exige uma evidência individual suficiente no top-5, enquanto o protocolo admite perguntas dependentes de evidências complementares. Um conjunto suficiente de passagens pode ser classificado como ausência de recuperação pertinente. Também é necessário distinguir o top-5 avaliado do contexto efetivamente entregue ao gerador.

**Critérios aplicáveis**: broad.claim-evidence-alignment e broad.method-evidence-alignment, v1.0, ponteiros exatos no companion.
**Relevância científica**: uma regra pode produzir o rótulo de corroboração contrariando a própria hipótese.
**Relevância ao alvo confirmado**: fundamenta D1/D3 na qualificação; não deriva de exigência específica do IDP.
**Remédio mínimo**: explicitar o domínio de H1, admitir conjuntos suficientes, registrar a célula que falsifica necessidade e distinguir ausência de contraexemplo na amostra de demonstração universal. Se a intenção for somente localizar falhas complementares, reformular H1 como proposição diagnóstica por decisão do autor.
**Esforço e concessões**: revisão da hipótese e da seção operacional; não exige fabricar dados, mas reduz a força de uma alegação universal.
**Opção mais forte**: contrastar contextos pertinentes, insuficientes e sem evidência com as mesmas perguntas, mediante novas execuções planejadas; maior custo e ampliação do desenho, sujeita à escolha do autor.

### W2: O padrão de relevância precisa permanecer comparável entre segmentações

**Severity**: Major
**Evidence Anchor**: absence: §§3.2.3 e 3.3.1, pp.32–36; §4.3, p.45 — expected regra de correspondência entre evidências de referência e segmentações alternativas; checked definições de Rq e Sq, fórmulas de recuperação, tratamento de itens não julgados e apêndices A–B.
**Confidence**: 5 — avaliação de recuperação e unidades de mensuração.

A comparação promete manter as mesmas perguntas e julgamentos, mas define a unidade relevante como o trecho indexado, justamente o objeto que muda com tamanho e sobreposição. O número de trechos relevantes e a quantidade de texto em cinco posições podem mudar sem mudança equivalente na evidência coberta. Retirar identificadores repetidos não elimina trechos sobrepostos que expressam o mesmo suporte. O texto reconhece referência incompleta e itens não julgados, mas ainda não especifica como completar julgamentos ou calcular cada métrica quando um recuperador encontra evidência nova.

**Critério aplicável**: broad.method-evidence-alignment, v1.0.
**Relevância científica**: diferenças de denominador, cobertura e orçamento de contexto podem parecer diferenças de qualidade de recuperação.
**Relevância ao alvo confirmado**: afeta a comparação central de recuperadores e segmentações, portanto D1.
**Remédio mínimo**: anotar evidências por documento e intervalo textual estável, estabelecer o mapeamento para cada segmentação, a regra para sobreposição e conjuntos complementares e o tratamento dos não julgados. Uma alternativa de menor custo é comparar os recuperadores em segmentação fixa e limitar a análise de outras segmentações a um ensaio separado claramente delimitado.
**Esforço e concessões**: revisão do protocolo de referência; a alternativa simples reduz a amplitude da conclusão sobre segmentação e depende da escolha do autor.
**Opção mais forte**: curadoria conjunta dos resultados dos recuperadores e análise de sensibilidade por orçamento de contexto, com novas anotações; maior esforço documental, sem assegurar antecipadamente qualquer resultado.

### W3: A nota global ainda não tem interpretação uniforme entre respostas e recusas

**Severity**: Major
**Evidence Anchor**: absence: §§3.3.2 e 3.4, pp.36–39; apêndice C, p.66 — expected descritores por dimensão e regras de aplicabilidade para recusas e respostas parcialmente respondíveis; checked escala geral 0–2, média de cinco dimensões, regras de H2 e conteúdo do apêndice C.
**Confidence**: 5 — validade de construto e elaboração de rubricas.

O texto apresenta cinco dimensões e uma descrição comum de 0, 1 e 2, mas não uma regra aplicável a cada situação. Uma recusa correta pode não conter afirmações factuais ou citações; não está definido como receberá notas de correção, aderência, citações e completude. Perguntas respondíveis podem igualmente não demandar declaração de insuficiência. A média das cinco dimensões pode, portanto, comparar desempenhos sob exigências diferentes. O problema incide diretamente sobre o contraste de H2 com perguntas não respondíveis e sobre a classificação de qualidade em H3.

**Critério aplicável**: broad.method-evidence-alignment, v1.0.
**Relevância científica**: diferenças de pontuação podem refletir a aplicabilidade dos critérios, em vez da qualidade da resposta.
**Relevância ao alvo confirmado**: afeta a mensuração principal prevista para a qualificação, D1.
**Remédio mínimo**: completar a rubrica com descritores e exemplos por dimensão, regras para recusa adequada, resposta parcial e ausência de afirmações/citações, além do tratamento de não aplicabilidade e do denominador da média. Fixar quais contrastes poderão usar uma pontuação comum.
**Esforço e concessões**: elaboração do instrumento e revisão dos contrastes; separar desfechos pode diminuir a simplicidade da nota global e aumentar sua interpretabilidade.
**Opção mais forte**: realizar piloto cognitivo de anotação com exemplos de cada classe e revisar ambiguidades antes de congelar a rubrica; exige novas anotações e disponibilidade de avaliadores.

### W4: O plano de H2 não define completamente a comparação nem sua incerteza

**Severity**: Major
**Evidence Anchor**: text: §3.4, pp.38–39; 03-procedimentos-metodologicos.tex:151, "em pelo menos duas dimensões e em duas das três comparações principais"; "Intervalos de confiança por bootstrap".
**Confidence**: 4 — desenho comparativo e análise de medidas dependentes.

É possível inferir três contrastes com perguntas simples, mas falta o mapeamento explícito das 16 categorias para grupos mutuamente definidos, incluindo sobreposição entre multievidência e multietapas e o destino dos itens parciais. Também falta estabelecer em qual configuração, ou sobre qual agregação de configurações, a regra decidirá H2. O contraste primário de média global não está ligado claramente ao critério de duas dimensões. Não está definido se desempenho menor significa diferença de estimativas ou diferença sustentada pelo intervalo; o que contará como inconclusivo tampouco foi fechado. A menção ao bootstrap não identifica a unidade reamostrada. Respostas da mesma pergunta sob recuperadores ou repetições diferentes não são perguntas independentes.

**Critério aplicável**: broad.method-evidence-alignment, v1.0.
**Relevância científica**: escolhas posteriores de agrupamento, configuração e unidade de reamostragem podem alterar a decisão da hipótese.
**Relevância ao alvo confirmado**: afeta a executabilidade da comparação principal, D1.
**Remédio mínimo**: registrar mapa de grupos, tamanhos analíticos previstos, contrastes e desfechos primários, regra de interpretação da incerteza e categoria inconclusiva; definir reamostragem por pergunta, preservando seu conjunto de observações e a estrutura adicional de dependência quando houver. Justificar o tamanho da bateria pela precisão e cobertura pretendidas, sem impor teste causal ou poder convencional a toda a análise descritiva.
**Esforço e concessões**: completar o plano analítico antes dos resultados; uma análise restrita à bateria intencional terá generalização delimitada.
**Opção mais forte**: dimensionar e ampliar os grupos com base na precisão dos contrastes planejados, mediante novas perguntas e anotações; aumenta custo e precisa de escolha do autor.

### W5: A referência humana e a decisão de H3 ainda não são operacionais

**Severity**: Major
**Evidence Anchor**: text: §3.3.3, pp.36–37; 03-procedimentos-metodologicos.tex:128, "preferencialmente aplicada por pelo menos dois avaliadores independentes"; §3.4, p.39, "pelo menos 10% da amostra".
**Confidence**: 4 — concordância entre avaliadores e meta-avaliação.

A independência é central para H3, mas quantidade de avaliadores, tamanho e seleção da amostra, material exibido e cegamento permanecem contingentes. O texto preserva notas individuais e prevê adjudicação, o que é positivo; falta definir se o juiz será comparado com cada humano, com consenso ou com uma referência adjudicada. Não se define qual nota representa aprovação ou não verificabilidade para contar falsos positivos e negativos. Os pesos do kappa, o denominador dos 10% e o tratamento de resultados diferentes por dimensão também precisam ser fixados. O intervalo 0,40–0,75, sozinho, não justifica concluir que o juiz é inadequado como critério único; a gravidade das divergências importa. O caso de concordância muito baixa, contemplado na introdução, não recebe regra equivalente em §3.4.

**Critérios aplicáveis**: broad.method-evidence-alignment e broad.claim-evidence-alignment, v1.0.
**Relevância científica**: sem referência e decisão definidas, a mesma matriz de notas pode sustentar classificações distintas de H3.
**Relevância ao alvo confirmado**: afeta um objetivo e uma hipótese centrais, D1; a falta de avaliadores confirmados é uma condição real de viabilidade.
**Remédio mínimo**: especificar um desenho humano mínimo executável, preservar julgamentos anteriores à adjudicação, fixar amostragem, comparação, pesos, limiares operacionais e denominadores; registrar decisões para concordância baixa, parcial, alta e inconclusiva. Justificar a insuficiência do juiz pelo tipo e consequência dos erros, além do acordo agregado.
**Esforço e concessões**: protocolo de anotação e confirmação de recursos; se o mínimo não for viável, reduzir o alcance de H3 exige escolha explícita do autor.
**Opção mais forte**: ampliar a dupla anotação e adicionar avaliação cega por juiz de outra família, com orçamento e novas avaliações; reduz uma fonte de dependência, sem garantir independência completa nem qualidade.

### W6: Congelar a bateria não separa desenvolvimento e avaliação

**Severity**: Major
**Evidence Anchor**: absence: §§3.2.3, 4.6 e 5.2, pp.31–33, 47 e 49 — expected separação explícita entre perguntas usadas para ajustar o sistema e perguntas usadas na avaliação principal; checked descrição da bateria de 200 itens, piloto de 32, curadoria, congelamento e apêndices A–B.
**Confidence**: 4 — desenho de benchmarks e controle de adaptação ao conjunto de teste.

O piloto orienta ajustes e a bateria será revisada e congelada, mas não está dito se os itens já examinados alimentarão também a comparação principal. Não há separação entre os dados usados para selecionar segmentação, prompts e parâmetros e aqueles empregados para avaliar a configuração escolhida. O congelamento posterior não elimina informação previamente usada no desenvolvimento. Isso é risco não controlado pelo protocolo, não evidência de que já tenha ocorrido seleção indevida.

**Critério aplicável**: broad.method-evidence-alignment, v1.0.
**Relevância científica**: desempenho e padrões de erro em uma bateria adaptada podem refletir ajustes aos próprios exemplos.
**Relevância ao alvo confirmado**: afeta a interpretação dos resultados principais futuros, D1.
**Remédio mínimo**: identificar itens e decisões usados no desenvolvimento, reservar um conjunto de avaliação não usado nos ajustes e congelar configurações antes de examiná-lo. Se toda a bateria for deliberadamente diagnóstica, declarar essa finalidade e limitar as inferências, por decisão do autor.
**Esforço e concessões**: reorganização da bateria e do procedimento; reservar itens diminui a amostra disponível para cada finalidade.
**Opção mais forte**: construir uma bateria adicional, curada sem consulta às saídas do sistema ajustado, com novas perguntas e evidências; maior custo de curadoria e anotação.

### W7: A integração qualitativa precisa de regra de seleção e registro

**Severity**: Minor
**Evidence Anchor**: absence: §3.3.5, p.37, e Tabela 2, p.40 — expected regra de seleção dos casos, procedimento de codificação e modo de integrar divergências aos resultados quantitativos; checked descrição da análise de erros, matriz metodológica e apêndice D.
**Confidence**: 4 — desenho multimétodo e auditabilidade da análise qualitativa.

As famílias de erro e os vínculos entre artefatos estão previstos, mas não o procedimento para selecionar casos ou registrar interpretações discordantes. Completar com uma regra de cobertura dos casos críticos, inclusão de casos discrepantes, registro de códigos iniciais/emergentes e uma matriz pergunta–métrica–erro–evidência. A seleção intencional pode permanecer adequada, desde que não produza estimativas de prevalência sem denominador apropriado. O problema não invalida, por si, a parte quantitativa.

### W8: O estatuto da inspeção de q20 oscila entre diagnóstico e hipótese

**Severity**: Minor
**Evidence Anchor**: text: §4.5, p.46; 04-artefato-e-caso-empirico.tex:70, "foi considerada inadequada por erro de escopo"; §5.1, p.49, "o caso ilustra uma hipótese de falha a verificar".
**Confidence**: 5 — comparação direta de passagens.

A descrição inicial sugere um diagnóstico estabelecido; o capítulo de resultados esclarece que se trata de proposta argumentada sem anotação independente. Harmonizar as passagens e identificar o responsável e o procedimento dessa inspeção, sem convertê-la em validação humana. A ressalva posterior preserva o alcance global, de modo que a correção é localizada.

### W9: A remissão de reprodução leva ao número errado

**Severity**: Minor
**Evidence Anchor**: text: §4.4, p.46; 04-artefato-e-caso-empirico.tex:63, "As configurações completas, os resumos e as saídas por pergunta"; PDF, mesma seção, "Apêndice 7.4".
**Confidence**: 5 — conferência do PDF e da referência LaTeX.

O leitor é encaminhado a um apêndice identificado como 7.4, embora 7.4 seja o cronograma e a reprodução esteja no apêndice E. Corrigir a numeração/remissão e, na versão consolidada, associar os artefatos de viabilidade a arquivos e revisão específica. A base congelada já tem identificador e hash; o apontamento não questiona sua existência.

### Comentários metodológicos complementares e perguntas ao autor

Quanto ao delineamento, estudo de caso aplicado e abordagem multimétodos são compatíveis com a pergunta. Não é necessário converter o trabalho em experimento causal nem exigir resultados finais na qualificação. A contribuição do protocolo, contudo, deverá ser apreciada também por sua capacidade de identificar e distinguir falhas, não apenas pelo desempenho dos recuperadores.

Quanto à amostragem, a bateria balanceada é defensável como teste de cobertura de riscos; ela não estima distribuição de consultas reais, e o manuscrito reconhece esse limite. O número de respostas geradas não deve ser confundido com o número de perguntas independentes. Os modelos e parâmetros finais podem ser escolhidos após a qualificação, desde que sua seleção não utilize o conjunto reservado para a comparação final.

Quanto à apresentação estatística, o critério broad.method-evidence-alignment é PARTLY_MEETS: há métricas, contrastes e intenção de intervalos, mas W3–W5 impedem uma especificação completa. Não faltam valores-p, efeitos ou concordância de um experimento principal já realizado: esse experimento não foi executado. Os recibos abaixo documentam tentativas limitadas sobre as médias exploratórias. Não identifiquei incompatibilidade aritmética demonstrada, fabricação ou p-hacking; os riscos de adaptação à bateria e pseudorreplicação são prospectivos.

As questões que precisam de resposta operacional são:

1. A verificabilidade de H1 será julgada apenas a partir do contexto realmente entregue ao gerador, ou permitirá consultar outras fontes? Como serão classificadas as recusas e os conjuntos multievidência?
2. Qual material comprovará a não respondibilidade no corpus, quem fará essa curadoria e como será registrada a distinção entre ausência de evidência e evidência ainda não localizada?
3. Quantas perguntas e respostas receberão anotação humana por condição, e qual desenho mínimo será mantido se os avaliadores disponíveis forem menos numerosos que o desejado?
4. Quais configurações serão ajustadas no desenvolvimento e quais perguntas permanecerão reservadas para avaliação? Qual orçamento de contexto será mantido ou explicitamente comparado?

O companion `constructive_method.json` registra W1–W6 com os ponteiros exatos do manifesto, aplicabilidade, relevância científica e ao alvo, remédios, esforço, concessões e escolhas autorais. Não propõe valores de resultados nem afirma execução de novas análises.

## Arithmetic Receipts

### AR1
procedure_id: grim
evidence_anchor: table: Tabela 4, p.48, execução 05/05/2026, 14:26.
reported_inputs: Perguntas concluídas 20; Erros 0; Média do juiz (0–10) 9,350; cinco critérios em escala de 0 a 2 descritos em §5.1.
assumptions: A escala exploratória é composta; o manuscrito não enumera seus valores admissíveis nem informa regra de arredondamento; não se transfere a discretização da rubrica principal para a exploratória.
derivation: A tentativa requer a granularidade discreta do escore agregado para estabelecer o conjunto de médias alcançáveis; esse dado não está especificado.
derived_value_or_range: Indeterminado sem a granularidade do escore exploratório.
comparison_rule: Não declarar compatibilidade ou incompatibilidade GRIM sem suporte discreto e regra de arredondamento informados.
status: not_computable
not_computable_reason: scale_granularity_unknown

### AR2
procedure_id: grim
evidence_anchor: table: Tabela 4, p.48, execução 05/05/2026, 15:33.
reported_inputs: Perguntas concluídas 20; Erros 0; Média do juiz (0–10) 9,250; cinco critérios em escala de 0 a 2 descritos em §5.1.
assumptions: A rubrica exploratória não explicita incrementos admissíveis ou regra de arredondamento; sua escala composta não recebe por suposição a discretização da rubrica principal.
derivation: Sem incrementos admissíveis do escore total não se determina a malha de médias e a verificação de alcance não pode ser completada.
derived_value_or_range: Indeterminado sem a granularidade do escore exploratório.
comparison_rule: Aplicar GRIM somente depois de documentar granularidade e arredondamento, sem preencher valores ausentes.
status: not_computable
not_computable_reason: scale_granularity_unknown

### AR3
procedure_id: grim
evidence_anchor: table: Tabela 4, p.48, execução 05/05/2026, 16:27.
reported_inputs: Perguntas concluídas 32; Erros 0; Média do juiz (0–10) 9,031; cinco critérios em escala de 0 a 2 descritos em §5.1.
assumptions: Não se presume escore total inteiro nem regra de arredondamento a partir da indicação dos extremos 0 e 10.
derivation: A precisão publicada é de três casas decimais, mas a malha de médias possíveis depende da granularidade da rubrica exploratória, não explicitada.
derived_value_or_range: Indeterminado sem a granularidade do escore exploratório.
comparison_rule: Os extremos da escala e o número de casas não bastam para uma decisão GRIM.
status: not_computable
not_computable_reason: scale_granularity_unknown

### AR4
procedure_id: grim
evidence_anchor: table: Tabela 4, p.48, execução 05/05/2026, 17:11.
reported_inputs: Perguntas concluídas 32; Erros 0; Média do juiz (0–10) 9,094; cinco critérios em escala de 0 a 2 descritos em §5.1.
assumptions: Granularidade e arredondamento da rubrica exploratória não especificados; o hash diferente não autoriza supor identidade com a rubrica de outra execução.
derivation: A malha de médias alcançáveis não pode ser estabelecida com os dados relatados.
derived_value_or_range: Indeterminado sem a granularidade do escore exploratório.
comparison_rule: Não atribuir mismatch ou consistent com base em uma escala discreta suposta.
status: not_computable
not_computable_reason: scale_granularity_unknown

### AR5
procedure_id: grim
evidence_anchor: text: §5.1, p.49, "ambas foram concluídas, com média automática 9,0".
reported_inputs: duas perguntas; média automática 9,0; execução complementar de 5 de maio.
assumptions: A passagem não fixa granularidade da pontuação ou arredondamento dessa execução; não se imputam as regras das outras rodadas.
derivation: O tamanho informado permite identificar duas observações, mas não a malha dos escores cuja média foi apresentada.
derived_value_or_range: Indeterminado sem a granularidade da pontuação.
comparison_rule: Ausência de malha discreta impede concluir a verificação GRIM.
status: not_computable
not_computable_reason: scale_granularity_unknown

### AR6
procedure_id: grim
evidence_anchor: text: §5.5, p.50, "três rodadas de 20 perguntas"; "9,15, 9,55 e 9,35"; primeira média da sequência de abril.
reported_inputs: 20 perguntas; média automatizada 9,15; §4.5 descreve cinco critérios em escala de 0 a 2 para a série inicial.
assumptions: Não se presume incremento inteiro do total ou arredondamento; a enumeração 0, 1 e 2 pertence à rubrica principal, distinta.
derivation: Falta granularidade explicitamente atribuída à rubrica exploratória para construir as médias possíveis.
derived_value_or_range: Indeterminado sem a granularidade do escore exploratório.
comparison_rule: Não converter uma interpretação plausível da escala em premissa do teste GRIM.
status: not_computable
not_computable_reason: scale_granularity_unknown

### AR7
procedure_id: grim
evidence_anchor: text: §5.5, p.50, "três rodadas de 20 perguntas"; "9,15, 9,55 e 9,35"; segunda média da sequência de abril.
reported_inputs: 20 perguntas; média automatizada 9,55; §4.5 descreve cinco critérios em escala de 0 a 2 para a série inicial.
assumptions: Granularidade e arredondamento da rubrica exploratória não especificados para esta média.
derivation: A granularidade ausente impede a comparação do valor publicado com o conjunto de médias alcançáveis.
derived_value_or_range: Indeterminado sem a granularidade do escore exploratório.
comparison_rule: Exigir alcance no intervalo de arredondamento e malha documentados antes de decidir consistência.
status: not_computable
not_computable_reason: scale_granularity_unknown

### AR8
procedure_id: grim
evidence_anchor: text: §5.5, p.50, "três rodadas de 20 perguntas"; "9,15, 9,55 e 9,35"; terceira média da sequência de abril.
reported_inputs: 20 perguntas; média automatizada 9,35; §4.5 descreve cinco critérios em escala de 0 a 2 para a série inicial.
assumptions: Não se presume granularidade do composto, arredondamento ou identidade desta rodada com a execução de maio cuja média também é 9,350.
derivation: O manuscrito relata séries distintas; a tentativa desta média não pode aproveitar premissas não especificadas ou fundir rodadas por coincidência numérica.
derived_value_or_range: Indeterminado sem a granularidade do escore exploratório.
comparison_rule: A decisão GRIM requer valores admissíveis e arredondamento da série efetivamente relatada.
status: not_computable
not_computable_reason: scale_granularity_unknown
