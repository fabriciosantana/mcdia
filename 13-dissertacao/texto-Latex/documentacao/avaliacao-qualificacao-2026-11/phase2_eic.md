# Parecer EIC — adequação, contribuição e apresentação

criteria_parallel_conflicts: []
[REVIEW-TARGET-BINDING v1]
target_review_id=qualification-dissertacao-2026-11
consumer_id=external_panel
role=EIC
context_ref=context.json
context_sha256=358b5370cead2090411589c48f05a3aa5234d12ef291f9d9d6ecb414ac21b320
resolved_digest=6f675cd7c2eed7118e7d5f65c5e9073367d48f17a8a92797d5df181e6e8ed70e
selected_criterion_ids=["broad.claim-evidence-alignment","broad.limitation-calibration","broad.method-evidence-alignment","broad.submission-traceability"]
[/REVIEW-TARGET-BINDING]

contract_role: eic
## Dimension Scores

### D1: methodology_rigor

score: not_assessed

### D2: domain_accuracy

score: not_assessed

### D3: argumentative_coherence

score: not_assessed

### D4: cross_disciplinary_relevance

score: not_assessed

### D5: writing_and_structure

score: warn
trigger: "Há ambiguidades locais, repetições, transições deficientes ou problemas de apresentação que dificultam a leitura, mas a proposta e seu estado de execução continuam identificáveis."

### D6: venue_fit_and_contribution

score: warn
trigger: "A contribuição é identificável e pertinente, mas sua diferenciação, seu público beneficiário ou seus limites precisam de explicitação pontual."

## Review Body

### Identidade, escopo e confiança

Journal-Fit Reviewer de caráter geral, configurado para uma qualificação de mestrado em Administração Pública. Manuscrito: *Técnicas de avaliação de sistemas RAG: aplicação empírica a discursos parlamentares do Senado Federal*. Foram lidos integralmente o PDF extraído, seus sete capítulos e apêndices; os arquivos LaTeX foram consultados para confirmar os locais indicados. As páginas citadas são as impressas no manuscrito.

Confiança geral: **4/5**, com base na análise editorial de contribuição, adequação e estrutura. Não foram auditados externamente os estudos citados nem reproduzidas as execuções. Não se avalia conformidade com normas institucionais ou editoriais indisponíveis. Nenhum parecer de outro revisor foi consultado. A continuidade do marcador EIC e da linha de conflitos foi preservada em relação à Fase 1.

Calibration Status: `NOT_CALIBRATED`.

### Síntese da apreciação

A dissertação propõe organizar técnicas de avaliação de RAG em um protocolo aplicado aos discursos da 56ª Legislatura do Senado Federal. O trabalho reúne corpus versionado, preparação documental e execuções de viabilidade; a comparação controlada entre recuperadores, a curadoria do conjunto de referência e a avaliação humana independente pertencem ao experimento principal ainda previsto. Seu mérito editorial está em transformar uma aplicação de IA em um problema de avaliação de informação pública, com atenção a autoria, fonte e insuficiência documental.

A proposta é pertinente a uma qualificação em Administração Pública e possui contribuição aplicada identificável. A organização permite reconstruir a pergunta, os objetivos e o percurso empírico. A discussão também distingue resultados preliminares de evidências necessárias para examinar H1–H3, sem converter notas automáticas em comprovação de qualidade institucional.

As ressalvas deste parecer concentram-se na explicitação do diferencial e na apresentação da versão submetida. O resumo não informa com suficiente precisão o estado de execução; as subseções finais permanecem vazias; os apêndices anunciados para os instrumentos ainda não apresentam conteúdo. Uma declaração mais direta do aprendizado esperado e do usuário imediato do protocolo fortaleceria a contribuição. Essas correções são localizadas: no escopo EIC, não exigem substituir o problema nem antecipar resultados finais. Os juízos D5 e D6 registram essas ressalvas; a decisão do painel cabe à síntese posterior.

### Aplicabilidade e juízos vinculados aos critérios

Os quatro critérios vinculados são pertinentes ao manuscrito. Sua aplicação neste parecer respeita o escopo editorial: a adequação técnica dos métodos permanece sem julgamento EIC. Não há critério específico de periódico ou instituição selecionado. A apreciação de D6 decorre do cartão aceito para qualificação, não de conformidade institucional presumida.

