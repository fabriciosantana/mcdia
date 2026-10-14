# Catálogo SQLite de perguntas e administração no dashboard

## Why

O banco de perguntas estava disponível apenas em CSV/JSON e a tabela `questions` só era preenchida no momento de uma execução. Isso obrigava a editar arquivos fora do aplicativo e não oferecia um catálogo persistente para curadoria.

## What Changes

- criar o catálogo `question_catalog` no SQLite;
- importar o banco inicial uma única vez;
- permitir cadastrar, editar, arquivar e validar perguntas no dashboard;
- executar experimentos selecionando perguntas validadas no catálogo;
- manter configurações e execuções administradas pelo SQLite e embeddings no ChromaDB.

## Fora de escopo

- apagar permanentemente perguntas que já participaram de execuções;
- substituir o corpus bruto por um catálogo de documentos nesta mudança.
