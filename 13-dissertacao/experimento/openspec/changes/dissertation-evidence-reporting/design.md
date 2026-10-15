# E6 — Desenho

## Contexto e decisões

Adotar SQLite como fonte operacional, Chroma para embeddings e arquivos apenas para entrada inicial, backup e exportação. A UI chama serviços de domínio; não replica validação. Dependências: E3, E4 e E5.

### Protocolo analítico congelado

O sistema SHALL registrar decisões H1–H3, grupos, contrastes, regra para parcial/não respondível, pesos kappa, bootstrap, exclusões e desfechos antes da análise confirmatória. Alterações SHALL ser versionadas e identificadas como posteriores.

### Resultados vinculados às hipóteses

O sistema SHALL produzir matriz H1 com casos e afirmações, contrastes H2 por grupos/dimensões e concordância H3 por avaliador/rodada, incluindo falsos positivos/negativos definidos no protocolo. Estatísticas SHALL informar denominadores, faltantes e não aplicáveis.

### Incerteza e concordância

O sistema SHALL calcular kappa ordinal com pesos declarados e resultado não estimável quando o denominador for zero. Bootstrap SHALL respeitar unidade pergunta e pareamento entre condições, sem tratar repetições como novas perguntas independentes.

### Exportação e restauração

O sistema SHALL disponibilizar download de tabelas LaTeX/CSV, relatório e pacote de auditoria com referências às versões SQLite/Chroma, hashes, código, configurações e histórico; SHALL ocultar segredos e identidade dos avaliadores. Backup consistente SHALL restaurar vínculos e resultados.

## Migração e riscos

Fazer backup consistente antes de migração; testar em cópia. Preservar registros e IDs legados por mapeamento explícito. Toda ambiguidade exige pendência visível, nunca inferência silenciosa. Segredos ficam em ambiente/referências seguras. Congelamento científico impede atualização destrutiva; arquivamento substitui exclusão de entidades referenciadas.

## Validação

Os cenários da spec são critérios de aceitação. Usar dados sintéticos e clientes falsos; teste de integração com SQLite/Chroma local. A validação estrutural OpenSpec não substitui execução dos testes.
