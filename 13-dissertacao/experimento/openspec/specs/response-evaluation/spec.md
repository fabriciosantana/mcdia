# response-evaluation Specification

## Purpose
A camada de respostas e avaliações relaciona geração, citações, evidências e julgamentos humanos para permitir análise de verificabilidade e qualidade do sistema RAG.

## Requirements

### Requirement: Registrar resposta e citações
O sistema SHALL registrar resposta, modelo, prompt, pergunta, execução e citações com identificadores dos documentos ou trechos usados.

#### Scenario: Resposta válida
- **WHEN** uma resposta contém pergunta, texto e execução existente
- **THEN** o sistema persiste a resposta e suas citações

#### Scenario: Execução inexistente
- **WHEN** uma resposta referencia uma execução desconhecida
- **THEN** o sistema rejeita a ingestão

### Requirement: Registrar avaliação humana
O sistema SHALL aceitar notas inteiras de 0 a 2 para correção factual, aderência ao contexto, suporte de citações, completude e insuficiência documental.

#### Scenario: Avaliação válida
- **WHEN** um avaliador envia notas válidas para uma resposta existente
- **THEN** o sistema persiste as cinco dimensões e observações

#### Scenario: Nota inválida
- **WHEN** uma nota está fora de 0–2 ou não é inteira
- **THEN** o sistema rejeita a avaliação sem alterar o registro

### Requirement: Consultar respostas e avaliações
O sistema SHALL permitir recuperar respostas, citações e avaliações vinculadas a uma execução.

#### Scenario: Consulta de execução
- **WHEN** o usuário seleciona uma execução no dashboard
- **THEN** a interface exibe respostas, citações e avaliações disponíveis
