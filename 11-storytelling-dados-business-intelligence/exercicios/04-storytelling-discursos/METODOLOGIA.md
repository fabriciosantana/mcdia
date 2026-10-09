# Metodologia e decisões de storytelling

## Pergunta e público

Como os registros de fala de senadores se distribuem no tempo, entre oradores e por assuntos na 56ª legislatura? O painel destina-se à exploração por estudantes, jornalistas e cidadãos. A chamada “Quem ocupa o espaço da palavra?” é operacionalizada por frequência de registros, não duração, influência, representatividade ou mérito.

O percurso apresenta contexto, ritmo mensal, concentração por orador, pistas temáticas e retorno aos registros. A ação esperada é conferir a fonte antes de formular uma interpretação. Os títulos factuais são derivados dos filtros; nenhum título mantém conclusões do recorte anterior.

## Dados e auditoria

Fonte original: Senado Federal, endpoints `/plenario/lista/discursos/{AAAAMMDD}/{AAAAMMDD}.json` e `/discurso/texto-integral/{CodigoPronunciamento}`. Consolidação utilizada: Fabricio Fernandes Santana, `fabriciosantana/discursos-senado-legislatura-56`, v1.1.1, revisão `c20b4e1ea45bbbfb408167cc07c6f79789c7c345`.

Parquet SHA-256: `e09cfc4793e5394be440906320c7d3008cda5a52b90bbc85bf47446362406af1`.

| Verificação | Resultado |
|---|---:|
| Registros no corpus completo | 15.729 |
| Códigos únicos | 15.729 |
| Códigos duplicados | 0 |
| Tipo autor Senador(a), antes de filtrar Casa | 13.290 |
| Autores externos | 2.074 |
| Deputados | 365 |
| Casa Senado Federal, antes de filtrar autor | 14.438 |
| Casa Congresso Nacional | 1.291 |
| Elegíveis: Senador(a) **e** Senado Federal | 12.414 |
| Excluídos por não satisfazer ambos os critérios | 3.315 |
| Elegíveis sem código de parlamentar | 0 |
| Elegíveis sem resumo | 45 |
| Corpus completo sem texto integral | 690 |
| Elegíveis sem texto integral | 623 |
| Visão inicial: categoria Discurso | 4.045 |
| Oradores na visão inicial | 106 |
| Sem texto integral na visão inicial | 620 |

As exclusões são a união das condições; não se somam diretamente 2.074 + 365 + 1.291 porque há interseção. Os dados de categorias e Casas são usados apenas na auditoria; o navegador recebe o recorte elegível completo.

A janela solicitada foi 01/02/2019–31/01/2023. Datas observadas: 01/02/2019–10/01/2023. Todos os 48 meses são representados. Janeiro de 2019 está fora da janela; 2023 contém apenas janeiro. A data final observada não prova que a API foi consultada somente até 10/01, nem prova ausência de atividade posterior. Não há comparação percentual entre anos apresentados como completos.

## Unidade e transformações

1. Uma ocorrência corresponde a `CodigoPronunciamento`. Duplicações ou datas inválidas interrompem a preparação em vez de serem corrigidas silenciosamente.
2. Filtrar `TipoAutor == Senador(a)` e `Casa == Senado Federal`. Inicialmente selecionar `TipoUsoPalavra.Descricao == Discurso`; os outros usos ficam acessíveis.
3. Identificar pessoa por `CodigoParlamentar`, preservando o nome original para exibição. O fallback por nome só serve a futuras fontes sem código e não foi necessário nesta revisão.
4. Preservar partido e UF do registro. Não converter filiações para partido atual nem fundir PR/PL, PODE/PODEMOS ou outras siglas históricas. Mudanças de nome/filiação não devem ser interpretadas como novas pessoas quando o código é igual.
5. Normalizar apenas espaços em resumo/indexação para exibição. Não reescrever nem gerar resumos. Para busca e dicionário, transformar em minúsculas e remover diacríticos.
6. Disponibilidade de texto integral = `ok` verdadeiro **e** `TextoDiscursoIntegral` não vazio. Ausentes continuam em todos os denominadores de frequência. Os textos integrais não são incluídos no JSON de navegação, para reduzir o tamanho; são acessados pelo link oficial. O status representa o snapshot, não uma checagem ao vivo do link.
7. Ordenar registros por data e código decrescentes. “Mais antigos” inverte essa ordem. Não há inferência de horário entre falas do mesmo dia.

## Indicadores e denominadores

Seja R o conjunto que atende a todos os filtros ativos e N seu tamanho:

- Pronunciamentos: N; a nota mostra `N / 12.414 × 100`.
- Oradores: códigos parlamentares distintos em R.
- Parcela dos dez mais frequentes: soma das contagens dos primeiros `min(10, número de oradores)` dividida por N. Empates são desempatados alfabeticamente para exibição. Com dez ou menos oradores, a parcela é 100% por definição.
- Texto integral disponível: contagem dos registros com disponibilidade dividida por N; a nota exibe o número absoluto ausente.
- Série temporal: contagem por mês dentro do período selecionado. No modo percentual, cada mês divide por N, não pelo total daquele mês antes dos filtros. As barras percentuais somam 100%, salvo arredondamento.
- Oradores e temas: número de registros correspondentes e percentual sobre N. A base dos gráficos é zero; a escala máxima é recalculada para cada gráfico e recorte e fica indicada. Comprimentos de gráficos separados não compartilham escala.
- N = 0: mostrar 0 para contagens e “—” para percentuais; nenhuma divisão por zero.

