# Plano de adequação ao trabalho final

## Diagnóstico e critério de parada

A versão inicial tem pergunta visível, fontes no painel, escalas apropriadas,
filtros e ressalvas metodológicas. Os 15 testes de dados existentes passaram.
Faltavam entrega autocontida, conclusão explícita, títulos conclusivos em parte
dos gráficos e roteiro de apresentação. Não há base para atribuir nota oral ou
prever ranking entre pares.

## Ciclos de execução

1. **Narrativa:** acrescentar conclusão que acompanha os filtros, títulos com
   achados e explicação da paleta; fornecer percurso e roteiro de 600 segundos.
2. **Entrega:** gerar um HTML que reúna código, estilos, dados e documentação,
   sem depender de servidor ou internet para explorar o corpus.
3. **Validação:** executar testes de dados e navegador, abrir a entrega offline,
   conferir filtros, exportações, estados vazios, acessibilidade básica e telas
   desktop/móvel. Corrigir regressões e repetir os testes afetados.
4. **Handoff:** registrar resultados e limitações em `AVALIACAO-FINAL.md`, com
   instruções de entrega e pendências exclusivas do apresentador.

Concluir os ciclos técnicos quando os testes passarem e o HTML independente
funcionar. Não marcar como cumpridas a duração real da fala, autoria individual,
submissão até 15/10/2026 ou participação na avaliação entre pares sem evidência.

### Encerramento dos ciclos técnicos — 13/10/2026

- [x] Narrativa, títulos, cores e roteiro de 600 segundos.
- [x] HTML independente gerado com dados e documentação embutidos.
- [x] Correções repetidas até aprovação: 19 testes analíticos/narrativos,
  regressão HTTP e teste offline no navegador.
- [x] Avaliação por critério e limitações em `AVALIACAO-FINAL.md`.
- [ ] Ensaio real, apresentação de 10 minutos, envio e ranking: ações do aluno.

## Correspondência com a rubrica

| Requisito | Evidência a verificar |
| --- | --- |
| Dados reais e fontes no painel | Método, revisão do dataset, manifesto e links por registro |
| Pergunta, desenvolvimento, conclusão | Hero, gráficos e síntese dinâmica |
| Gráficos adequados | Barras a partir de zero; séries temporais; denominadores e lacunas explícitos |
| Cores intencionais | Legenda de função, valores e rótulos sem depender apenas da cor |
| Títulos conclusivos | Achados calculados, incluindo empates e ausência de base |
| HTML ou link | `entrega/vozes-do-senado.html`, aberto offline |
| Apresentação de 10 minutos | Roteiro com marcos; ensaio humano ainda necessário |
| Prazo e ranking | Checklist do apresentador; sem nota ou posição inventadas |
