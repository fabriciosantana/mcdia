# Desenho

O índice será um artefato local composto por uma matriz `.npz` e um manifesto `.json`. A matriz dos documentos é identificada pelo hash ordenado de IDs e textos, além do nome do modelo. Embeddings de consultas são armazenados individualmente sob o mesmo diretório, identificados pelo hash do texto e do modelo.

O cache será criado em `data/embeddings`, separado do SQLite que registra as execuções. A execução continuará registrando os hashes dos documentos e das perguntas; o índice será registrado como artefato quando a recuperação densa for usada. A escrita será atômica para evitar arquivos parcialmente gravados.
