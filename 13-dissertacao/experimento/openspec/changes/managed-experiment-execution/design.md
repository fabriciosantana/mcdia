# E4 — Desenho

## Contexto e decisões

Adotar SQLite como fonte operacional, Chroma para embeddings e arquivos apenas para entrada inicial, backup e exportação. A UI chama serviços de domínio; não replica validação. Dependências: E1, E2 e E3.

### Plano de execução

O sistema SHALL administrar experimentos, configurações tipadas, prompts versionados e repetições com seleção de bateria, chunk set e índice no SQLite. SHALL mostrar parâmetros efetivos antes de iniciar e rejeitar combinações incompatíveis.

### Tarefas persistentes

O sistema SHALL persistir etapas e estados queued/running/completed/failed/cancelled, heartbeat, checkpoints, erro e tentativas por item. Transações SHALL ser curtas e não abranger chamadas de rede. Retomada ou nova repetição SHALL ser explícita e idempotente.

### Geração auditável

O sistema SHALL registrar pergunta, contexto ordenado exato, prompt completo e hash, versão da rubrica quando pertinente, modelo/provedor, parâmetros solicitados e efetivos, data, duração, uso e custo estimado ou indisponível. Contexto faltante SHALL bloquear geração.

### Citações e orçamento

O sistema SHALL preservar chunk_id, document_id, URL e citação textual como campos distintos, identificar citações desconhecidas e administrar limites de custo/tempo antes de chamadas. Segredos SHALL permanecer fora dos snapshots e exportações.

## Migração e riscos

Fazer backup consistente antes de migração; testar em cópia. Preservar registros e IDs legados por mapeamento explícito. Toda ambiguidade exige pendência visível, nunca inferência silenciosa. Segredos ficam em ambiente/referências seguras. Congelamento científico impede atualização destrutiva; arquivamento substitui exclusão de entidades referenciadas.

## Validação

Os cenários da spec são critérios de aceitação. Usar dados sintéticos e clientes falsos; teste de integração com SQLite/Chroma local. A validação estrutural OpenSpec não substitui execução dos testes.
