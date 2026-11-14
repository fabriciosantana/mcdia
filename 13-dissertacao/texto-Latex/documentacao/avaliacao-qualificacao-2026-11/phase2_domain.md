# Parecer de domínio — Peer Reviewer 2

criteria_parallel_conflicts: []
[REVIEW-TARGET-BINDING v1]
target_review_id=qualification-dissertacao-2026-11
consumer_id=external_panel
role=R2
context_ref=context.json
context_sha256=358b5370cead2090411589c48f05a3aa5234d12ef291f9d9d6ecb414ac21b320
resolved_digest=6f675cd7c2eed7118e7d5f65c5e9073367d48f17a8a92797d5df181e6e8ed70e
selected_criterion_ids=["broad.claim-evidence-alignment","broad.limitation-calibration","broad.method-evidence-alignment","broad.submission-traceability"]
[/REVIEW-TARGET-BINDING]

contract_role: domain
## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: warn
trigger: "Imprecisão terminológica localizada, referência relevante ausente ou contextualização insuficiente de uma afirmação secundária requer correção delimitada, sem alterar o entendimento dos conceitos centrais ou a contribuição proposta."

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

### Identidade e escopo

Perspectiva simulada de pesquisador em Ciência da Informação e informação legislativa, com foco em recuperação da informação e acervos parlamentares.

Foram lidos integralmente o manuscrito compilado, incluindo referências e apêndices, e os trechos pertinentes do código LaTeX. A avaliação considera uma dissertação em qualificação: procedimentos prospectivos não são tratados como resultados ausentes de um estudo concluído. Não foram consultados pareceres de outros avaliadores.

A verificação externa foi pontual: caracterizações de ARES e LegalBench-RAG nas páginas primárias das versões citadas. As demais descrições da literatura foram examinadas quanto à integração e consistência no manuscrito, sem certificação bibliográfica ou factual integral.

### Recomendação do papel

**Minor Revision**, restrita ao domínio. As correções identificadas preservam a pergunta, o objeto empírico e a proposta de protocolo. Não foi identificado achado Critical ou Major nesta avaliação.

### Confiança

**4/5 — domínio principal: recuperação da informação e interpretação documental.** A confiança não equivale à verificação integral das referências, dos dados ou da implementação.

### Calibration Status

`NOT_CALIBRATED`

### Criterion-Bound Judgements

| Dimensão / critério | Fonte do critério | Julgamento | Âncoras | Fundamentação | Limite | Incidência |
|---|---|---|---|---|---|---|
| D2 / correspondência entre alegações e evidências | Manifesto: `broad.claim-evidence-alignment@1.0` | PARTLY_MEETS | `table: Tabela 1, p. 24, linhas ARES e LegalBench-RAG`; `text: §3.4, p. 38, “ao menos uma evidência suficiente”` | A fundamentação sustenta a separação das camadas avaliativas, mas duas caracterizações bibliográficas e um rótulo conceitual precisam de correção. | Conferência externa limitada às duas fontes identificadas. | Sim: fundamenta correções delimitadas em D2. |
| D2 / calibração das limitações documentais | Manifesto: `broad.limitation-calibration@1.0` | PARTLY_MEETS | `table: Tabela 3, p. 44, disponibilidade textual`; `text: §3.2.3, p. 32, “deverá confirmar-se a ausência de suporte no recorte”` | O texto reconhece cobertura parcial e resultados preliminares; falta precisar o universo documental ao declarar não respondibilidade. | Não foi auditada a completude histórica da coleta. | Sim: esclarecimento localizado, sem invalidar o corpus. |
| Adequação técnica de métodos e evidências | Manifesto: `broad.method-evidence-alignment@1.0` | NOT_ASSESSED | — | O julgamento técnico pertence ao avaliador de metodologia. | D1 não elegível para este papel. | Não neste parecer. |
| Rastreabilidade geral da submissão | Manifesto: `broad.submission-traceability@1.0` | NOT_ASSESSED | — | Não foi realizada auditoria integral dos artefatos nem de requisitos institucionais. | Critério consultivo; normas específicas do IDP não fornecidas. | Não neste parecer. |

### Avaliação sintética

A dissertação propõe organizar técnicas de avaliação de RAG e aplicá-las a discursos da 56ª Legislatura do Senado Federal. O manuscrito apresenta caracterização documental e execuções de viabilidade, enquanto reserva a comparação controlada e os julgamentos humanos para o experimento principal. Sua principal qualidade de domínio está em distinguir recuperação, geração e julgamento, tratando autoria, proveniência e insuficiência documental como elementos substantivos da avaliação.

O referencial combina fundamentos de recuperação da informação, estudos sobre avaliação de RAG e contextualização parlamentar. A diferenciação entre texto integral e resumo substituto e a recusa em interpretar notas automatizadas como validação independente ajudam a delimitar corretamente o alcance das evidências. A contribuição pretendida é uma adaptação contextual e uma articulação de instrumentos existentes, não uma nova arquitetura ou demonstração de superioridade já concluída.

