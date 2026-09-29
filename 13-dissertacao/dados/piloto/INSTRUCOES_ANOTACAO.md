# Instruções de anotação do conjunto de referência

## Unidade

A unidade é o par pergunta–documento/trecho. Um documento pode ter vários trechos relevantes; cada trecho deve preservar `id`, posição inicial e final no texto indexado.

## Campos obrigatórios

- `id_pergunta`: identificador estável;
- `categoria`: uma das 12 categorias do plano;
- `pergunta`: formulação final, sem copiar o resumo usado para escolher o documento;
- `respondibilidade`: `respondível` ou `não_respondível`;
- `documentos_referencia`: IDs dos pronunciamentos suficientes;
- `trechos_relevantes`: identificadores ou intervalos dos trechos;
- `grau_relevancia`: `2` suficiente, `1` parcialmente relevante, `0` irrelevante;
- `justificativa`: por que o documento/trecho sustenta a pergunta;
- `status`: `rascunho`, `validada` ou `revisar`.

## Regras

1. Não classificar um documento como relevante apenas por compartilhar palavras com a pergunta.
2. Para perguntas respondíveis, registrar ao menos um trecho suficiente; se houver mais de uma evidência necessária, registrar todas.
3. Para perguntas não respondíveis, deixar `documentos_referencia` vazio e registrar por que o corpus não fornece evidência suficiente.
4. Não transformar conhecimento externo em evidência do corpus.
5. Em caso de dúvida entre relevância total e parcial, usar `1` e explicar a dúvida.
6. Registrar ambiguidades de autoria, data, escopo e referência normativa.
7. A anotação deve ser feita antes de comparar os recuperadores.

## Controle de qualidade

A primeira rodada deve ser revisada pelo pesquisador. Quando houver segundo avaliador, comparar decisões por pergunta e resolver divergências em uma coluna própria, preservando as decisões originais.
