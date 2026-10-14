# Desenho

`question_catalog` representa o banco operacional, com campos de proveniência, critérios, riscos, referências e estado de curadoria. A tabela `questions` continua sendo um snapshot por execução. A interface seleciona apenas registros `validada` e o executor copia esses registros para o snapshot da execução.

O JSON inicial é usado somente quando o catálogo SQLite está vazio. Depois da importação, as operações de manutenção usam exclusivamente o dashboard e o SQLite. O ChromaDB permanece responsável pelos embeddings persistentes.
