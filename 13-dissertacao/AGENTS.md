# Instruções da dissertação

Este diretório contém a dissertação de mestrado em Administração Pública sobre técnicas de avaliação de sistemas RAG aplicadas a discursos parlamentares do Senado Federal.

## Fontes de contexto

- Pré-projeto: `../06-iag/5-project-paper/chatbot-rag-pre/`.
- Artigo/prova de conceito: `../06-iag/5-project-paper/chatbot-rag/`.
- Implementação e evidências: `../06-iag/4-project/`.
- Template institucional: `/workspaces/TemplateLatexIDP/`.

Antes de alterações substantivas, leia o arquivo afetado, `documentacao/MAPA_FONTES.md`, `documentacao/PLANO_REDACAO.md` e as instruções do diretório-fonte pertinente.

## Regras centrais

- `config/dados.tex` é a fonte única dos metadados.
- Não alterar `idp.cls`.
- Não inventar referências, dados, resultados, parâmetros, nomes de banca ou informações catalográficas.
- Diferenciar prova de conceito anterior, protocolo planejado e evidência final da dissertação.
- Manter recuperação, geração, avaliação humana e julgamento automatizado como camadas analíticas distintas.
- Tratar o sistema como artefato sociotécnico e calibrar as conclusões ao alcance das evidências.
- Todo capítulo primário deve ter parágrafo introdutório antes da primeira subseção.
- Compilar após alterações em `.tex` ou `.bib` com `latexmk -pdf main.tex`, verificar `aux/main.log` e confirmar a geração de `out/main.pdf`.

## Estado editorial

Os capítulos 1, 2 e 4 foram inicialmente reaproveitados do pré-projeto e ainda contêm linguagem prospectiva a ser atualizada conforme a execução. Os capítulos 3 e 5 a 8 são esqueletos editoriais com marcadores `TODO`. Resumo, abstract, dados da orientação, banca e ficha catalográfica permanecem pendentes.