| Dimensão ou critério | Fonte | Juízo | Âncora | Fundamentação e limite | Incidência neste parecer |
|---|---|---|---|---|---|
| D5 — apresentação | Contrato e compromisso EIC | PARTLY_MEETS | absence: §7.1–7.3, p. 53 — expected síntese escrita do estágio atual; checked capítulo 7 e seu arquivo LaTeX | O percurso está reconstruível, mas o fechamento e os instrumentos anunciados estão incompletos; W2–W4. | Sim, sustenta `warn`. |
| D6 — contribuição e adequação | Cartão aceito: qualificação em Administração Pública | PARTLY_MEETS | text: §2.4.1, p. 24, "Esta dissertação se diferencia por avaliar um acervo real de discursos do Senado brasileiro" | Contribuição contextual pertinente; explicitar o aprendizado e o destinatário imediato fortaleceria sua diferenciação; W1. Não se exige inovação algorítmica. | Sim, sustenta `warn`. |
| `broad.claim-evidence-alignment` | Manifesto, versão 1.0 | PARTLY_MEETS | text: resumo, "seguida de um experimento principal com protocolo consolidado e comparação controlada" | O corpo distingue adequadamente as etapas; o resumo precisa transportar essa distinção; W2. Avaliação restrita à apresentação das alegações. | Sim, ressalva localizada em D5; sem voto em D1–D3. |
| `broad.limitation-calibration` | Manifesto, versão 1.0 | MEETS | text: §6.4, p. 52, "não foram testados como resultados de implantação institucional" | As limitações de inferência e implantação são explícitas. Não equivale a validar a suficiência dos controles metodológicos. | Sim, sustenta a delimitação positiva de D6. |
| `broad.method-evidence-alignment` | Manifesto, versão 1.0 | NOT_ASSESSED | — | Aplicável à pesquisa, mas a avaliação técnica não pertence a esta cadeira. A localização editorial de instrumentos é examinada em W4. | Não recebe voto técnico EIC. |
| `broad.submission-traceability` | Manifesto, versão 1.0; caráter consultivo | PARTLY_MEETS | absence: apêndices A–D, pp. 64–67 — expected conteúdo ou remissões específicas aos instrumentos anunciados; checked apêndices A–E e §§3.2.3, 3.3.2–3.3.4 | Há versão e hash do corpus; faltam instrumentos nos apêndices e remissões precisas para alguns materiais. Não se presume exigência institucional. | Consultivo; nunca constitui fundamento exclusivo de bloqueio. |

Ponteiros exatos do manifesto, preservados sem redefinição dos critérios:

| Critério | Versão | Digest |
|---|---|---|
| `broad.claim-evidence-alignment` | `1.0` | `3fa3b4d5a78ed61a13821b70f03e6b741ef91a5818c636f217e7a4461a8c48cc` |
| `broad.limitation-calibration` | `1.0` | `dbbcee8ad323847d1765a3678243734077c801fe03d075ce81ec2c788319e2ee` |
| `broad.method-evidence-alignment` | `1.0` | `1b753aeb4639e5b97f98732598cbbcd26ec8ebdaf8c15127eb45f584901d95d3` |
| `broad.submission-traceability` | `1.0` | `803a83aceb4f629df74469670c9ad5276cd0a2eb0a400bbffd88d46cf2033296` |

### S1: Problema de Administração Pública delimitado pela avaliação do uso documental

**Evidence Anchor**: text: §1.5, p. 17, "oferecer uma forma mais criteriosa de avaliá-los antes de qualquer uso ampliado".

A justificativa concentra a contribuição na avaliação de sistemas aplicados à informação legislativa. Isso permite uma dissertação pertinente ao campo sem depender da promessa de implantação nem da demonstração de impactos sociais que o desenho não pretende medir. A ligação com acesso verificável à informação pública é clara para pesquisadores, gestores e equipes técnicas.

### S2: Distinção explícita entre viabilidade e conclusão sobre as hipóteses

**Evidence Anchor**: text: abertura do capítulo 6, p. 51, "os resultados não corroboram nem refutam H1–H3".

