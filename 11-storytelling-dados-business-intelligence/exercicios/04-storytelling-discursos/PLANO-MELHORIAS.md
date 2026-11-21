# Plano de evolução — segunda versão

Pedido: implementar as oito melhorias propostas, em ciclos até conclusão funcional.

1. Comparação A/B por intervalos mensais, atalhos com os mesmos meses em anos adjacentes, avisos de extensão e sazonalidade, deltas absolutos e percentuais com base zero tratada. Comparar também composição temática e oradores.
2. Evolução mensal por tema: proporção sobre o total de registros daquele mês sob os demais filtros; denominador explícito e lacunas sem divisão por zero; tabela equivalente e seleção de mês/tema.
3. Anotações factuais de pico, concentração e ausências, e contexto histórico com fonte primária, sem atribuição causal.
4. Auditoria do dicionário: palavras acionadoras e campos de origem por registro, amostra estratificada reproduzível, leitura qualitativa assistida por IA identificada como tal, formulário de anotação humana com importação/exportação e métricas apenas para rótulos efetivamente revisados. Não inventar validação humana.
5. Participação acumulada (ordem decrescente explicitada), comparação de dois oradores; investigar e integrar intervalos de exercício oficiais para taxa por 100 dias com cobertura e limitações visíveis.
6. Filtros/controles persistidos na URL, histórico de navegação e restauração, copiar link; pacote único CSV + metadados com versão, revisão, regras, filtros e hashes.
7. Corpus dividido: índice analítico compacto, detalhes carregados por mês e sob demanda, busca carregando somente meses necessários, cache e recuperação de erro; textos maiores, controles com áreas maiores, visualizações adaptadas ao celular, operação por teclado.
8. Painel de qualidade por mês e tipo de fala, incluindo disponibilidade do texto, resumo e indexação; denominadores e origem claros.

## Critérios de aceite

Testes independentes das novas fórmulas e casos-limite; conservação dos totais; comparação e taxas auditáveis; URL reproduz estado; CSV completo com metadados coerentes; amostra sem alegação falsa de revisão humana; desempenho inicial medido antes/depois; desktop/móvel sem transbordamento; erro de fragmento recuperável; docs atualizados.

## Limites epistemológicos

Revisão humana exige uma pessoa: entregar o fluxo operacional e separar resultados assistidos por IA de rótulos humanos. Intervalos oficiais de exercício não medem oportunidades de fala ou presença em sessão. Dados de sessões e cargos adicionais não serão inferidos a partir das falas.
