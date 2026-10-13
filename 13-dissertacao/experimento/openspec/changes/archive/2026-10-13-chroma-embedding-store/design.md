# Desenho

`EmbeddingStore` usa `chromadb.PersistentClient`. Cada corpus e modelo geram uma coleção de documentos cuja chave contém o hash ordenado de IDs e textos. As consultas ficam em uma coleção por modelo, com o hash da consulta como ID. Manifestos JSON continuam sendo produzidos para inspeção e registro no SQLite.
