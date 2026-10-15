# Avaliação humana e juiz com evidências

## ADDED Requirements

### Requirement: Rubrica e afirmações
O sistema SHALL versionar as cinco dimensões 0–2 com âncoras, exemplos e limites; SHALL registrar afirmações centrais e seus vínculos de suporte completo/parcial/ausente, distinguindo contexto fornecido e referência do corpus.

#### Scenario: Avaliar verificabilidade
- **WHEN** uma resposta mistura afirmações apoiadas e extrapolação
- **THEN** cada afirmação central e evidência podem ser anotadas sem reduzir verificabilidade à presença de citação

### Requirement: Avaliação independente
O sistema SHALL administrar avaliadores pseudonimizados, informação/ciência da finalidade, amostras estratificadas, atribuições, piloto, rodadas, submissão e adjudicação. A tela cega SHALL ocultar sistema, modelo, notas de outros avaliadores e juiz até submissão.

#### Scenario: Avaliar com dois humanos
- **WHEN** dois avaliadores recebem a mesma resposta
- **THEN** ambos têm pergunta e evidências, não veem notas alheias e seus registros originais sobrevivem à adjudicação

### Requirement: Juiz fundamentado
O sistema SHALL enviar pergunta, resposta, contexto recuperado, referência apropriada e rubrica ao juiz, identificando quais evidências avaliam cada dimensão. SHALL persistir prompt próprio, hash correto, modelo/provedor, parâmetros e repetição.

#### Scenario: Julgar sem contexto
- **WHEN** um snapshot obrigatório está ausente
- **THEN** o julgamento é bloqueado e não gera nota; com contexto válido, a requisição pode ser reconstruída sem usar o hash da geração

### Requirement: Pareamento e validade
O sistema SHALL selecionar explicitamente rodada humana, adjudicação e rodada do juiz para comparar notas; SHALL impedir produto cartesiano inadvertido e rejeitar booleanos como notas.

#### Scenario: Repetir julgamentos
- **WHEN** uma resposta tem dois humanos e duas rodadas do juiz
- **THEN** o relatório informa unidades e pares escolhidos e não chama quatro linhas de quatro respostas independentes
