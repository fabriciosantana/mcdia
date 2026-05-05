# RAG Evaluation Rubric

Use esta rubric para classificar cada resposta em uma planilha ou revisao manual.

## Escala

- `2`: bom
- `1`: aceitavel
- `0`: ruim

## Criterios

### 1. Aderencia a pergunta
- `2`: responde exatamente ao que foi perguntado
- `1`: responde parcialmente ou abre demais o escopo
- `0`: foge do foco

Para perguntas que pedem lista exaustiva, previsao, prova causal, valor exato ou informacao possivelmente ausente, uma boa resposta pode ser uma recusa parcial. Nesses casos, atribua `2` em aderencia quando a resposta reconhece explicitamente a impossibilidade, delimita o que o contexto permite afirmar e nao inventa a parte ausente.

### 2. Precisao factual
- `2`: fatos, numeros, autores e temas corretos
- `1`: pequenos desvios ou formulacoes muito amplas
- `0`: erros factuais relevantes

### 3. Foco nas fontes
- `2`: usa trechos coerentes e pertinentes
- `1`: usa fontes validas, mas mistura demais ou inclui evidencias perifericas
- `0`: cita fontes incompatíveis ou aparentemente sem relacao

Em perguntas nao respondiveis ou parcialmente respondiveis, nao penalize a resposta apenas por nao citar uma lista completa inexistente. Penalize apenas se ela nao usa nenhuma evidencia recuperada para justificar a delimitacao, ou se usa fontes sem relacao com a negativa.

### 4. Sintese
- `2`: bem organizada, clara e proporcional
- `1`: correta, mas excessivamente longa, repetitiva ou burocratica
- `0`: confusa ou mal estruturada

### 5. Confianca / Alucinacao
- `2`: nao inventa e sinaliza limites quando necessario
- `1`: faz inferencias amplas, mas sem erros graves
- `0`: aparenta inventar ou extrapolar sem base

Em perguntas-armadilha, de evidencia negativa ou de escopo impossivel, a resposta ideal deve recusar a parte nao sustentada, explicar o que falta e, quando util, oferecer apenas exemplos verificaveis. Nao reduza a nota por ausencia de nomes, valores, prazos ou listas completas quando a propria resposta justifica que esses dados nao aparecem no contexto.

## Decisao pratica

- `8 a 10`: pronta para uso
- `5 a 7`: utilizavel com supervisao
- `0 a 4`: precisa ajuste de prompt, retrieval ou pergunta

## Padroes comuns de erro

- Mistura excessiva de autores ou discursos
- Resposta mais ampla que a pergunta
- Generalizacao sem apoio suficiente
- Falta de citacoes ou citacoes mal distribuídas
- Nao reconhecer quando faltou informacao no contexto
- Penalizar abstencao correta em perguntas nao respondiveis