O capítulo de discussão delimita o alcance das execuções e preserva a necessidade de referência documental e avaliação humana independentes. As notas do juiz permanecem descritas como resultados da configuração preliminar. Essa apresentação evita que a qualificação se apoie em resultados do experimento principal ainda não realizado.

### S3: Caracterização documental útil e rastreabilidade da base

**Evidence Anchor**: table: Tabela 3, p. 44 — 15.039 registros com texto integral, 687 com resumo substituto e três sem conteúdo utilizável.

A caracterização distingue fontes com cobertura documental diferente e torna visíveis limitações relevantes para interpretar consultas. A versão e o hash apresentados em §3.2.2 e as instruções do Apêndice E complementam essa contribuição. O mérito é a documentação disponível no manuscrito; este parecer não certifica a integridade externa dos arquivos.

### W1: O diferencial aplicado está identificado, mas seu produto de conhecimento pode ser mais explícito

**Severity**: Minor
**Evidence Anchor**: text: §2.5, pp. 26–27, "a lacuna refere-se à escassez de estudos empíricos"; §1.4.2, p. 16, "Analisar a complementaridade e os limites das técnicas avaliativas".
**Confidence**: 4 — análise editorial de contribuição aplicada.

**Problema e relevância**: a lacuna e os objetivos permitem reconhecer uma contribuição contextual, mas o leitor precisa reunir passagens distintas para entender o que constituirá o aprendizado próprio da dissertação, além da aplicação ao corpus brasileiro. A lista ampla de públicos na Tabela 2 também não identifica quem utilizará imediatamente o protocolo. Isso enfraquece a nitidez de D6, sem descaracterizar a pertinência do projeto.

**Melhoria**: acrescentar uma declaração breve que diferencie técnicas aproveitadas da literatura, adaptações ao acervo parlamentar e conhecimento que a comparação pretende produzir. Indicar o destinatário imediato e a decisão avaliativa que o protocolo pretende apoiar. Essa explicitação pode usar o escopo já assumido, sem ampliar o estudo para implantação ou avaliação de impacto. Vínculo: D6 e `broad.claim-evidence-alignment`, conforme o ponteiro acima.

### W2: O resumo não distingue claramente o que já foi executado

**Severity**: Minor
**Evidence Anchor**: text: resumo, "O protocolo avaliativo articula métricas de recuperação, rubrica de avaliação das respostas, julgamento humano independente"; §5.5, p. 50, "Os artefatos disponíveis não documentam uma rodada de avaliação humana independente".
**Confidence**: 5 — comparação direta entre resumo e estado de execução declarado.

**Problema e relevância**: o presente empregado no resumo descreve o protocolo pretendido, mas não informa que o julgamento humano independente e a comparação principal permanecem planejados. Não há afirmação inequívoca de que foram concluídos; há uma ambiguidade evitável na principal porta de entrada do texto, relevante para D5.

**Melhoria**: identificar expressamente a versão de qualificação, resumir os produtos já disponíveis e marcar como futuras as etapas principais. Uma frase sobre o alcance limitado da viabilidade transportará para o resumo a cautela já presente no corpo. Não incluir resultados ou conclusões ainda inexistentes. Vínculos: `broad.claim-evidence-alignment` e `broad.limitation-calibration`.

### W3: O capítulo final ainda não fecha a argumentação da versão de qualificação

**Severity**: Minor
**Evidence Anchor**: absence: §7.1–7.3, p. 53 — expected síntese das contribuições disponíveis, limitações atuais e próximos passos; checked capítulo 7 completo e capitulos/07-consideracoes-finais.tex.
**Confidence**: 5 — verificação direta de subseções sem texto.

**Problema e relevância**: os três títulos aparecem sem desenvolvimento, enquanto o cronograma ocupa o restante do capítulo. O leitor termina sem uma resposta provisória e delimitada sobre o que a pesquisa já construiu e o que falta para responder à pergunta. As informações necessárias estão em outras partes, portanto a falha é de fechamento editorial, não de ausência de resultados finais obrigatórios.

**Melhoria**: redigir uma síntese própria da qualificação, relacionando produtos disponíveis aos objetivos, reunindo limitações já reconhecidas e explicitando as dependências do experimento principal. Não aguardar a execução final para preencher essas subseções. Vínculos: D5 e `broad.submission-traceability`, de caráter consultivo.

