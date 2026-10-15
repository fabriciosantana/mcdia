# E1 — Implementação e aceitação concluídas

- [x] 1. Projetar migração de corpus_versions, documents, chunk_sets e vínculos versionados de document_chunks, com backup e relatório de reconciliação.
- [x] 2. Implementar importação transacional e distinção integral/resumo, exclusões, metadados e tokenizador.
- [x] 3. Implementar catálogo, comparação de versões, paginação e seleção contextual na interface.
- [x] Aplicar migrações 009–015 ao banco operacional com backup prévio: 94.360 chunks reconciliados, 15.726 documentos legados, 200 perguntas e `integrity_check=ok`.
- [x] Exercitar importação integral/resumo/sem texto, idempotência, filtros, paginação, contexto e persistência dos chunks.
- [x] Testar coexistência de segmentações, fonte alterada sob os mesmos IDs, imutabilidade dos chunks anteriores e rollback de fonte inválida.
- [x] Renderizar as abas do dashboard com Streamlit AppTest; os serviços de busca e seleção contextual passaram na aceitação sintética.
- [x] Confirmar os critérios de passagem automatizados; a aceitação não substitui revisão científica do corpus.
