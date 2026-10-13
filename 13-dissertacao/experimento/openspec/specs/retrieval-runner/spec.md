# retrieval-runner Specification

## Purpose
O executor de recuperação aplica estratégias comparáveis a um conjunto de perguntas e documentos, preserva os rankings produzidos e calcula métricas reproduzíveis para cada execução.

## Requirements

### Requirement: Executar estratégia de recuperação
O sistema SHALL aceitar documentos, perguntas, referências e uma estratégia entre `bm25`, `tfidf` e `hybrid`, produzindo um ranking por pergunta.

#### Scenario: Execução válida
- **WHEN** os arquivos de entrada são válidos e a estratégia é suportada
- **THEN** o sistema cria uma execução e produz ranking para cada pergunta

#### Scenario: Estratégia desconhecida
- **WHEN** o usuário informa uma estratégia não suportada
- **THEN** o sistema rejeita a execução antes de criar resultados parciais

### Requirement: Calcular métricas de recuperação
O sistema SHALL calcular Recall@1, Recall@5, Recall@10 e MRR usando os documentos de referência de cada pergunta.

#### Scenario: Documento relevante no ranking
- **WHEN** um documento de referência aparece em uma posição do ranking
- **THEN** as métricas refletem a primeira posição relevante encontrada

#### Scenario: Pergunta sem referência
- **WHEN** uma pergunta é marcada como não respondível e não possui referência
- **THEN** o sistema registra a pergunta sem classificá-la como falha de recuperação respondível

### Requirement: Persistir resultados reproduzíveis
O sistema SHALL persistir estratégia, parâmetros, ranking, métricas, hashes das entradas e arquivo JSON detalhado associados à execução.

#### Scenario: Resultado registrado
- **WHEN** a execução termina
- **THEN** a consulta da execução retorna métricas e o caminho do artefato detalhado

#### Scenario: Entrada alterada
- **WHEN** os arquivos de documentos ou perguntas mudam após a execução
- **THEN** a validação identifica divergência pelos hashes registrados
