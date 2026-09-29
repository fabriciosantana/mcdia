# Plano da bateria de perguntas — piloto

## Objetivo

Construir um conjunto pequeno, balanceado e auditável para avaliar recuperação documental antes da avaliação da geração. A bateria inicial terá 24 perguntas: duas por cada uma das 12 categorias já previstas no protocolo. Este arquivo registra a estrutura; as perguntas atuais estão em `bateria_rascunho.csv` e ainda precisam de revisão humana.

## Categorias

1. factual;
2. foco no autor;
3. desambiguação;
4. evidência negativa;
5. comparação entre autores;
6. comparação temporal;
7. pergunta numérica;
8. síntese temática;
9. múltiplas etapas;
10. autoria cruzada;
11. controle de escopo;
12. estresse de recuperação.

A planilha contém duas formulações rascunhadas por categoria para iniciar a curadoria. Ambas precisam ser revisadas, mantendo equilíbrio por ano e extensão documental.

## Distribuição provisória

- 18 perguntas com evidência candidata no corpus;
- 6 perguntas não respondíveis ou fora do escopo, a confirmar pela curadoria;
- dentro das respondíveis, quatro categorias exigem múltiplos documentos.

A distribuição final deve ser registrada antes da execução e não pode ser alterada em função dos resultados de recuperação.

## Critérios de seleção

A seleção cobre 2019–2023, inclui documentos de anos distintos e preserva os identificadores originais. A planilha `documentos_candidatos.csv` registra os documentos usados como âncoras. A seleção é um ponto de partida, não uma amostra representativa da atividade parlamentar.

## Próxima decisão

Reescrever as perguntas em linguagem independente dos resumos, confirmar respondibilidade, indicar os trechos suficientes e preencher a segunda pergunta de cada categoria. Somente linhas com `status=validada` devem alimentar o conjunto-ouro. Até essa validação, o notebook continua usando as consultas provisórias anteriores.
