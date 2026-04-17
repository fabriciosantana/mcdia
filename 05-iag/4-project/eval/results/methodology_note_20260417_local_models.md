# Nota metodologica curta - testes com modelos locais no Open WebUI

Data: 2026-04-17

## Objetivo

Avaliar se a separacao entre gerador e juiz altera materialmente os resultados e verificar se modelos locais expostos via Open WebUI podem ser usados de forma confiavel no protocolo A.

## Rodadas executadas

- [rag_eval_20260417T014653Z.csv](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260417T014653Z.csv:1)
  - Gerador: `gpt-5-nano`
  - Juiz: `gemma3:12b`
- [rag_eval_20260417T022327Z.csv](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260417T022327Z.csv:1)
  - Gerador: `gemma4:31b`
  - Juiz: `gemma4:31b`
- [rag_eval_20260417T024620Z.csv](/workspaces/mcdia/05-iag/4-project/eval/results/rag_eval_20260417T024620Z.csv:1)
  - Gerador: `gpt-5.4-nano`
  - Juiz: `gemma4:31b`

## Conclusoes

1. A troca de juiz altera materialmente a leitura dos resultados e, portanto, deve ser tratada como parte do protocolo metodologico, nao como detalhe operacional.
2. O `gemma3:12b` mostrou instabilidade operacional no papel de juiz, com respostas nulas em parte da bateria, o que inviabiliza seu uso como juiz principal no protocolo atual.
3. O `gemma4:31b` foi estavel operacionalmente como gerador e como juiz, inclusive em bateria completa com 20/20 perguntas `ok`.
4. Apesar dessa estabilidade, o `gemma4:31b` atribuiu `10/10` a todos os itens tanto no cenario `gemma4 -> gemma4` quanto no cenario `gpt-5.4-nano -> gemma4`, o que sugere um perfil de julgamento excessivamente leniente.

## Implicacao pratica

No estado atual do projeto, os testes recomendam:

- nao adotar `gemma3:12b` como juiz principal;
- nao adotar `gemma4:31b` como juiz principal sem validacao manual adicional;
- manter como referencia principal as rodadas de estabilidade ja consolidadas com o juiz baseline;
- usar os testes com modelos locais como evidencia metodologica de que o juiz escolhido influencia o experimento e precisa ser justificado explicitamente.
