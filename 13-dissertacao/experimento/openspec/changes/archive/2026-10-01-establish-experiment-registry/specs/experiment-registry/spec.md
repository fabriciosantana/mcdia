# Spec Delta

## Purpose

O registro de experimentos fornece uma fonte persistente e auditável para relacionar configurações, execuções, artefatos e métricas produzidos pelo protocolo avaliativo de RAG.

## ADDED Requirements

### Requirement: Criar uma execução identificável
O sistema SHALL criar uma execução com identificador único, nome legível, estado, horário de início e configuração associada.

#### Scenario: Iniciar execução
- **WHEN** o usuário fornece um nome e uma configuração válida
- **THEN** o sistema cria uma execução identificável no estado `created` e retorna seu identificador

#### Scenario: Rejeitar configuração ausente
- **WHEN** o usuário tenta criar uma execução sem configuração
- **THEN** o sistema rejeita a operação e informa o campo obrigatório ausente

### Requirement: Preservar configuração imutável
O sistema SHALL armazenar uma cópia serializada e um hash da configuração usada na execução, sem substituí-la quando novas configurações forem registradas.

#### Scenario: Registrar configuração
- **WHEN** uma execução é criada com parâmetros de corpus, recuperação, geração ou avaliação
- **THEN** o sistema persiste os parâmetros e o hash correspondente

#### Scenario: Repetir configuração
- **WHEN** duas execuções recebem configurações idênticas
- **THEN** cada execução mantém seu próprio identificador e o mesmo hash de configuração

### Requirement: Associar artefatos à execução
O sistema SHALL associar a uma execução os identificadores das perguntas, documentos, trechos, respostas, avaliações e arquivos derivados produzidos por ela.

#### Scenario: Registrar artefato
- **WHEN** um artefato é produzido durante uma execução
- **THEN** o sistema registra seu tipo, localização, hash e relação com a execução

#### Scenario: Artefato ausente
- **WHEN** um arquivo associado não existe ou seu hash não pode ser calculado
- **THEN** o sistema rejeita o registro e preserva a execução sem uma associação incompleta

### Requirement: Consultar e validar execuções
O sistema SHALL permitir listar execuções, recuperar uma execução por identificador e verificar a integridade dos hashes registrados.

#### Scenario: Listar execuções
- **WHEN** o usuário solicita a lista de execuções
- **THEN** o sistema retorna identificador, nome, estado, data e hash da configuração de cada execução

#### Scenario: Validar integridade
- **WHEN** o usuário executa a validação de uma execução
- **THEN** o sistema informa quais artefatos permanecem íntegros e quais foram alterados ou removidos
