# E3 — Desenho

## Contexto e decisões

Adotar SQLite como fonte operacional, Chroma para embeddings e arquivos apenas para entrada inicial, backup e exportação. A UI chama serviços de domínio; não replica validação. Dependências: E1 e E2.

### Métricas por pergunta

O sistema SHALL distinguir Recall@k (evidências relevantes distintas recuperadas / evidências relevantes de referência), Hit@k, Precision@k, MRR e nDCG. Graus, ganho, denominador de precisão, tratamento de não julgados e política de duplicação SHALL ser versionados. Ausência de gold SHALL produzir não aplicável com motivo.

### Estratégias explícitas

O sistema SHALL disponibilizar BM25, busca vetorial Chroma e fusão lexical-vetorial configurável, mantendo TF-IDF e o híbrido lexical legado identificados separadamente. Parâmetros efetivos, k e filtros SHALL constar na execução.

### Índices Chroma administráveis

O sistema SHALL manter registro SQLite de índice, coleção, versão do corpus/chunks, provedor, modelo, dimensões, distância, parâmetros e estado. Construção em lotes SHALL registrar progresso, falhas e retomada explícita; falha de leitura SHALL NOT apagar coleção automaticamente.

### Identidade dos vetores

O sistema SHALL associar vetores e resultados por ID, validar contagem/dimensão/valores e consultar a coleção via busca vetorial parametrizada. Alteração do provedor ou dimensão SHALL gerar índice incompatível distinto.

## Migração e riscos

Fazer backup consistente antes de migração; testar em cópia. Preservar registros e IDs legados por mapeamento explícito. Toda ambiguidade exige pendência visível, nunca inferência silenciosa. Segredos ficam em ambiente/referências seguras. Congelamento científico impede atualização destrutiva; arquivamento substitui exclusão de entidades referenciadas.

## Validação

Os cenários da spec são critérios de aceitação. Usar dados sintéticos e clientes falsos; teste de integração com SQLite/Chroma local. A validação estrutural OpenSpec não substitui execução dos testes.
