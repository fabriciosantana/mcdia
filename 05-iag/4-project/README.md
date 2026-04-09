# 2.13 Importando batches por script

O projeto inclui um script para importar automaticamente os arquivos de
`knowledge_openwebui/md_batches/` para uma Knowledge Base do Open WebUI,
sem precisar fazer upload manual arquivo por arquivo na interface.

Arquivo:

-   `scripts/import_batches_to_openwebui.py`

Pré-requisitos no `.env`:

``` bash
OPENWEBUI_URL=http://localhost:8080
OPENWEBUI_API_KEY=sua_chave_da_api
```

## Listando o `knowledge_id`

O endpoint abaixo retorna as knowledges disponíveis:

``` bash
curl -s \
  -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
  "$OPENWEBUI_URL/api/v1/knowledge/" | jq
```

Exemplo de `knowledge_id`:

    902f627d-ab07-43bb-a395-8d573117f4fc

## Importando todos os batches

``` bash
python scripts/import_batches_to_openwebui.py \
  --knowledge-id 902f627d-ab07-43bb-a395-8d573117f4fc \
  --pattern 'knowledge_openwebui/md_batches/batch_*.md'
```

## Retomando de um batch específico

Exemplo a partir de `batch_00031.md`:

``` bash
python scripts/import_batches_to_openwebui.py \
  --knowledge-id 902f627d-ab07-43bb-a395-8d573117f4fc \
  --pattern 'knowledge_openwebui/md_batches/batch_*.md' \
  --start-from batch_00031.md
```

## Testando com poucos arquivos

``` bash
python scripts/import_batches_to_openwebui.py \
  --knowledge-id 902f627d-ab07-43bb-a395-8d573117f4fc \
  --pattern 'knowledge_openwebui/md_batches/batch_*.md' \
  --start-from batch_00031.md \
  --limit 3
```

## Estratégia contra erros 429

O script já inclui retry com backoff exponencial para erros de rate
limit da OpenAI na etapa de embeddings.

Exemplo mais conservador:

``` bash
python scripts/import_batches_to_openwebui.py \
  --knowledge-id 902f627d-ab07-43bb-a395-8d573117f4fc \
  --pattern 'knowledge_openwebui/md_batches/batch_*.md' \
  --start-from batch_00031.md \
  --max-add-retries 10 \
  --initial-backoff 15 \
  --max-backoff 180
```

## Resumo da execução

Ao final, o script informa:

-   quantidade de arquivos importados
-   quantidade de falhas
-   nomes dos arquivos importados com sucesso
-   nomes dos arquivos que falharam

------------------------------------------------------------------------

# 2.14 Avaliando o RAG por script

O projeto inclui um script para executar perguntas de avaliação contra a
Knowledge Base no Open WebUI usando a mesma collection anexada na
interface.

Arquivos:

-   `eval/discursos_questions.json`: conjunto inicial de perguntas
-   `eval/RUBRIC.md`: critérios de avaliação manual
-   `scripts/run_rag_eval.py`: executor dos testes

Pré-requisitos no `.env`:

``` bash
OPENWEBUI_URL=http://localhost:8080
OPENWEBUI_API_KEY=sua_chave_da_api
```

O script usa por padrão a knowledge:

    Discursos do plenário do Senado 2019-2023

## Rodando todos os testes

``` bash
python scripts/run_rag_eval.py
```

## Rodando apenas parte dos testes

Exemplo com as 3 primeiras perguntas:

``` bash
python scripts/run_rag_eval.py --limit 3
```

## Resultado da execução

Os resultados são gravados em:

-   `eval/results/*.jsonl`: resposta completa e payload retornado
-   `eval/results/*.md`: resumo legível para revisão humana

Exemplo de saída:

    Resultados salvos em:
    - /workspaces/.../eval/results/rag_eval_YYYYMMDDTHHMMSSZ.jsonl
    - /workspaces/.../eval/results/rag_eval_YYYYMMDDTHHMMSSZ.md

## Como revisar

1. Abra o arquivo `.md` gerado.
2. Compare cada resposta com a pergunta correspondente.
3. Use `eval/RUBRIC.md` para classificar:

-   aderência à pergunta
-   precisão factual
-   foco nas fontes
-   síntese
-   risco de alucinação

## Ajustes úteis

Trocar o modelo:

``` bash
python scripts/run_rag_eval.py --model gpt-5-nano
```

Adicionar pausa maior entre perguntas:

``` bash
python scripts/run_rag_eval.py --sleep-between 5
```
