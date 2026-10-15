# Execução integral e geração rastreável

## ADDED Requirements

### Requirement: Plano de execução
O sistema SHALL administrar experimentos, configurações tipadas, prompts versionados e repetições com seleção de bateria, chunk set e índice no SQLite. SHALL mostrar parâmetros efetivos antes de iniciar e rejeitar combinações incompatíveis.

#### Scenario: Executar sem arquivos manuais
- **WHEN** o operador seleciona entidades cadastradas
- **THEN** recuperação e geração leem snapshots do banco; não exigem caminho JSONL nem edição de JSON

### Requirement: Tarefas persistentes
O sistema SHALL persistir etapas e estados queued/running/completed/failed/cancelled, heartbeat, checkpoints, erro e tentativas por item. Transações SHALL ser curtas e não abranger chamadas de rede. Retomada ou nova repetição SHALL ser explícita e idempotente.

#### Scenario: Reabrir após falha
- **WHEN** o aplicativo ou trabalhador reinicia durante geração
- **THEN** itens concluídos permanecem, itens incertos ficam identificados e a interface permite retomada sem duplicação silenciosa

### Requirement: Geração auditável
O sistema SHALL registrar pergunta, contexto ordenado exato, prompt completo e hash, versão da rubrica quando pertinente, modelo/provedor, parâmetros solicitados e efetivos, data, duração, uso e custo estimado ou indisponível. Contexto faltante SHALL bloquear geração.

#### Scenario: Gerar com evidência congelada
- **WHEN** o documento do catálogo foi revisado depois da recuperação
- **THEN** a resposta usa o snapshot original; ausência desse snapshot gera erro visível, sem descarte silencioso de IDs

### Requirement: Citações e orçamento
O sistema SHALL preservar chunk_id, document_id, URL e citação textual como campos distintos, identificar citações desconhecidas e administrar limites de custo/tempo antes de chamadas. Segredos SHALL permanecer fora dos snapshots e exportações.

#### Scenario: Inspecionar execução
- **WHEN** a geração retorna um identificador inexistente ou alcança limite de orçamento
- **THEN** a citação é marcada inválida e rastreável; novas chamadas são suspensas com estado e motivo, permitindo decisão do operador
