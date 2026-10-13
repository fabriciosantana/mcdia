# Proposta: centro de controle experimental

## Problema

A execução dependia de comandos no terminal e distribuía configuração, recuperação, geração e avaliação em arquivos separados. Isso aumenta o risco de registrar resultados de forma inconsistente.

## Mudança

Ampliar o dashboard Streamlit para concentrar configurações, execução de recuperação, geração de respostas, visualização de perguntas/respostas e avaliação humana. Os perfis de configuração passam a ser persistidos no SQLite.

## Resultado esperado

O piloto pode ser executado e avaliado por uma interface local, mantendo IDs, métricas, artefatos, citações e notas humanas no registro persistente.

