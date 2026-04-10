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

### 2. Precisao factual
- `2`: fatos, numeros, autores e temas corretos
- `1`: pequenos desvios ou formulacoes muito amplas
- `0`: erros factuais relevantes

### 3. Foco nas fontes
- `2`: usa trechos coerentes e pertinentes
- `1`: usa fontes validas, mas mistura demais ou inclui evidencias perifericas
- `0`: cita fontes incompatíveis ou aparentemente sem relacao

### 4. Sintese
- `2`: bem organizada, clara e proporcional
- `1`: correta, mas excessivamente longa, repetitiva ou burocratica
- `0`: confusa ou mal estruturada

### 5. Confianca / Alucinacao
- `2`: nao inventa e sinaliza limites quando necessario
- `1`: faz inferencias amplas, mas sem erros graves
- `0`: aparenta inventar ou extrapolar sem base

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
