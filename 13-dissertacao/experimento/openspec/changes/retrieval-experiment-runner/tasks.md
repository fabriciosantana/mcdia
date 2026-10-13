# Tasks

## 1. Persistência

- [x] 1.1 Criar migração para perguntas, resultados de recuperação e métricas; verificar banco temporário.
- [x] 1.2 Implementar funções de persistência e consulta dos resultados; verificar integridade referencial.

## 2. Executor

- [x] 2.1 Implementar leitura validada de JSONL/CSV e hashes de entrada; verificar erros de esquema.
- [x] 2.2 Implementar BM25 e TF–IDF e combinação híbrida; verificar ranking em corpus sintético.
- [x] 2.3 Implementar métricas Recall@1/5/10 e MRR; verificar casos respondível e não respondível.
- [x] 2.4 Integrar executor ao registro e gerar artefato JSON detalhado; verificar uma execução completa.

## 3. Interface e documentação

- [x] 3.1 Adicionar comando CLI para executar e consultar recuperação; verificar comando em corpus sintético.
- [x] 3.2 Exibir métricas agregadas no dashboard; verificar carregamento sem execução ativa.
- [x] 3.3 Documentar formato de entrada, comando e limitações; verificar instalação e execução limpa.

## 4. Fechamento

- [x] 4.1 Executar testes, compileall e `openspec validate --all`; registrar resultados.
