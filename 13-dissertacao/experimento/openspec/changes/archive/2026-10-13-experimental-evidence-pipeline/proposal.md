# Proposta: pipeline experimental orientado a evidências

## Why

O gerenciador atual executa apenas um piloto lexical simplificado. A dissertação exige conjunto de perguntas validado, evidência em nível de trecho, métricas de recuperação ampliadas, julgamento automatizado, concordância humana e artefatos de resultados reproduzíveis.

## What Changes

- adicionar ingestão e chunking de documentos com proveniência;
- ampliar o esquema de perguntas e resultados para categorias, trechos e relevância;
- calcular Precision@k, Hit@k e nDCG além das métricas existentes;
- registrar julgamentos automatizados e calcular concordância com avaliações humanas;
- exportar tabelas CSV e LaTeX para os capítulos de resultados;
- disponibilizar essas operações pela interface.

## Impact

As mudanças ampliam o registro SQLite, o dashboard e os módulos de execução, mantendo compatibilidade com as execuções existentes.

