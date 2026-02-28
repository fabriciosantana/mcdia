# Llama 3.2 3B Instruct com Ollama

Configuração e exemplos de uso do modelo **meta-llama/Llama-3.2-3B-Instruct** via Ollama.

## O que é

Llama 3.2 3B é um modelo de linguagem compacto da Meta, ideal para:
- Prototipagem rápida
- Ambientes com recursos limitados
- Tarefas de NLP não triviais
- Fine-tuning experimental

---

## Comandos Executados

### 1. Verificar modelos instalados

```bash
ollama list
```

**Saída:**
```
NAME           ID              SIZE      MODIFIED
llama3.2:3b    a80c4f17acd5    2.0 GB    12 seconds ago
glm-5:cloud    c313cd065935    -         35 minutes ago
```

### 2. Baixar o modelo Llama 3.2 3B

```bash
ollama pull llama3.2:3b
```

**Saída:**
```
pulling dde5aa3fc5ff: 100% ▕██████████████████▏ 2.0 GB
pulling 966de95ca8a6: 100% ▕██████████████████▏ 1.4 KB
pulling fcc5a6bec9da: 100% ▕██████████████████▏ 7.7 KB
pulling a70ff7e570d9: 100% ▕██████████████████▏ 6.0 KB
pulling 56bb8bd477a5: 100% ▕██████████████████▏   96 B
pulling 34bb5ab01051: 100% ▕██████████████████▏  561 B
verifying sha256 digest
writing manifest
success
```

### 3. Instalar biblioteca Python ollama

```bash
pip install ollama
```

### 4. Testar o modelo via API

```bash
curl -s http://localhost:11434/api/chat -d '{"model": "llama3.2:3b", "messages": [{"role": "user", "content": "Diga: Configurado com sucesso!"}], "stream": false}'
```

**Saída:**
```
Sim, parece que a configuração foi bem-sucedida!
```

---

## Uso via Python

### Chat básico

```python
import ollama

response = ollama.chat(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": "Explique transformers."}]
)
print(response["message"]["content"])
```

### Com streaming

```python
for chunk in ollama.chat(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": "Conte uma piada."}],
    stream=True
):
    print(chunk["message"]["content"], end="", flush=True)
```

### Com parâmetros

```python
response = ollama.chat(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": "Gerar ideias criativas."}],
    options={
        "temperature": 0.9,
        "num_predict": 100,
        "top_p": 0.9,
    }
)
```

---

## Uso via API REST

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2:3b",
  "messages": [{"role": "user", "content": "Olá!"}],
  "stream": false
}'
```

---

## Arquivos

- `llama3_example.ipynb` - Notebook Jupyter com exemplos completos
- `README.md` - Este arquivo

---

## Próximos passos

1. **Fine-tuning**: Use `ollama create` com um Modelfile para customizar
2. **RAG**: Combine com embeddings para Q&A sobre documentos
3. **Agents**: Use com frameworks como LangChain ou CrewAI
4. **API**: Exponha via servidor para aplicações web

---

## Referências

- [Ollama Docs](https://ollama.ai/docs)
- [Llama 3.2 Model Card](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct)
- [ollama-python](https://github.com/ollama/ollama-python)

---

*Configurado por Neo 🤖 em 2026-02-28*

---

## Notebooks Disponíveis

| Notebook | Descrição |
|----------|-----------|
| `llama3_example.ipynb` | Exemplos usando **Ollama** (local, sem API key) |
| `huggingface_example.ipynb` | Exemplos usando **Hugging Face API** (cloud ou local com GPU) |

### Comparação: Ollama vs Hugging Face

| Aspecto | Ollama | Hugging Face API |
|---------|--------|------------------|
| **Instalação** | Local apenas | Cloud ou local |
| **GPU** | Opcional | Necessária para local |
| **API Key** | Não | Sim |
| **Rate limits** | Não | Sim (free tier) |
| **Latência** | Baixa (local) | Variável |
| **Custo** | Gratuito | Freemium |

---

*Atualizado por Neo 🤖 em 2026-02-28*