### W4: Os apêndices anunciam instrumentos que ainda não estão apresentados

**Severity**: Minor
**Evidence Anchor**: absence: apêndices A–D, pp. 64–67 — expected instrumentos identificados nos títulos ou indicação precisa de sua localização e estágio; checked páginas dos apêndices A–E, postextual/apendices.tex e §§3.2.3, 3.3.2–3.3.4.
**Confidence**: 5 — inspeção integral dos apêndices e das remissões no corpo.

**Problema e relevância**: quatro páginas contêm apenas títulos. O Apêndice E aponta um diretório geral para os artefatos de viabilidade, mas não permite identificar imediatamente quais arquivos correspondem à bateria, à rubrica e às execuções discutidas. O corpo descreve esses elementos suficientemente para compreender a proposta; o prejuízo aqui é a consulta editorial aos materiais anunciados, em D5.

**Melhoria**: apresentar versões preliminares disponíveis, exemplos reais identificados e remissões específicas a arquivos e versões. Separar claramente instrumentos da viabilidade, rascunhos do protocolo principal e materiais ainda não produzidos. Não apresentar a bateria existente como conjunto-ouro nem exigir artificialmente seu congelamento final nesta etapa. Vínculo: `broad.submission-traceability`, apenas consultivo. A suficiência técnica dos instrumentos não é julgada por esta cadeira.

### Comentários detalhados

**Adequação e significância.** §§1.2, 1.5, 2.2 e 6.4 conectam avaliação documental a responsabilidades do uso público da informação. O recorte é compatível com contribuição aplicada de mestrado. A utilidade institucional permanece proposta, conforme o próprio texto; não se demonstraram efeitos sobre usuários, transparência ou implantação.

**Originalidade.** A contribuição pretendida é de articulação metodológica e investigação contextual. Não há necessidade de criar uma técnica inédita para justificá-la. A revisão narrativa reconhece em §3.2.1 que não demonstra inexistência de estudos semelhantes; essa limitação deve permanecer também na declaração de diferencial recomendada em W1. Este parecer não certifica novidade por busca bibliográfica externa.

**Estrutura e apresentação.** A sequência problema–literatura–procedimentos–caso–resultados–discussão permite acompanhar o projeto. A Figura 2 é corretamente apresentada como estimativa de dimensionamento; a Tabela 4, como notas automatizadas de viabilidade. Os problemas de fechamento e localização de instrumentos são os descritos em W3 e W4.

**Título, resumo e conclusão.** O título identifica objeto e caso de aplicação e não promete superioridade de desempenho. O resumo precisa esclarecer a etapa, conforme W2. A conclusão pode e deve sintetizar o estado da qualificação, sem simular resultados principais, conforme W3.

### Perguntas ao autor

1. Qual é o destinatário imediato do protocolo — avaliadores, equipe técnica ou gestores — e qual decisão concreta ele deverá conseguir tomar a partir da aplicação?
2. Entre os materiais já produzidos, quais versões da bateria, da rubrica e dos registros de execução serão apresentadas à banca como instrumentos de viabilidade, e quais permanecerão explicitamente preliminares para o experimento principal?

### Ajustes editoriais menores

- As remissões impressas como “Apêndice 7.4” em §§3.2.1, 3.2.2, 4.4 e 4.5 devem apontar para o Apêndice E.
- Em §§4.4, 5.1 e 6.3, substituir as crases literais usadas em nomes de modelos e parâmetros por formatação consistente; em §3.4, corrigir a composição de *kappa*, que aparece com letras espaçadas.
- Na Tabela 2, harmonizar a classificação da caracterização do corpus com o texto de §3.1, que explicita sua dimensão quantitativa descritiva.
- Na Tabela 5, esclarecer se o congelamento do corpus e a construção da bateria previstos para março de 2027 representam revisão das versões existentes ou criação de versões analíticas para o experimento principal.

Não foram identificados achados Critical ou Major no escopo deste parecer EIC; portanto, não há linhas a transportar para o artefato complementar `constructive-review-findings/1.0`. Isso não constitui julgamento das dimensões D1–D4 nem decisão editorial do painel.
