# Laboratório: Retrieval-Augmented Generation (RAG)

Este laboratório tem como objetivo **construir um ambiente local de RAG
(Retrieval-Augmented Generation)** utilizando ferramentas modernas do
ecossistema de IA generativa.

Ao final do laboratório, os alunos terão um sistema funcional capaz de:

-   Indexar documentos
-   Recuperar trechos relevantes
-   Utilizar modelos de linguagem para responder perguntas com base
    nesses documentos

A stack utilizada inclui:

-   Ollama -- gerenciamento de modelos locais (LLMs e embeddings)
-   Open WebUI -- interface gráfica para interação com LLMs
-   ChromaDB -- banco de dados vetorial
-   Docling -- extração de conteúdo de documentos
-   Modelos hospedados no Hugging Face

------------------------------------------------------------------------

# Estrutura da Aula

## 1. Apresentação Teórica

A aula começa com uma apresentação conceitual sobre **RAG
(Retrieval-Augmented Generation)** abordando:

-   Limitações de LLMs sem contexto
-   Conceito de recuperação semântica
-   Embeddings vetoriais
-   Bancos vetoriais
-   Pipeline RAG
-   Estratégias de re-ranking

------------------------------------------------------------------------

# 2. Laboratório

O laboratório consiste em montar **uma stack completa de RAG rodando
localmente**.

Arquitetura:

    Usuário
       │
       ▼
    Open WebUI
       │
       ├── Ollama (LLM + Embeddings + Reranker)
       │
       ├── ChromaDB (Vector Database)
       │
       └── Docling (Extração de conteúdo)

------------------------------------------------------------------------

# 2.1 Pré-requisitos

Instale previamente:

-   Git
-   Docker
-   VSCode (usado como terminal)

------------------------------------------------------------------------

# 2.2 Clonando o Repositório

Clone o repositório da disciplina:

``` bash
git clone https://github.com/marcelopita/ia_generativa_idp.git
```

O diretório clonado será a **raiz dos laboratórios da disciplina**.

Neste laboratório utilizaremos o diretório:

    2-rag

------------------------------------------------------------------------

# 2.3 Instalando Ollama (Bare Metal)

O **Ollama será instalado diretamente no host**, permitindo uso completo
da GPU.

Isso é especialmente importante para:

-   GPUs NVIDIA
-   Chips Apple Silicon que não suportam GPU em containers
    Docker.

Instale com:

``` bash
curl -fsSL https://ollama.com/install.sh | sh
```

------------------------------------------------------------------------

## Baixando os modelos

``` bash
ollama pull qwen3-embedding:0.6b
ollama pull llama3.2:3b
```

### Modelos utilizados

| Modelo                | Tipo            | Função no RAG                              | Parâmetros | Dimensão |
|----------------------|-----------------|---------------------------------------------|-----------|----------|
| `qwen3-embedding:0.6b` | Embedding Model | Converte textos em vetores para busca semântica | 600M      | 1024     |
| `llama3.2:3b`         | Language Model  | Gera respostas a partir do contexto recuperado | 3B        | —        |

## Variáveis importantes do Ollama

``` bash
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=2
```

Inicie o servidor:

``` bash
ollama serve
```

------------------------------------------------------------------------

## 2.3.1 Usando Ollama na Nuvem (opcional)

Crie o arquivo `.env` a partir do exemplo:

``` bash
cp .env.example .env
```

Para Ollama Cloud, ajuste:

``` bash
OLLAMA_BASE_URL=https://ollama.com
OLLAMA_API_KEY=seu_token_aqui
```

Observações:

-   Se quiser continuar local, mantenha:
    `OLLAMA_BASE_URL=http://localhost:11434`.
-   O modelo de embedding também pode ser alterado no `.env` via
    `RAG_EMBEDDING_MODEL`.

------------------------------------------------------------------------

## 2.3.2 Usando OpenAI para Embeddings (opcional)

No `.env`, ajuste:

``` bash
RAG_EMBEDDING_ENGINE=openai
RAG_EMBEDDING_MODEL=text-embedding-3-small
RAG_OPENAI_API_BASE_URL=https://api.openai.com/v1
RAG_OPENAI_API_KEY=seu_token_openai
```

Depois aplique:

``` bash
docker compose up -d
```

Observação importante:

-   Se trocar de modelo/dimensão de embedding (ex.: 1024 para 1536),
    crie um novo Knowledge ou reindexe do zero para evitar conflito de
    dimensão no ChromaDB.

------------------------------------------------------------------------

# 2.4 Subindo o restante da stack com Docker

Entre no diretório:

    2-rag

Execute:

``` bash
docker compose up -d
```

Saída esperada:

    [+] up 4/4
    ✔ Network 2-rag_default     Created
    ✔ Container docling-service Started
    ✔ Container chromadb        Started
    ✔ Container open-webui      Started

Para parar os serviços:

``` bash
docker compose down
```

------------------------------------------------------------------------

# 2.5 Adicionando modelos do Hugging Face no Open WebUI

Acesse o painel administrativo:

    Usuário → Painel do Admin → Configurações → Conexões → API OpenAI

Adicionar nova conexão:

    URL Base da API:
    https://router.huggingface.co/v1

    Chave da API:
    Token Hugging Face

------------------------------------------------------------------------

# 2.6 Configurando Docling no Open WebUI

    Usuário → Painel do Admin → Configurações → Documentos

Selecionar **Docling** como mecanismo de extração.

Configuração:

