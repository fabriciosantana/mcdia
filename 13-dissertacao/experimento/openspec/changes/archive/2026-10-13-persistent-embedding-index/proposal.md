# Índice persistente de embeddings

## Objetivo

Persistir os embeddings do corpus e das consultas para que execuções repetidas do piloto reutilizem o mesmo índice vetorial e registrem sua proveniência.

## Escopo

- cache local de embeddings em artefatos NumPy e manifestos JSON;
- chaveamento por modelo e hash determinístico dos documentos ou da consulta;
- integração com a recuperação densa existente;
- testes de reutilização e invalidação do cache.

## Fora de escopo

- implantação de banco vetorial distribuído;
- alteração dos documentos brutos;
- treinamento ou ajuste fino de modelos.

## Critérios de aceitação

- uma segunda execução com o mesmo corpus, modelo e perguntas não chama novamente o endpoint de embeddings;
- mudança no corpus ou no modelo gera um novo artefato;
- o caminho do índice e seus metadados são registrados na execução;
- os testes existentes continuam aprovados.
