# Memória de trabalho — avaliação causal do Programa Mais Médicos

Última atualização: 23 de julho de 2026.

## 1. Objetivo da atividade

Aplicar o quadro de resultados potenciais e o critério de backdoor a uma
política pública diferente do Bolsa Família. A entrega deve:

1. escolher uma política federal ou estadual;
2. definir um estimando — ATE, ATT ou ATU;
3. apresentar um DAG plausível com pelo menos um confundidor, um mediador e um
   colisor;
4. justificar quais variáveis devem e quais não devem ser controladas.

A política escolhida foi o **Programa Mais Médicos (PMM)**. O desfecho é a
taxa municipal de **internações por condições sensíveis à atenção primária
(ICSAP)**.

## 2. Estado atual do trabalho

O notebook inicial era conceitualmente consistente, mas utilizava somente
dados simulados. Ele foi substituído por uma aplicação com dados
administrativos reais.

Arquivo principal:

- `atividade_inferencia_causal_mais_medicos.ipynb`

O notebook foi executado integralmente e contém as saídas, tabelas e gráficos.
Na última validação, nenhuma célula apresentou erro.

Arquivos auxiliares:

- `data/processed/mais_medicos_icsap_go.csv`: base analítica pronta, com uma
  linha por município;
- `preparar_dados_reais.py`: reconstrói a base analítica a partir dos arquivos
  brutos;
- `construir_notebook.py`: gera a estrutura do notebook;
- `data/README.md`: documenta as fontes e a reprodução;
- `data/raw/.gitignore`: impede que os arquivos brutos grandes sejam
  versionados.

## 3. Recorte empírico atual

- Unidade: município.
- Recorte geográfico: os 246 municípios de Goiás.
- Tratamento: presença de pelo menos um profissional ativo do PMM na fotografia
  de 29/11/2013.
- Tratados: 29 municípios.
- Comparação: 217 municípios.
- Linha de base: janeiro a outubro de 2013, anualizada por `12/10`.
- Resultado: média das taxas anuais de ICSAP de 2014 e 2015.
- Taxa: número de internações classificadas como numerador de ICSAP dividido
  pela população municipal, multiplicado por 10 mil.
- Estimando: ATT da entrada inicial no programa.

Formalmente:

`ATT = E[Y(1) - Y(0) | D = 1]`.

Interpretação: efeito médio da entrada inicial no PMM sobre as ICSAP dos
municípios goianos inicialmente atendidos.

## 4. Por que foram escolhidos esses períodos

A série histórica do PMM fornece uma fotografia municipal em 29/11/2013.
Janeiro–outubro de 2013 foi usado como período anterior a essa fotografia.
2014–2015 fornece dois anos completos depois da entrada inicial e permite algum
tempo para o mecanismo da atenção básica afetar internações.

Limitação importante: o PMM foi lançado em julho de 2013. Portanto,
janeiro–outubro de 2013 é anterior à fotografia operacional do tratamento, mas
não necessariamente anterior a qualquer exposição ao programa. Uma linha de
base em 2012 seria mais limpa, mas a base goiana de ICSAP utilizada começa em
2013.

## 5. Por que Goiás

Goiás foi escolhido por disponibilidade operacional dos dados, não por ser
necessariamente o caso substantivo ideal.

A Secretaria de Estado da Saúde de Goiás disponibiliza uma base:

- oficial;
- derivada do SIH/DATASUS;
- previamente classificada segundo a lista brasileira de ICSAP;
- identificada por município de residência e mês;
- compatível com códigos municipais do IBGE;
- com cobertura dos 246 municípios.

Isso tornou possível integrar PMM, ICSAP e população de forma transparente e
reproduzível. Uma análise nacional exigiria baixar e classificar os microdados
do SIH de todas as UFs.

Consequência: o ATT de Goiás não pode ser automaticamente generalizado para o
Brasil.

Texto sugerido para a entrega:

> O recorte de Goiás foi determinado pela disponibilidade de uma base oficial,
> municipal e previamente classificada de internações por condições sensíveis
> à atenção primária, que pôde ser integrada à série histórica do Programa Mais
> Médicos e às estimativas populacionais do IBGE. O recorte favorece a
> transparência e a reprodutibilidade da aplicação, mas limita a validade
> externa dos resultados.

## 6. Fontes de dados

### Programa Mais Médicos

Ministério da Saúde, Programa de Provimento Federal — série histórica do PMM:

`https://dadosabertos.saude.gov.br/dataset/provimento-federal-programa-mais-medicos`

Arquivo CSV/ZIP utilizado:

