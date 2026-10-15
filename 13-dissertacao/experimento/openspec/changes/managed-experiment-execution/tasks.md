# E4 — Implementação e aceitação concluídas

- [x] 1. Implementar configurações tipadas e precedência explícita de perfil/campos, com valores realmente enviados ao provedor.
- [x] 2. Criar worker local, filas SQLite, checkpoints e política explícita de retentativa, cancelamento e prevenção de clique duplo.
- [x] 3. Remover dependência operacional de JSONL na geração/recuperação; congelar entradas e armazenar requisição/resposta e citações.
- [x] Exercitar plano congelado, recuperação, snapshots de contexto e geração com cliente falso; verificar prompt, citações e metadados persistidos.
- [x] Testar resultado incerto, bloqueio de repetição implícita, reenvio explícito, contexto ausente, orçamento de tokens e duração.
- [x] Testar cancelamento/retomada, preservação dos itens concluídos e ausência de chamadas externas no preflight bloqueado.
- [x] Renderizar a interface de execução pelo Streamlit AppTest.
- [x] Confirmar os critérios de passagem automatizados; chamadas reais a LLM permanecem para o piloto controlado.
