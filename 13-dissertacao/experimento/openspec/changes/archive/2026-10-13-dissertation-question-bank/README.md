# Verificação

O banco foi gerado por `scripts/prepare_question_bank.py`. A validação confirma:

- 200 perguntas canônicas sem IDs duplicados;
- 24 perguntas no piloto, duas em cada categoria principal;
- todos os IDs de fonte presentes no corpus Parquet;
- nenhum item marcado como validado automaticamente.

