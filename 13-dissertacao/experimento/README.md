# Construção do experimento

Este diretório será usado para desenvolver a infraestrutura de apoio e execução dos experimentos da dissertação.

O escopo será separado em dois componentes:

- gerenciador de experimentos, responsável por configurações, execuções, dados persistentes, métricas e relatórios;
- sistema RAG de referência, responsável por indexação, recuperação, geração e registro das evidências.

As primeiras decisões de arquitetura e especificações serão registradas aqui antes da implementação.

## OpenSpec

A estrutura de especificações está em `openspec/`, com o schema `spec-driven` e regras específicas deste subprojeto em `openspec/config.yaml`.

Comandos úteis, executados a partir deste diretório:

```bash
openspec list
openspec validate --all
openspec validate --changes
openspec validate --specs
```

Cada mudança relevante deve ser proposta e especificada antes da implementação. As especificações permanentes ficam em `openspec/specs/`; propostas em andamento ficam em `openspec/changes/` e só devem ser arquivadas depois de implementadas e verificadas.

## Registro experimental inicial

A primeira implementação usa apenas a biblioteca padrão do Python e SQLite. As dependências de teste estão em `requirements.txt`.

Inicialize o banco local:

```bash
python -m experiment_registry.cli init
```

Crie uma execução sintética e um relatório JSON:

```bash
python -m experiment_registry.cli demo
```

O banco será criado em `data/experiment_registry.sqlite3` e o relatório em `data/outputs/demo-run.json`. Para listar execuções:

```bash
python -m experiment_registry.cli list
```

Os testes podem ser executados sem dependências externas:

```bash
python -m unittest discover -s tests -v
```

O registro atual implementa preparação de corpus e chunks, baselines BM25, TF-IDF, híbrido e recuperação densa por embeddings, geração via API Responses, julgamento automatizado auxiliar, concordância e persistência SQLite. A recuperação densa exige `OPENAI_EMBEDDING_MODEL` configurado. Seus embeddings são persistidos em coleções ChromaDB sob `data/embeddings/chroma`, identificadas pelo modelo e pelo hash do corpus; consultas repetidas também são reutilizadas. Manifestos JSON registram a coleção, o modelo, as dimensões e os IDs dos documentos. Quando o corpus ou o modelo muda, uma nova coleção é criada e o manifesto usado é registrado como artefato da execução.

## Pipeline de evidências

A aba **Experimentos** também prepara JSONL ou Parquet em chunks determinísticos, registra a proveniência e exporta tabelas CSV/LaTeX por execução. A aba **Questões e respostas** permite editar categoria, status de validação, trechos relevantes e notas de curadoria. O conjunto CSV só entra na recuperação quando a linha estiver marcada como `validada` (ou `validated`).

As métricas ampliadas incluem Precision@k, Hit@k e nDCG quando os julgamentos de relevância fornecem graus suficientes. O julgamento automatizado fica em tabela própria e a tela de execução calcula acordo exato e kappa ponderado apenas para respostas com avaliação humana e automática correspondentes.

O sistema também calcula intervalos de confiança por bootstrap com semente explícita, registra casos críticos por tipo e severidade e atribui citações somente quando o identificador da fonte aparece explicitamente na resposta gerada.

## Dashboard local

Instale as dependências do subprojeto e execute a interface:

```bash
python -m pip install -r requirements.txt
streamlit run dashboard/app.py
```

O dashboard é o centro de controle local do piloto. A aba **Visão geral** mostra execuções, métricas, respostas e avaliações; **Configurações** salva e consulta perfis JSON persistentes; **Experimentos** executa recuperação, gera respostas via LLM e valida artefatos; **Questões e respostas** permite consultar perguntas, respostas, citações e registrar as cinco avaliações humanas de 0 a 2. Depois de iniciar o Streamlit, o fluxo normal pode ser feito pela interface, sem executar os comandos de domínio no terminal. Ele é local e não possui autenticação ou acesso remoto configurado.

## Executor de recuperação

Entradas do executor:

- documentos em JSONL, uma linha por documento: `{"id": "doc-1", "text": "..."}`;
- perguntas em CSV com as colunas `question_id,query,reference_doc_ids`; múltiplas referências são separadas por `;`.

Execute um baseline:

```bash
python -m experiment_registry.cli run-retrieval \
  --documents /caminho/documentos.jsonl \
  --questions /caminho/perguntas.csv \
  --method bm25 \
  --name piloto-bm25
```

As estratégias disponíveis são `bm25`, `tfidf` e `hybrid`. Resultados, métricas e hashes das entradas são gravados no registro e em `data/outputs/`.

## Respostas e avaliações

Respostas geradas por qualquer modelo podem ser entregues em JSONL, sem dependência de provedor:

```json
{"run_id":"...","question_id":"q1","answer":"...","model":"modelo-local","prompt_hash":"...","citations":[{"document_id":"doc-1","chunk_id":"doc-1:0"}]}
```

Ingestão e consulta:

```bash
python -m experiment_registry.cli ingest-responses respostas.jsonl
python -m experiment_registry.cli responses RUN_ID
```

As avaliações humanas usam as cinco dimensões ordinais de 0 a 2: `factual_correctness`, `context_adherence`, `citation_support`, `proportional_completeness` e `insufficiency_recognition`.

## Geração via OpenAI

Com `OPENAI_API_KEY` e `OPENAI_MODEL` definidos em `.env`, gere respostas para uma execução de recuperação:

```bash
python -m experiment_registry.cli generate-responses RUN_ID \
  --documents documentos.jsonl \
  --model "$OPENAI_MODEL"
```

O adaptador usa a API Responses, registra o hash do prompt e associa os documentos recuperados como citações. Os testes usam um cliente falso; nenhuma chave é necessária para executar a suíte.
