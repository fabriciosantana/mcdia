# E1 — Desenho

## Contexto e decisões

Adotar SQLite como fonte operacional, Chroma para embeddings e arquivos apenas para entrada inicial, backup e exportação. A UI chama serviços de domínio; não replica validação. Dependências: Nenhuma.

### Versões documentais

O sistema SHALL registrar corpus, versão, hash, documento, texto original, texto utilizado, tipo de fonte (integral/resumo), URL, autoria, data e cobertura dos demais metadados no SQLite. Exclusões e fallback SHALL ter motivo explícito.

### Segmentações coexistentes

O sistema SHALL identificar cada chunk por versão do corpus, configuração de segmentação e posição, preservando versões usadas por perguntas ou execuções. A configuração SHALL registrar tokenizador e versão, unidades, janela e sobreposição; a implementação atual por espaços SHALL ser identificada como legado.

### Curadoria navegável

O sistema SHALL oferecer busca paginada por texto, documento, autor, período e versão, com contexto anterior/posterior, texto completo, fonte e indicação de resumo.

### Migração preservadora

O sistema SHALL migrar chunks existentes sem descartar anotações; IDs legados ambíguos SHALL gerar pendência de reconciliação. Reimportação idêntica SHALL ser idempotente e falhas SHALL preservar a versão anterior.

## Migração e riscos

Fazer backup consistente antes de migração; testar em cópia. Preservar registros e IDs legados por mapeamento explícito. Toda ambiguidade exige pendência visível, nunca inferência silenciosa. Segredos ficam em ambiente/referências seguras. Congelamento científico impede atualização destrutiva; arquivamento substitui exclusão de entidades referenciadas.

## Validação

Os cenários da spec são critérios de aceitação. Usar dados sintéticos e clientes falsos; teste de integração com SQLite/Chroma local. A validação estrutural OpenSpec não substitui execução dos testes.
