# Registro de decisões

Use este arquivo para decisões que afetem problema, escopo, corpus, protocolo, métricas, modelos, baselines, avaliação humana ou interpretação. Cada registro deve conter data, decisão, justificativa, arquivos afetados e consequência para a redação.

## 2026-08-17 — estrutura inicial

- A dissertação usa o template institucional do IDP com opção `mestrado` e modo `rascunho`.
- A prova de conceito anterior é antecedente e ponto de partida, não resultado final.
- O protocolo avaliativo é o artefato metodológico principal; o sistema RAG é o caso empírico de aplicação.
- A estrutura separa trabalhos relacionados, artefato/caso, resultados e discussão para tornar explícita a cadeia problema--método--evidência--interpretação.

## 2026-08-18 — esquema canônico da base de discursos

- A nova coleta reproduziu os 15.729 códigos da base anterior, com 15.039 textos integrais, 690 respostas HTTP 404, 687 registros aproveitáveis por resumo e três registros sem conteúdo utilizável.
- O script de coleta passou a aplicar uma ordem canônica de colunas compatível com o dataset usado na prova de conceito e a ordenar campos de objetos aninhados antes da serialização em Parquet.
- Colunas novas eventualmente retornadas pela API serão preservadas, mas não poderão deslocar os campos canônicos de resultado.
- Os campos `__janela_inicio` e `__janela_fim` preservam as janelas mensais realmente consultadas. Eles não serão alterados para reproduzir artificialmente as janelas da coleta anterior.
- O Parquet reconsolidado em 18 de agosto de 2026 contém 15.729 registros únicos e possui SHA-256 `e09cfc4793e5394be440906320c7d3008cda5a52b90bbc85bf47446362406af1`.

## 2026-08-20 — consolidação metodológica após o notebook 01

- O notebook 01 é evidência da constituição, auditoria e caracterização do corpus; não é evidência de qualidade da recuperação ou da geração.
- Os 15.726 registros com texto integral ou resumo são considerados indexáveis, mas resumos de fallback deverão manter proveniência explícita e não serão tratados como equivalentes ao texto integral.
- As estimativas de chunking do notebook 01 servem apenas ao dimensionamento. Os chunks reais e a comparação de tamanhos e sobreposições serão produzidos no notebook 02.
- O notebook 02 iniciará o protocolo experimental pela recuperação, comparando BM25, busca vetorial e busca híbrida sob o mesmo conjunto de perguntas e julgamentos de relevância.
- A avaliação da geração será posterior e analiticamente separada da recuperação, preservando a distinção entre falha de busca, uso inadequado da evidência e extrapolação do modelo gerador.
- O capítulo metodológico passa a empregar tempos verbais diferentes para procedimentos concluídos e planejados, sem antecipar resultados experimentais.
