# Registro de implementação e validação

Primeira versão funcional concluída em 09/10/2026. Verificações executadas no ambiente de desenvolvimento; não são resultados de uma avaliação independente.

## Execução em ciclos

1. Planejamento registrado em `PLANEJAMENTO.md`, consulta dirigida às fontes e inspeção do corpus.
2. Download do Parquet na revisão fixada e confirmação do SHA-256 declarado pelo produtor. Identificação de convidados, deputados e registros da Casa Congresso Nacional; definição e documentação do recorte elegível.
3. Implementação do pipeline, interface, agregações, dicionário, exploração e exportação. Dados reais locais, sem amostragem para a interface.
4. Seis testes analíticos passaram. O primeiro conector de navegador falhou ao iniciar o Chrome por restrição de namespaces. Foi usado o Chrome instalado, via Playwright local, com `--no-sandbox` restrito ao processo de QA.
5. A primeira execução do teste de navegador detectou que o link de referências retornava 404 enquanto a documentação ainda não havia sido escrita. A documentação foi concluída. A revisão também identificou que “Restaurar visão inicial” deveria restaurar medida e ordenação, além dos filtros; comportamento corrigido.
6. Nova execução completa do teste de navegador passou, incluindo documentação, desktop, celular e erro de carga. Capturas foram inspecionadas visualmente. A série mensal mantém rolagem horizontal interna no celular para preservar legibilidade, sem alargar a página.
7. Verificação final de sintaxe, testes analíticos, regras do dicionário e hash da origem passou. A dependência de reconstrução foi fixada na versão efetivamente utilizada: PyArrow 25.0.1, com Python 3.14.6 neste ambiente. A visualização não depende desse pacote.

## Evidências de verificação

| Verificação | Resultado |
|---|---|
| HTTP da página inicial | 200 |
| JavaScript `node --check` | Sem erro de sintaxe |
| Testes `node --test tests/analytics.test.mjs` | 6 passaram; 0 falhas |
| SHA-256 do Parquet | Coincide com produtor e manifesto |
| SHA-256 do JSON | Coincide com manifesto local |
| IDs e janela | Sem duplicados; datas dentro da janela |
| Visão inicial | 4.045 registros, 106 oradores, 3.425 textos disponíveis |
| Todos os tipos elegíveis | 12.414 registros |
| Top 10 inicial | 1.955 registros, 48,3% do recorte |
| Maior mês inicial | Maio de 2019, 208 registros |
| Meses na série inicial | 48, incluindo meses sem registros |
| Combinação PT + RS + código 825 | 442 registros; 1 orador |
| Busca `educação` / `EDUCACAO` | Mesmos resultados |
| Busca inexistente | 0 registros, mensagem explícita e exportação desabilitada |
| Filtro temático e seleção de orador | Controles e totais atualizados |
| Barra mensal por teclado | Enter seleciona o mês e atualiza o período |
| Modo percentual | Escala e legenda indicam % do recorte |
| Paginação | Página 2 de 506 na visão inicial |
| Ordenação crescente | Primeiro registro de 02/02/2019 |
| Datas invertidas | Erro explícito e ausência de agregados enganosos |
| CSV real baixado no navegador | 4.045 registros + cabeçalho, todas as páginas |
| Neutralização de fórmulas CSV | Testes de prefixo e aspas passaram |
| Links oficiais | Padrão de URL com código verificado; não houve varredura ao vivo de todos os links |
| Links locais de método, referências e manifesto | HTTP 200 |
| Layout desktop | 1440 × 1080, captura inspecionada |
| Layout móvel | 390 × 844, sem transbordamento horizontal da página; filtro de UF funcional |
| Falha simulada do JSON | Mensagem de erro com instrução de recuperação |
| Erros de JavaScript capturados | Nenhum nos cenários testados |
| Dicionário | Acentos e caixa normalizados; `SUS` não corresponde a `sustentável`; repetição não duplica o tema |

As afirmações acima podem ser reproduzidas com os comandos do README. Os casos principais de interface estão em `tests/browser.cjs`. As verificações pontuais de dicionário e checksum da origem também foram executadas diretamente em Python durante a preparação; não dependem de um serviço externo.

## Limites de validação

- Não houve teste com usuários, leitor de tela, Safari ou Firefox, nem auditoria formal de WCAG.
- Não houve avaliação humana da precisão/recall dos temas; as categorias são explicitamente exploratórias.
- As contagens foram reconciliadas com o Parquet e o card do produtor, não com uma segunda coleta da API do Senado.
- Os textos integrais estão ligados à origem, não incorporados na interface. Sua disponibilidade ao vivo pode mudar.
- O carregamento inicial transfere aproximadamente 9,6 MB; não foi feito benchmark sob conexões lentas. Após carregar, filtros são locais.
- Nenhum deploy, push ou envio de mensagens foi realizado. O servidor de QA é temporário; para visualizar novamente, execute o comando do README.
