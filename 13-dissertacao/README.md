# Dissertação — técnicas de avaliação de sistemas RAG

Base LaTeX da dissertação de Fabricio Fernandes Santana no Mestrado em Administração Pública do IDP. A estrutura usa a classe institucional `idp.cls` e reaproveita, de forma rastreável, o pré-projeto, o artigo de prova de conceito e os artefatos da implementação.

## Compilação

```bash
latexmk -pdf main.tex
latexmk -c
```

O documento está em modo `rascunho`. Campos institucionais ainda desconhecidos aparecem como pendências; a opção `entrega` só deve ser ativada após seu preenchimento e conferência.

## Onde escrever

- `config/dados.tex`: metadados, orientação, banca e ficha catalográfica;
- `capitulos/`: texto principal;
- `pretextual/`: resumo, abstract e siglas;
- `postextual/`: apêndices e anexos;
- `figuras/`: imagens;
- `documentacao/`: mapa de fontes, decisões e plano de redação.

Consulte `documentacao/PLANO_REDACAO.md` antes de iniciar um capítulo e mantenha `documentacao/DECISOES.md` atualizado quando houver mudança relevante de escopo, método ou configuração experimental.