`https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/MaisMedicos/csv/ppf_mais_medicos_serie_historica.csv.zip`

O arquivo bruto esperado pelo script deve se chamar:

`data/raw/ppf_mais_medicos_serie_historica.csv.zip`

### ICSAP

Secretaria de Estado da Saúde de Goiás, base derivada do SIH/DATASUS:

`https://dadosabertos.go.gov.br/dataset/436edce3-5c43-4c79-8ba4-d9a48e8e1d1c/resource/b9c62bb7-dbd7-492e-a3be-822de01992fd/download/internacoes-icsap.csv`

O arquivo bruto esperado deve se chamar:

`data/raw/internacoes_icsap_go.csv`

Na base:

- `tipo = Numerador` representa as internações usadas no numerador de ICSAP;
- os dados vão de 2013 até 2026, mas 2026 é parcial.

Referência normativa para a lista brasileira de ICSAP:

`https://bvsms.saude.gov.br/bvs/saudelegis/sas/2008/prt0221_17_04_2008.html`

### População

IBGE/SIDRA, tabela 6579, estimativas populacionais municipais de Goiás para
2013–2015:

`https://apisidra.ibge.gov.br/values/t/6579/n6/in%20n3%2052/v/9324/p/2013-2015?formato=json`

O arquivo bruto esperado deve se chamar:

`data/raw/populacao_go_2013_2015.json`

## 7. DAG e estratégia causal

Variáveis teóricas:

- `V`: vulnerabilidade socioeconômica prévia;
- `B`: oferta/cobertura de atenção básica e ICSAP prévias;
- `G`: capacidade administrativa municipal prévia;
- `D`: entrada inicial no PMM;
- `M`: acesso ou consultas após o PMM — mediador;
- `K`: gasto municipal em saúde posterior — colisor plausível;
- `U`: choque de saúde não observado;
- `Y`: ICSAP posterior.

Caminhos de backdoor:

- `D <- V -> Y`;
- `D <- B -> Y`;
- `D <- G -> Y`.

Conjunto de ajuste teórico:

`Z = {V, B, G}`.

Para estimar o efeito total:

- controlar vulnerabilidade, oferta de APS, capacidade administrativa e
  desfecho prévio, todos medidos antes do tratamento;
- não controlar consultas ou cobertura posteriores, pois são mediadores;
- não controlar gasto posterior quando ele funciona como colisor entre PMM e
  choques de saúde;
- não incluir automaticamente variáveis apenas porque predizem bem o
  resultado.

## 8. Limitação central de identificação

A base empírica atual mede:

- taxa prévia de ICSAP;
- taxa prévia de internações clínicas;
- porte populacional;
- região de saúde.

Ela não mede integralmente:

- vulnerabilidade socioeconômica;
- oferta anterior de médicos e cobertura da APS;
- capacidade fiscal e administrativa.

Essas variáveis observadas são proxies incompletas para o conjunto de ajuste do
DAG. Portanto, a hipótese de ausência de confundimento não observado é forte.
O resultado deve ser apresentado como **estimativa observacional ajustada,
compatível com o DAG sob as hipóteses declaradas**, e não como prova definitiva
do efeito causal.

## 9. Métodos e resultados atuais

O notebook apresenta:

1. diferença bruta entre tratados e controles;
2. diferença em mudanças, descontando a taxa prévia;
3. ATT ponderado por escore de propensão.

O escore de propensão utiliza:

- taxa de ICSAP prévia;
- taxa de internações clínicas prévia;
- log da população;
- região de saúde.

Resultados salvos no notebook:

| Estimador | Estimativa | IC bootstrap 95% |
|---|---:|---:|
| Diferença bruta | -83,16 | [-156,36; -2,97] |
| Diferença em mudanças | -11,38 | [-60,86; 33,03] |
| ATT ponderado | -19,50 | [-83,11; 34,16] |

Unidade: internações ICSAP por 10 mil habitantes.

Leitura correta:

- o ATT ponderado sugere associação com redução de 19,5 internações por 10 mil;
- o intervalo inclui zero e é amplo;
- os dados são compatíveis com redução, ausência de efeito ou pequeno aumento;
- não se deve escrever que o PMM comprovadamente causou redução;
- o bootstrap representa incerteza amostral, não incerteza sobre o DAG ou
  confundimento não observado.

Formulação sugerida:

> A estimativa ajustada do ATT foi de -19,5 internações por 10 mil habitantes,
> com intervalo bootstrap de 95% entre -83,1 e 34,2. A imprecisão e a possível
> presença de confundimento residual impedem uma conclusão causal categórica.

