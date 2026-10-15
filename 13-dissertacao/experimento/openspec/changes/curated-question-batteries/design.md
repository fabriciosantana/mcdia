# E2 — Desenho

## Contexto e decisões

Adotar SQLite como fonte operacional, Chroma para embeddings e arquivos apenas para entrada inicial, backup e exportação. A UI chama serviços de domínio; não replica validação. Dependências: E1.

### Integridade da pergunta

O sistema SHALL separar respondibilidade de elegibilidade experimental, normalizar booleanos explicitamente e preservar campos omitidos em edições parciais. A categoria parcial SHALL permanecer pendente de decisão documentada para sua projeção binária.

### Conjunto de referência

O sistema SHALL manter julgamentos por pergunta, versão de chunk, grau 0/1/2, suficiência, anotador, justificativa e revisão; não julgado SHALL ser diferente de irrelevante.

### Baterias versionadas

O sistema SHALL administrar baterias, membros e divisões piloto/avaliação final, congelando revisões e distribuição por categoria, ano, tamanho e tipo de fonte quando aplicável.

### Imutabilidade e administração

O sistema SHALL permitir criar, revisar, arquivar e restaurar perguntas e baterias; revisões após congelamento SHALL originar nova versão sem modificar snapshots de execuções anteriores.

## Migração e riscos

Fazer backup consistente antes de migração; testar em cópia. Preservar registros e IDs legados por mapeamento explícito. Toda ambiguidade exige pendência visível, nunca inferência silenciosa. Segredos ficam em ambiente/referências seguras. Congelamento científico impede atualização destrutiva; arquivamento substitui exclusão de entidades referenciadas.

## Validação

Os cenários da spec são critérios de aceitação. Usar dados sintéticos e clientes falsos; teste de integração com SQLite/Chroma local. A validação estrutural OpenSpec não substitui execução dos testes.
