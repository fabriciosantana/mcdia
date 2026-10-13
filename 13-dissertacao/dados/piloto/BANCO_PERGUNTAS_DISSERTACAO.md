# Banco de perguntas da dissertação

Arquivos gerados a partir de `discursos_questions_v4_200.json`:

- `banco_perguntas_dissertacao_v1.json/csv`: 200 perguntas candidatas normalizadas;
- `bateria_piloto_dissertacao_24_v1.json/csv`: 24 perguntas, duas por categoria principal;
- `banco_perguntas_dissertacao_v1.manifest.json`: hashes, contagens e proveniência.

Todas as perguntas estão com `status=rascunho`. A coluna `reference_doc_ids` contém candidatos importados da fonte v4; ela não representa ainda o conjunto-ouro. As colunas `reference_chunk_ids` e `relevance_judgments` permanecem vazias até a validação manual.

## Procedimento de validação

Para cada pergunta do piloto:

1. confirmar a formulação e a categoria;
2. confirmar `sim`, `parcial` ou `não` para respondibilidade;
3. localizar os chunks suficientes no corpus congelado;
4. registrar os `chunk_id` em `reference_chunk_ids`;
5. atribuir graus de relevância e justificar a decisão;
6. alterar o status para `validada` somente após a revisão.

A bateria pode então ser importada no gerenciador. Não reutilizar automaticamente as notas ou respostas das rodadas antigas do Open WebUI como evidência final.

