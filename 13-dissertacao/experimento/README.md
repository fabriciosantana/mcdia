# Centro de controle dos experimentos

Aplicativo local para preparar o corpus, curar perguntas e evidências, executar baselines RAG, gerar respostas, organizar avaliações humanas e do juiz, e exportar evidências da dissertação. SQLite é o registro operacional; ChromaDB armazena os vetores. O fluxo normal é pela interface, sem editar CSVs ou JSONs.

## Instalação e execução

```bash
python -m pip install -r requirements.txt
streamlit run dashboard/app.py
```

Configure `OPENAI_API_KEY`, `OPENAI_MODEL` e `OPENAI_EMBEDDING_MODEL` no ambiente ou em `.env` para geração e embeddings. BM25 pode ser executado sem credenciais. A interface abre em **Visão geral** e aplica migrações SQLite automaticamente.

## Fluxo de trabalho

1. Em **Experimentos → Preparar corpus e chunks**, importe JSONL ou Parquet e escolha tokenizador, janela e sobreposição. O arquivo é lido como fonte de importação; documentos, proveniência, metadados, exclusões e chunks ficam persistidos no SQLite. Versões e segmentações coexistem. O tokenizador `whitespace-regex` está identificado como legado.
2. Em **Banco de perguntas**, importe o catálogo inicial uma vez e edite as perguntas no SQLite. Elegibilidade, respondibilidade e validação são campos separados. Uma pergunta só entra em bateria congelada após decisão documentada e vínculo com a segmentação escolhida.
3. Em **Documentos e chunks**, filtre por texto, documento, autoria, data e versão. Selecione o trecho e associe-o à pergunta com grau 0–2, suficiência, justificativa e estado de revisão.
4. Em **Baterias**, crie uma composição ou importe o piloto de 24 perguntas por `source_question_id`. Revise itens, registre a decisão de respondibilidade para cada segmentação e congele a bateria antes da execução.
5. Em **Experimentos**, construa ou retome um índice Chroma. Escolha BM25, busca vetorial ou híbrida, bateria, segmentação e parâmetros; o aplicativo mostra os valores efetivos e salva um plano congelado. As tarefas rodam em worker local e persistem progresso e falhas.
6. Gere respostas para uma repetição explícita. O sistema usa o contexto recuperado congelado e guarda prompt, hash, parâmetros, duração, uso informado pelo provedor e citações. Antes das chamadas, estima tokens de entrada e aplica limites de tokens, chamadas e duração. Quando uma chamada fica incerta, o reenvio exige confirmação explícita.
7. Em **Avaliação humana → Gestão**, cadastre pseudônimos com códigos individuais, crie rodadas e distribua todas as respostas ou uma amostra estratificada reprodutível. O avaliador entra na **Sessão do avaliador**, que mostra pergunta, resposta, contexto, evidência de referência e rubrica sem exibir sistema, modelo ou notas alheias. Adjudicação cria novos registros e preserva os originais.
8. Configure e congele versões da rubrica e do protocolo H1–H3. Defina grupos simples/complexos e rodadas comparadas. Gere relatórios por pergunta, categoria e execução, com cobertura, denominadores, intervalos bootstrap, concordância e casos críticos. Baixe JSON, CSV e um `.tex` mínimo.
9. Gere um pacote de auditoria SQLite + Chroma e, se necessário, restaure-o em um diretório novo. O pacote remove códigos de acesso e substitui pseudônimos por aliases estáveis.

## Dados locais

- Registro SQLite: `data/experiment_registry.sqlite3`.
- Manifestos e artefatos derivados: `data/artifacts/` e `data/outputs/`.
- Coleções persistentes Chroma: `data/embeddings/chroma/`.
- Índice lexical BM25 versionado e comprimido: tabela `lexical_indexes` no SQLite.

Se a migração encontrar chunks do esquema anterior, cria primeiro `data/artifacts/experiment_registry-pre-versioned-corpus.sqlite3` e registra a reconciliação no banco. O registro legado é preservado para auditoria.

## OpenSpec e validação

As seis mudanças em `openspec/changes/` documentam corpus versionado, baterias curadas, recuperação, execução, avaliação e relatórios. Não as arquive antes de executar a aceitação sintética descrita em cada `tasks.md` e conciliar os resultados. Comandos úteis:

```bash
openspec list
openspec validate --all
openspec validate --changes
openspec validate --specs
```

Para repetir a aceitação integrada, com banco e dados sintéticos criados em diretório temporário, use:

```bash
python scripts/acceptance_synthetic.py
```

O roteiro aplica as migrações 001–015 num registro legado descartável, prepara corpus, congela bateria, constrói vetores Chroma determinísticos, executa BM25/denso/híbrido, gera e avalia respostas falsas, compila o relatório `.tex`, restaura SQLite + Chroma e verifica a renderização do dashboard. Requer as dependências de `requirements.txt` e `pdflatex`; não usa credenciais nem altera `data/experiment_registry.sqlite3`.

O modo administrativo é local e não tem autenticação geral. Os códigos dos avaliadores são armazenados como hashes e isolam as atribuições na sessão cega; compartilhe o endereço do dashboard somente com pessoas autorizadas.