``` json
{
  "pipeline": "standard",
  "ocr": false,
  "table_structure": false,
  "do_layout_analysis": false,

------------------------------------------------------------------------

  "pdf_dpi": 150,
  "num_workers": 4,
  "max_pages": 200
}
```

------------------------------------------------------------------------

# 2.7 Configurando Chunking

    Usuário → Painel do Admin → Configurações → Documentos

Parâmetros:

    Tamanho de chunk: 800
    Sobreposição: 150

------------------------------------------------------------------------

# 2.8 Configurando Embeddings

    Usuário → Painel do Admin → Configurações → Documentos

Modelo:

    qwen3-embedding:0.6b

------------------------------------------------------------------------

# 2.9 Configurando Recuperação

    Usuário → Painel do Admin → Configurações → Documentos → Re-ranking

Parâmetros:

    Pesquisa híbrida: ativada
    Enriquecer texto da pesquisa: ativado
    Motor de reclassificação: Padrão (SentenceTransformers)
    Top K: 30
    Top K reclassificado: 5

------------------------------------------------------------------------

# 2.10 Configurando o Prompt RAG

    Usuário → Painel do Admin → Configurações → Documentos → Modelo RAG

Prompt:

    ### Task / Tarefa

    Answer the user's query using the provided context.
    Responda à pergunta do usuário utilizando o contexto fornecido.

    Use the context as the **primary source of information**.
    Use o contexto como **fonte primária de informação**.

    ---

    ### Guidelines / Diretrizes

    * Prefer information from the provided context over prior knowledge.
    Prefira informações presentes no contexto em vez de conhecimento prévio.

    * If the answer cannot be found in the context, clearly state that.
    Se a resposta não estiver no contexto, declare isso claramente.

    * If necessary, you may use your own knowledge, but explicitly state that the information does not come from the provided sources.
    Se necessário, você pode usar seu próprio conhecimento, mas indique explicitamente que a informação não vem das fontes fornecidas.

    * When multiple sources are relevant, synthesize them into a single coherent answer.
    Quando múltiplas fontes forem relevantes, sintetize-as em uma única resposta coerente.

    * Paraphrase information instead of copying long passages from the context.
    Parafraseie as informações em vez de copiar longos trechos do contexto.

    * If the context is unclear, incomplete, or low quality, inform the user.
    Se o contexto for confuso, incompleto ou de baixa qualidade, informe o usuário.

    * Ask the user for clarification if the question is ambiguous.
    Solicite esclarecimentos se a pergunta for ambígua.

    * Respond in the same language as the user's query.
    Responda no mesmo idioma da pergunta do usuário.

    ---

    ### Citations / Citações

    * Place the citation immediately after the statement it supports.
    Coloque a citação imediatamente após a frase que ela sustenta.

    * Do not include XML tags in the final answer.
    Não inclua tags XML na resposta final.

    ---

    ### Output / Saída

    Provide a clear and concise answer based on the context bellow, including citations when applicable.
    Forneça uma resposta clara e objetiva baseada no contexto abaixo, incluindo citações quando aplicável.

    <context>
    {{CONTEXT}}
    </context>

------------------------------------------------------------------------

# 2.11 Indexando a Base de Conhecimento

No Open WebUI:

    Workspace → Conhecimento → Novo Conhecimento

Configurar:

    Nome: PL 2338/2023
    Objetivo: Legislação da IA no Brasil

Adicionar documentos:

    Adicionar conteúdo → Carregar arquivos

Selecionar arquivos do diretório:

    docs_rag

------------------------------------------------------------------------

# 2.12 Perguntas de Teste

## Teste 1 -- Sem base de conhecimento

Pergunte no chat:

    Qual é o objetivo do PL 2338/2023?

------------------------------------------------------------------------

## Teste 2 -- Com base de conhecimento

Abra um chat **com a base selecionada**.

### Pergunta A

    Qual é o objetivo do PL 2338/2023?

Resposta esperada:

-   Regulação da IA
-   Proteção de direitos fundamentais
-   Promoção de inovação

------------------------------------------------------------------------

### Pergunta B

    Quais são as categorias de risco de sistemas de IA previstas no projeto?

Resposta esperada:

-   risco inaceitável (ou excessivo)
-   alto risco
-   risco mínimo (ou limitado)

------------------------------------------------------------------------

### Pergunta C

    O que caracteriza um sistema de IA de alto risco?

Resposta esperada:

Um sistema de IA é considerado **de alto risco** quando seu uso pode
afetar:

-   direitos fundamentais
-   segurança
-   acesso a serviços essenciais

especialmente em **contextos decisórios relevantes ou setores
sensíveis**.

------------------------------------------------------------------------

### Pergunta D

    Quem será a autoridade reguladora da IA segundo o projeto?

Resposta esperada:

O projeto propõe a criação de um **Sistema Nacional de Regulação e
Governança de Inteligência Artificial**, em vez de definir uma
autoridade única já existente.

------------------------------------------------------------------------

### Pergunta E

    Quais são as penalidades (mudar para "sanções" em seguida) previstas?

Resposta esperada:

-   Advertência
-   Multa simples
-   Multa diária
-   Publicização da infração
-   Bloqueio do sistema de IA
-   Proibição parcial ou total do sistema

------------------------------------------------------------------------

# Resultado Esperado

Ao final do laboratório, o aluno terá:

-   Um **ambiente RAG completo rodando localmente**
-   Pipeline de **extração → chunking → embeddings → busca → re-ranking
    → geração**
-   Capacidade de **consultar documentos com LLMs**

------------------------------------------------------------------------

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
