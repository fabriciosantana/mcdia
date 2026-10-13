# Desenho

O pipeline será dividido em etapas persistentes: preparação documental, curadoria da bateria, recuperação, geração, avaliação e exportação. Cada etapa registra seus insumos por hash e mantém o vínculo entre discurso, chunk, pergunta, resposta e julgamento.

A preparação aceita JSONL e, quando pandas/pyarrow estiverem instalados, Parquet com as colunas canônicas do corpus. O chunking produz JSONL com `document_id`, `chunk_id`, texto e metadados.

A referência de cada pergunta será armazenada como JSON estruturado, preservando documentos e trechos com grau de relevância. A recuperação calculará métricas compatíveis com a granularidade disponível e deixará métricas não calculáveis explicitamente nulas.

Julgamentos automatizados usam um adaptador de provedor injetável, como o adaptador OpenAI já existente, e não substituem a avaliação humana. A concordância será calculada apenas quando houver pares correspondentes de dimensões.

A exportação gera CSV e fragmentos LaTeX determinísticos, vinculados ao run_id, para revisão antes da incorporação na dissertação.