As fragilidades encontradas são delimitadas. A Tabela 1 atribui dimensões imprecisas a ARES e amplia o objeto avaliado por LegalBench-RAG. Além disso, o indicador de H1 usa pertinência como rótulo de suficiência, e a declaração de não respondibilidade precisa explicitar o universo documental considerado. Essas questões justificam revisão menor no domínio. A avaliação estatística das hipóteses, a exequibilidade integral e a decisão sobre a qualificação permanecem fora da competência decisória deste parecer.

### S1: Separação conceitual das dimensões avaliativas

O manuscrito define groundedness em relação ao contexto recuperado e apresenta a rubrica como síntese construída para o estudo. Isso permite distinguir uma adaptação autoral da reprodução de um instrumento já validado.

**Evidence Anchor**: text: §2.3, p. 22 — “Essa composição é uma síntese operacional, e não uma rubrica canônica única”.

### S2: Tratamento substantivo da proveniência e da cobertura documental

A caracterização diferencia texto integral, resumo substituto e ausência de conteúdo. Também explica por que essas modalidades não sustentam inferências equivalentes. Essa distinção é pertinente para avaliar respostas sobre registros parlamentares, especialmente quando a pergunta exige detalhes ausentes de um resumo.

**Evidence Anchor**: table: Tabela 3, p. 44 — 15.039 registros com texto integral, 687 com resumo substituto e três sem conteúdo utilizável.

### S3: Interpretação prudente dos resultados automatizados

O texto distingue execução operacional de desempenho validado e reconhece a dependência entre geração e julgamento pelo mesmo modelo. O risco de mistura de autores também é apresentado como sinal para inspeção, sem ser convertido automaticamente em erro confirmado.

**Evidence Anchor**: text: §5.1, p. 49 — “Não demonstram desempenho validado nem testam as hipóteses da dissertação.”

### S4: Limitação explícita do alcance da revisão narrativa

A revisão declara seu caráter intencional e sua concentração em processamento de linguagem natural. Isso permite sustentar a seleção de instrumentos sem transformar o levantamento em prova de inexistência de pesquisas anteriores.

**Evidence Anchor**: text: §3.2.1, p. 30 — “não comprova a inexistência de estudos semelhantes nem é apresentada como revisão sistemática”.

### W1: A Tabela 1 não representa corretamente as dimensões de ARES

**Severity**: Minor  
**Evidence Anchor**: table: Tabela 1, p. 24, linha ARES, coluna Foco de avaliação — Groundedness, correção e completude; fonte LaTeX `02-referencial-teorico.tex`, linha 56.  
**Confidence**: 5 — comparação direta com a descrição primária do framework.

