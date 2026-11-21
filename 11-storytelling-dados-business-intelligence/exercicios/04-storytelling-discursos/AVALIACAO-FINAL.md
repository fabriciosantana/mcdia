# Avaliação frente à especificação do trabalho final

Revisão técnica em 13/10/2026. Não substitui a avaliação do professor nem a
apresentação oral. Escopo: arquivos deste exercício e corpus local já existente;
nenhuma nova coleta ou substituição dos dados foi feita.

## Parecer por critério

| Critério | Avaliação e evidência |
| --- | --- |
| Dados reais, fontes no painel | Atendido documentalmente: Senado Federal, consolidação identificada, revisão fixada, manifesto e links por código. Os testes reconciliam o snapshot; não fizemos uma segunda coleta independente. |
| Pergunta central visível | Atendido: “Quem ocupa o espaço da palavra?” aparece no título, com período e unidade de contagem explicados. |
| Clareza narrativa | Melhorado: pergunta → ritmo → distribuição → temas → evidências → conclusão. A síntese acompanha os filtros e não generaliza seleções de até dez oradores à legislatura. |
| Adequação dos gráficos | Atendido nos cenários verificados: barras com origem zero; séries por mês; curva acumulada explicitamente distinta de Lorenz; denominadores visíveis e lacunas sem base não tratadas como 0%. |
| Uso intencional das cores | Melhorado: legenda explica destaque/contexto e A/B. Corrigido o seletor que impedia destacar a primeira barra após o eixo. Rótulos e valores acompanham a cor. |
| Títulos conclusivos | Melhorado: temas, períodos, evolução, qualidade e comparação de oradores apresentam resultados calculados; vazios e empates têm tratamento explícito. |
| Relevância da história | Explicitada na conclusão: participação registrada como pergunta sobre representação, sem confundir frequência com desempenho parlamentar. |
| HTML ou link | Entrega autocontida em `entrega/vozes-do-senado.html`, aproximadamente 8,5 MB. Não é necessário enviar a pasta nem iniciar servidor. |
| Qualidade oral e exatamente 10 minutos | Preparado, mas não comprovado: roteiro soma 600 segundos. Exige ensaio e execução humana; não basta ler o painel. |
| Individualidade, prazo e ranking | Dependem do aluno: confirmar autoria, enviar até 15/10/2026 e entregar a ficha de todos os colegas sem empates. Não houve envio ao professor. |

## Ciclos executados

1. **Diagnóstico:** 15 testes existentes aprovados; identificadas ausência de
   conclusão, dependência de servidor e falta de roteiro cronometrado.
2. **Correção:** síntese dinâmica, títulos, legenda, percurso e roteiro;
   empacotamento offline com dados, módulos e documentação embutidos.
3. **Teste e nova correção:** a regressão detectou um seletor antigo
   `button:first-child` incompatível com o eixo inserido antes das barras.
   Ajustados teste e destaque CSS para o primeiro botão, preservando o eixo.
   Corrigidos também a leitura de uma tabela ainda fechada e a espera pela
   cópia assíncrona de link. Acrescentados casos sem dados, com um orador e com
   frequências iguais. Na revisão temática, a mensagem de salvamento deslocava
   o botão durante o primeiro clique; salvar o nome durante a digitação eliminou
   a falha, reproduzida em 1440 × 1080.
4. **Revalidação:** suíte analítica, regressão HTTP e entrega offline aprovadas.

## Resultados finais

| Verificação | Resultado |
| --- | --- |
| Testes automatizados de dados e narrativa | 19 aprovados; zero falhas |
| Regressão de navegador com servidor | Aprovada: filtros, comparações, histórico, exportações, revisão, erros de carga e recuperação |
| HTML aberto por `file://`, rede desativada | Aprovado: zero requisições HTTP e zero erros JavaScript nos cenários testados |
| Layout | Desktop 1440 × 1080 e móvel 390 × 844; sem transbordamento horizontal da página; conclusão inspecionada visualmente |
| Cor real da primeira barra | Verde em oradores e terracota em temas, verificados por estilo computado |
| Corpus inicial | 4.045 discursos; 106 oradores; top dez: 1.955 (48,3%); 620 sem integral no snapshot |
| Exportação ZIP | Cinco arquivos; verificação independente com `unzip -t` sem erros |
| Carga modular inicial | 941.627 bytes em 13 recursos no teste local; não é benchmark de rede lenta |
| Entrega autocontida | 8.478.094 bytes; 45 fragmentos mensais embutidos; sem dependências de rede para explorar |
| Sintaxe e alterações | Scripts verificados; `git diff --check` sem erros |

SHA-256 do HTML entregue:
`bf198153fa47ff8f615322d743a76aeb2b6720062eafe305cbcd7f0887bcb884`.
Os casos sintéticos de anotação executam em contextos isolados do navegador;
não alteram a amostra nem constituem validação humana dos temas.

## Validação reproduzível

Da raiz do repositório:

```bash
node exercicios/04-storytelling-discursos/scripts/build_delivery.mjs
node --test exercicios/04-storytelling-discursos/tests/*.test.mjs
python3 -m http.server 8001 --bind 127.0.0.1 --directory exercicios/04-storytelling-discursos
```

Com o servidor ativo, em outro terminal (Playwright instalado separadamente em
`/tmp/vozes-senado-qa`, conforme o README):

```bash
NODE_PATH=/tmp/vozes-senado-qa/node_modules DASHBOARD_URL=http://127.0.0.1:8001 node exercicios/04-storytelling-discursos/tests/browser.cjs
NODE_PATH=/tmp/vozes-senado-qa/node_modules node exercicios/04-storytelling-discursos/tests/delivery.cjs
```

O teste de entrega usa Chrome, `file://` e rede desabilitada: verifica dados,
conclusões, cores computadas, filtros, busca, CSV, ZIP, downloads de documentos,
amostra de revisão, âncoras e ausência de transbordamento móvel. Capturas de QA
ficam em `/tmp/vozes-final-*.png`; são temporárias, não parte da entrega.

## Limites e preparação final

Não estimamos nota: o professor responde por 4,2 dos 6 pontos, sem distribuição
interna informada entre seus critérios. Os 1,8 pontos dos pares dependem de
rankings reais; não podem ser inferidos por teste automatizado.

A detecção temática continua exploratória. Não houve validação humana
representativa, auditoria formal de acessibilidade, teste com leitor de tela,
Firefox/Safari ou checagem ao vivo de todos os links externos. A disponibilidade
do texto integral é a do snapshot, não uma garantia de acesso atual na fonte.
O HTML contém resumos/indexações e metadados, não os textos integrais das falas.

Antes do envio: abrir a cópia final fora do ambiente de desenvolvimento, ensaiar
com cronômetro e projetor, conferir autoria e cumprir a data. O tamanho do HTML
pode exigir envio como arquivo anexado ou link para download, conforme o canal
aceito pelo professor. Não houve deploy, commit, push ou submissão automática.
