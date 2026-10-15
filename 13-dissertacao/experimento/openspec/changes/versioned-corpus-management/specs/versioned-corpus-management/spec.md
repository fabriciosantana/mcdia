# Corpus e segmentações imutáveis

## ADDED Requirements

### Requirement: Versões documentais
O sistema SHALL registrar corpus, versão, hash, documento, texto original, texto utilizado, tipo de fonte (integral/resumo), URL, autoria, data e cobertura dos demais metadados no SQLite. Exclusões e fallback SHALL ter motivo explícito.

#### Scenario: Importar corpus pela interface
- **WHEN** um arquivo autorizado é importado uma única vez
- **THEN** documentos e cobertura são consultáveis sem reabrir o arquivo; três registros sem texto do corpus conhecido ficam contabilizados como excluídos, não desaparecem silenciosamente

### Requirement: Segmentações coexistentes
O sistema SHALL identificar cada chunk por versão do corpus, configuração de segmentação e posição, preservando versões usadas por perguntas ou execuções. A configuração SHALL registrar tokenizador e versão, unidades, janela e sobreposição; a implementação atual por espaços SHALL ser identificada como legado.

#### Scenario: Preparar outra janela
- **WHEN** um corpus já anotado recebe outra segmentação
- **THEN** as duas versões coexistem e a primeira referência mantém ID, conteúdo e hash; nenhuma exclusão por hash global ocorre

### Requirement: Curadoria navegável
O sistema SHALL oferecer busca paginada por texto, documento, autor, período e versão, com contexto anterior/posterior, texto completo, fonte e indicação de resumo.

#### Scenario: Inspecionar evidência
- **WHEN** o operador muda de página ou seleciona um trecho
- **THEN** filtros persistem, posições são ordenadas numericamente e o trecho pode ser associado à pergunta sem copiar IDs

### Requirement: Migração preservadora
O sistema SHALL migrar chunks existentes sem descartar anotações; IDs legados ambíguos SHALL gerar pendência de reconciliação. Reimportação idêntica SHALL ser idempotente e falhas SHALL preservar a versão anterior.

#### Scenario: Migrar os dados locais
- **WHEN** o esquema evolui após backup
- **THEN** contagens, textos, hashes e vínculos são conciliados em relatório, com restauração testada