**Problema e relevância:** ARES apresenta as dimensões *context relevance*, *answer faithfulness* e *answer relevance*. Correção e completude não reproduzem essa enumeração. A diferença importa porque a tabela explica a origem dos critérios escolhidos para a dissertação. A descrição primária confirma essas três dimensões. [ARES, NAACL 2024](https://aclanthology.org/2024.naacl-long.20/)

**Correção mínima:** apresentar relevância do contexto, fidelidade da resposta e relevância da resposta como dimensões do framework. Explicar separadamente quais adaptações sustentam a rubrica da dissertação. A declaração de síntese operacional em §2.3 permite fazer essa correção sem substituir o protocolo.

### W2: A Tabela 1 amplia o objeto avaliado por LegalBench-RAG

**Severity**: Minor  
**Evidence Anchor**: table: Tabela 1, p. 24, linha LegalBench-RAG, coluna Foco de avaliação — Recuperação e resposta fundamentada; fonte LaTeX `02-referencial-teorico.tex`, linha 57.  
**Confidence**: 5 — comparação direta com a apresentação primária do benchmark.

**Problema e relevância:** LegalBench-RAG foi concebido para avaliar a etapa de recuperação, com localização precisa de segmentos relevantes. Sua contribuição pode favorecer respostas fundamentadas, mas esse benefício esperado não equivale à avaliação da resposta gerada. A tabela atualmente aproxima essas duas coisas. [LegalBench-RAG, versão de 2024](https://arxiv.org/abs/2408.10343v1)

**Correção mínima:** identificar o foco como recuperação de segmentos jurídicos relevantes e apresentar a fundamentação da resposta como finalidade posterior. Preservar a contribuição do estudo à escolha da unidade recuperável.

### W3: O rótulo de pertinência em H1 designa suficiência

**Severity**: Minor  
**Evidence Anchor**: text: §3.4, p. 38 — “recuperação pertinente” e “ao menos uma evidência suficiente”; fonte LaTeX `03-procedimentos-metodologicos.tex`, linha 149.  
**Confidence**: 5 — contraste com as definições explícitas do próprio manuscrito.

**Problema e relevância:** A seção 3.3.1 distingue unidades relevantes de unidades suficientes e prevê conjuntos complementares de evidências. Entretanto, §3.4 denomina recuperação pertinente um indicador definido por evidência suficiente. O rótulo pode levar o leitor a interpretar ausência de suficiência como ausência de relevância, embora um trecho possa ser pertinente e incompleto.

**Correção mínima:** alinhar o nome do indicador ao construto efetivamente medido e remeter à convenção já prevista para evidências complementares. Se H1 pretende tratar pertinência e suficiência separadamente, explicitar essa opção conceitual. Não é necessário introduzir outra métrica apenas para resolver a terminologia; a adequação técnica da operacionalização cabe ao parecer metodológico.

### W4: A não respondibilidade precisa de um universo documental inequívoco

**Severity**: Minor  
**Evidence Anchor**: text: §3.2.3, p. 32 — “deverá confirmar-se a ausência de suporte no recorte”; fonte LaTeX `03-procedimentos-metodologicos.tex`, parágrafo sobre curadoria do conjunto de referência.  
**Confidence**: 4 — interpretação documental apoiada nas limitações de cobertura declaradas.

**Problema e relevância:** A formulação não esclarece suficientemente se a ausência será estabelecida no corpus congelado disponível, nos documentos oficiais completos ou no contexto efetivamente fornecido ao gerador. Esses universos diferem: o próprio manuscrito registra resumos substitutos e documentos sem conteúdo utilizável. Uma ausência no material disponível não demonstra ausência de manifestação parlamentar no período.

**Correção mínima:** delimitar expressamente a não respondibilidade ao universo documental avaliado e distinguir ausência de suporte no corpus de falha de recuperação. Nos itens afetados por cobertura incompleta, registrar a limitação documental na decisão de curadoria. A correção aproveita a caracterização já existente, sem exigir que a qualificação apresente uma busca histórica exaustiva.

### Comentários detalhados

**Revisão da literatura.** Há cobertura pertinente de fundamentos, frameworks, benchmarks e aplicações parlamentares. A síntese distingue tarefas e evita agregar resultados de estudos heterogêneos como se fossem diretamente comparáveis. As correções W1 e W2 devem preservar essa diferenciação também na tabela. Não identifiquei uma referência ausente cuja inclusão pudesse ser exigida com segurança a partir desta revisão delimitada.

**Referencial conceitual.** A separação entre recuperação documental, geração e julgamento é adequada à pergunta. Sua aplicação aparece na distinção entre documento, trecho e afirmação, na análise das citações e no tratamento da insuficiência. O diálogo com Design Science Research pode permanecer como enquadramento declarado; este parecer não exige adoção de outro modelo teórico. Como alternativa de apresentação, as relações entre consulta, documento, trecho, afirmação e fonte poderiam ser explicitadas em um esquema conceitual, sem acrescentar uma nova teoria.

**Precisão dos argumentos.** Os resultados preliminares são interpretados com cautela. O manuscrito não confunde notas do juiz com métricas de recuperação nem trata o corpus como representação probabilística das consultas dos usuários. W3 e W4 apontam os locais onde a terminologia ainda precisa acompanhar essa cautela.

**Contribuição ao domínio.** O valor potencial está em mostrar como técnicas existentes se complementam diante de autoria, temporalidade, granularidade e cobertura documental em um acervo parlamentar brasileiro. Essa contribuição permanece prospectiva quanto ao experimento principal. O texto deve conservar essa delimitação ao apresentar posteriormente os resultados.

**Referências a conferir.** As duas obras abaixo já estão na bibliografia; recomenda-se corrigir sua representação, não acrescentá-las como referências novas.

~~~yaml suggested-references
- title: "ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems"
  authors: ["Saad-Falcon, J.", "Khattab, O.", "Potts, C.", "Zaharia, M."]
  year: "2024"
  doi: "10.18653/v1/2024.naacl-long.20"
  arxiv_id: null
- title: "LegalBench-RAG: A Benchmark for Retrieval-Augmented Generation in the Legal Domain"
  authors: ["Pipitone, N.", "Houir Alami, G."]
  year: "2024"
  doi: "10.48550/arXiv.2408.10343"
  arxiv_id: "2408.10343"
~~~

### Perguntas ao autor

1. Na dimensão correção factual, o julgamento incidirá sobre a fidelidade do relato ao que o parlamentar afirmou ou também sobre a verdade externa do conteúdo afirmado? Como a rubrica distinguirá uma atribuição documental correta de uma resposta que endossa a alegação do discurso?
2. Em H1, evidência identificável significa evidência efetivamente incluída no contexto recebido pelo gerador ou também conteúdo acessível no documento original pela URL? Essa escolha pode alterar a classificação de uma resposta verificável.
3. Caso um pronunciamento contenha citação de terceiros ou intervenção de outro participante, como será distinguido o autor do registro da pessoa a quem a afirmação deve ser atribuída?

### Questões editoriais menores

- Na Tabela 1, a expressão “idioma não parlamentar”, na linha RAGTruth, mistura idioma e domínio. Explicitar qual limitação de transferência se pretende indicar.
- As remissões impressas como “Apêndice 7.4”, por exemplo em §3.2.1, devem apontar para a identificação correta do apêndice de reprodução.
- Em §3.3.2, verificar se “abstinência” deve ser “abstenção”, conforme o comportamento de não responder que o protocolo pretende designar.