Não há testes de hipótese ou intervalos de confiança: as contagens descrevem o corpus disponível. Isso não elimina vieses de cobertura nem autoriza generalização para toda a atividade parlamentar.

## Temas: classificação exploratória por dicionário

Seis grupos definidos manualmente, sem treinamento, agrupamento de tópicos, sentimento ou modelo generativo. O dicionário integral está em `scripts/prepare_data.py`, no manifesto e no painel. A regra procura palavras/expressões completas, com fronteira de palavra, em `Resumo + Indexacao`, após normalização de espaços, caixa e acentos. Um registro conta no máximo uma vez em cada tema, mesmo que repita a palavra.

Exemplos: `sus` só corresponde à palavra inteira, não a uma parte de “sustentável”; `previdencia` não engloba automaticamente qualquer radical, por isso variantes são explicitadas. “Saúde e pandemia” não equivale a uma classificação de discursos exclusivamente sobre COVID-19. O dicionário não é exaustivo, não teve precisão/recall avaliados contra anotação humana e pode produzir falsos positivos e negativos. Um registro pode pertencer a vários temas; as parcelas não formam uma partição.

“Sem tema detectado” significa ausência de correspondência com este dicionário, não conteúdo irrelevante ou inexistente. Buscar “educação” e filtrar tema “Educação” são operações diferentes: a busca procura uma expressão e o tema combina várias palavras. Busca não alcança o texto integral.

## Aplicação da literatura

| Fundamento | Decisão verificável no dashboard |
|---|---|
| Knaflic: contexto, redução de ruído e foco | Hierarquia de títulos, uma série temporal, destaque seletivo do pico e títulos que explicitam o achado |
| Tufte: integridade e economia gráfica | Sem 3D, pictogramas proporcionais ou fundos decorativos nos gráficos; grade discreta e valores auditáveis |
| Cleveland e McGill: percepção de posição/comprimento | Barras mensais e horizontais, em vez de áreas, bolhas ou pizza para ordenar frequências |
| Healey e Enns: atenção visual | Contraste seletivo em verde e terracota, repetição consistente de elementos |
| Huff; Bergstrom e West; Pandey et al. | Zero nas barras, denominadores e escala explícitos, indicação de recortes parciais e de dados ausentes |
| Cairo; Nguyen e Lugo-Ocando | Contexto antes da exploração, fontes acessíveis e explicação do significado das medidas |
| Harrower e Brewer | Cores usadas com parcimônia e acompanhadas por texto/valores, sem exigir distinguir vermelho de verde; a paleta é autoral, não uma reprodução certificada de ColorBrewer |
| Ioannidis | Separação entre descrição e inferência; sem transformar padrões exploratórios em explicações causais |
| Segel e Heer | Sequência guiada seguida de exploração livre por filtros e retorno à evidência |
| Blanco, TD 355 e TD 357 | Atenção à heterogeneidade dos tipos de fala e aos limites da comparação entre corpora; sem atribuir legibilidade ou interatividade a estas contagens |

A literatura orienta escolhas de projeto; não se afirma que este dashboard foi validado em experimento de compreensão humana. Acessibilidade foi tratada com HTML semântico, rótulos, foco visível, tabelas equivalentes, descrições e operação por teclado, mas não há certificação WCAG ou teste com leitor de tela.

## Limites e extensões

Não existe ajuste por sessões, oportunidades, licenças, mandatos ou dias de exercício. Oradores distintos não correspondem a cadeiras simultaneamente ocupadas. O corpus não foi reconciliado contra uma segunda extração independente. Campos faltantes podem ser seletivos; especialmente a falta de texto integral se concentra na categoria Discurso, razão para não restringir a análise a textos recuperados.

Os estudos de Blanco abrangem 2007–2024 e utilizam procedimentos adicionais; o TD 357 descreve seleção por extensão textual e exclusão de apartes. Este painel não replica suas análises, não estima leiturabilidade e não atribui causalidade à pandemia ou às redes sociais.

Extensões futuras: validação humana dos temas com amostra estratificada e protocolo publicado; ajuste por período efetivo de mandato com fonte adicional; histórico de filtros por URL; avaliação de usabilidade e acessibilidade assistiva. Essas extensões não são requisitos para executar a versão entregue.

## Autoria e ferramentas

Implementação e documentação assistidas por Codex. Skills utilizadas: hf-cli / huggingface-datasets para exploração e extração; academic-research-suite para consulta dirigida a fontes; sites para desenvolvimento e preview locais. A consulta foi feita no mesmo contexto de implementação, sem revisores independentes ou revisão sistemática. Dados públicos não foram enviados a serviços de inferência. O dashboard não contém IA em execução nem análise gerada de posição política.
