# Desenho

`prepare_documents` continuará produzindo o JSONL, mas também aplicará uma migração e gravará cada chunk em `document_chunks`. O `metadata_json` conterá caminho da fonte, janela, sobreposição e posição dos tokens. Antes de inserir uma nova preparação da mesma fonte, os chunks daquela fonte serão substituídos para evitar mistura de versões de segmentação.

O dashboard consultará o SQLite com filtros por `document_id` e texto, exibirá o identificador e o conteúdo e permitirá copiar o `chunk_id` para a curadoria manual.