## 10. Hipóteses e ameaças à validade

- Consistência: “receber PMM” engloba diferentes doses, duração e perfil de
  profissionais.
- Positividade: devem existir tratados e controles comparáveis em todos os
  perfis relevantes.
- Ausência de confundimento não observado: principal fragilidade.
- Não interferência: pacientes e médicos podem cruzar fronteiras municipais.
- Ordenação temporal: apenas variáveis anteriores devem entrar no ajuste.
- Adoção posterior: municípios de comparação podem receber PMM em 2014–2015,
  reduzindo o contraste.
- Mensuração: o SIH representa internações financiadas pelo SUS.
- Poucos tratados: somente 29 municípios na coorte inicial.
- Validade externa: o resultado de Goiás não representa automaticamente o
  Brasil.

## 11. Possível atualização futura

Foi discutida a possibilidade de usar dados recentes. A decisão atual foi
**manter o desenho de 2013–2015 por enquanto**.

Se o trabalho for atualizado futuramente, a alternativa recomendada é:

- linha de base: 2022;
- tratamento: entrada ou expansão do PMM durante 2023;
- resultados: média das taxas de ICSAP em 2024–2025;
- não usar 2026, pois o ano é parcial.

O tratamento recente não deve ser simplesmente “ter PMM em 2023”, porque muitos
municípios já participavam. Duas definições possíveis:

1. novo ingresso: não tinha profissionais em dezembro de 2022 e passou a ter
   em dezembro de 2023;
2. expansão: aumento previamente definido no número de profissionais ou de
   profissionais por 10 mil habitantes.

Antes de trocar o desenho, verificar:

1. quantos municípios ingressaram ou expandiram em 2023;
2. quantos controles permaneceram sem expansão até o fim de 2025;
3. se existe suporte comum adequado;
4. se há tratamento suficiente em Goiás ou se será necessária uma análise
   nacional;
5. datas e ciclos exatos de entrada;
6. modalidades de financiamento e coparticipação.

Vantagens potenciais:

- linha de base completa;
- dois anos completos de resultado;
- covariáveis socioeconômicas do Censo 2022;
- maior relevância para a configuração atual da política.

Riscos:

- tratamento já muito disseminado;
- poucos controles puros;
- múltiplos ciclos de adesão;
- contaminação do grupo de comparação por expansão em 2024–2025;
- resquícios da pandemia em 2022;
- possível violação de positividade.

Fontes institucionais úteis para essa atualização:

- série histórica 2013–2026:
  `https://dadosabertos.saude.gov.br/dataset/provimento-federal-programa-mais-medicos`;
- chamamentos de 2023:
  `https://www.gov.br/saude/pt-br/composicao/sgtes/mais-medicos/chamamentos-publicos/2023/2023`;
- descrição oficial da retomada:
  `https://www.gov.br/saude/pt-br/composicao/sgtes/mais-medicos/saiba-mais`.

## 12. Reprodução e validação

Com os três arquivos brutos nos caminhos descritos:

```bash
python 09-appd/assignments/preparar_dados_reais.py
```

Isso deve produzir:

`09-appd/assignments/data/processed/mais_medicos_icsap_go.csv`

Para reconstruir o notebook:

```bash
python 09-appd/assignments/construir_notebook.py
```

Observação: esse comando gera novamente o notebook e remove as saídas
anteriores. Em seguida, é preciso executá-lo para preservar resultados e
gráficos:

```bash
JUPYTER_CONFIG_DIR=/tmp/mcdia-jupyter-config \
JUPYTER_DATA_DIR=/tmp/mcdia-jupyter-data \
JUPYTER_RUNTIME_DIR=/tmp/mcdia-jupyter-runtime \
jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=300 \
  09-appd/assignments/atividade_inferencia_causal_mais_medicos.ipynb
```

O ambiente pode exigir autorização para abrir os sockets locais do kernel
Jupyter.

## 13. Próximos passos possíveis

Se o trabalho for retomado sem alterar o período:

1. revisar linguagem acadêmica e identificação dos integrantes;
2. verificar padrão bibliográfico exigido pelo professor;
3. decidir se o script gerador deve permanecer na entrega;
4. acrescentar dados pré-tratamento de CNES/ESF, Censo/Atlas Brasil e finanças
   municipais;
5. reestimar o ATT e revisar suporte comum;
6. exportar o notebook para HTML ou PDF, se solicitado.

Se o professor exigir apenas a estratégia de identificação, pode-se reduzir a
ênfase na estimativa numérica e manter os dados reais como ilustração.

