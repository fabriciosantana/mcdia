# E5 — Desenho

## Contexto e decisões

Adotar SQLite como fonte operacional, Chroma para embeddings e arquivos apenas para entrada inicial, backup e exportação. A UI chama serviços de domínio; não replica validação. Dependências: E2 e E4.

### Rubrica e afirmações

O sistema SHALL versionar as cinco dimensões 0–2 com âncoras, exemplos e limites; SHALL registrar afirmações centrais e seus vínculos de suporte completo/parcial/ausente, distinguindo contexto fornecido e referência do corpus.

### Avaliação independente

O sistema SHALL administrar avaliadores pseudonimizados, informação/ciência da finalidade, amostras estratificadas, atribuições, piloto, rodadas, submissão e adjudicação. A tela cega SHALL ocultar sistema, modelo, notas de outros avaliadores e juiz até submissão.

### Juiz fundamentado

O sistema SHALL enviar pergunta, resposta, contexto recuperado, referência apropriada e rubrica ao juiz, identificando quais evidências avaliam cada dimensão. SHALL persistir prompt próprio, hash correto, modelo/provedor, parâmetros e repetição.

### Pareamento e validade

O sistema SHALL selecionar explicitamente rodada humana, adjudicação e rodada do juiz para comparar notas; SHALL impedir produto cartesiano inadvertido e rejeitar booleanos como notas.

## Migração e riscos

Fazer backup consistente antes de migração; testar em cópia. Preservar registros e IDs legados por mapeamento explícito. Toda ambiguidade exige pendência visível, nunca inferência silenciosa. Segredos ficam em ambiente/referências seguras. Congelamento científico impede atualização destrutiva; arquivamento substitui exclusão de entidades referenciadas.

## Validação

Os cenários da spec são critérios de aceitação. Usar dados sintéticos e clientes falsos; teste de integração com SQLite/Chroma local. A validação estrutural OpenSpec não substitui execução dos testes.
