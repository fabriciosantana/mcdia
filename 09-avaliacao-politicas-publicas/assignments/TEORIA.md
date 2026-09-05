# Guia integrado de inferência causal — atividades 1 e 2

Este documento reúne os conceitos necessários para compreender, explicar e
criticar as duas atividades sobre o Programa Mais Médicos (PMM). A **Parte I**
trata da avaliação observacional realizada na atividade 1; a **Parte II** trata
do planejamento de um experimento aleatorizado na atividade 2. O objetivo não
é substituir os livros indicados nas referências, mas oferecer uma trilha de
estudo objetiva, didática e aplicada às decisões concretas dos notebooks.

| Atividade | Pergunta central | Estimando principal | Ferramentas centrais |
|---|---|---|---|
| 1 — avaliação observacional | Qual foi o efeito da presença inicial do PMM nos municípios que receberam o programa? | ATT | resultados potenciais, DAG, backdoor, escore de propensão e ponderação |
| 2 — experimento planejado | Qual seria o efeito de oferecer prioritariamente um novo pacote do PMM? | ITT; LATE como análise secundária | aleatorização, MDE, poder, não conformidade e validade |

As duas partes usam a mesma linguagem de resultados potenciais. A diferença
fundamental é a origem da comparabilidade: na atividade 1 ela depende de
hipóteses e ajustes com dados observados; na atividade 2 ela é criada pelo
sorteio, em expectativa.

# Parte I — Atividade 1: avaliação causal observacional do Mais Médicos

## 1. Da associação à pergunta causal

Uma comparação simples entre municípios com e sem PMM mede uma **associação**.
Ela somente representa um efeito causal se os grupos forem comparáveis quanto
a todas as causas relevantes do tratamento e do desfecho. Isso é especialmente
importante no PMM: o programa não foi distribuído ao acaso; municípios com
maior vulnerabilidade, carência médica ou capacidade de adesão podem ter maior
probabilidade de recebê-lo e também apresentar trajetórias diferentes de ICSAP.

Uma pergunta causal bem definida explicita cinco elementos:

1. **Unidade:** município de Goiás.
2. **Tratamento:** presença de ao menos um profissional do PMM em 29/11/2013.
3. **Comparação:** ausência de profissional nessa data.
4. **Desfecho:** média da taxa anual de ICSAP em 2014–2015, por 10 mil habitantes.
5. **População-alvo e estimando:** municípios que receberam inicialmente o PMM; ATT.

No banco há 246 municípios, dos quais 29 tratados e 217 controles. A data de
tratamento é uma fotografia operacional, não uma descrição de toda a exposição
posterior. Um controle pode ter aderido depois, e a intensidade do programa
pode variar entre tratados. Essa distinção deve acompanhar a interpretação.

## 2. Resultados potenciais e o problema fundamental

Para cada município \(i\), imagine dois resultados:

- \(Y_i(1)\): ICSAP que seria observada com presença inicial do PMM;
- \(Y_i(0)\): ICSAP que seria observada sem essa presença inicial.

O efeito individual seria \(Y_i(1)-Y_i(0)\). Entretanto, apenas um resultado é
observado:

\[
Y_i=D_iY_i(1)+(1-D_i)Y_i(0).
\]

Nunca observamos simultaneamente os dois futuros do mesmo município. Esse é o
**problema fundamental da inferência causal**. Métodos causais procuram usar
outras unidades para construir um contrafactual crível, não recuperar o
contrafactual individual perdido.

### ATE, ATT e ATU

\[
ATE=E[Y(1)-Y(0)]
\]

é o efeito médio em toda a população; 

\[
ATT=E[Y(1)-Y(0)\mid D=1]
\]

é o efeito médio entre os tratados; e

\[
ATU=E[Y(1)-Y(0)\mid D=0]
\]

é o efeito médio entre os não tratados.

O notebook escolhe o **ATT** porque sua pergunta é retrospectiva: qual foi o
efeito nos municípios efetivamente alcançados na implantação inicial? A escolha
também combina com a ponderação utilizada, que mantém peso 1 para tratados e
reconstrói, entre os controles, a distribuição de características dos tratados.
ATE ou ATU responderiam a perguntas políticas diferentes.

## 3. Por que a diferença bruta pode ser enviesada

A diferença observada pode ser decomposta conceitualmente em:

\[
E[Y\mid D=1]-E[Y\mid D=0]
=ATT+\{E[Y(0)\mid D=1]-E[Y(0)\mid D=0]\}.
\]

O termo entre chaves é o **viés de seleção**: mesmo sem o programa, os grupos
poderiam ter resultados diferentes. Ajustar covariáveis busca tornar esse termo
condicionalmente nulo. Não basta incluir muitas variáveis; é preciso incluir as
causas comuns adequadas e evitar controles que criem novos vieses.

## 4. DAG: representar hipóteses causais antes de modelar

Um grafo causal dirigido acíclico (DAG) contém:

- **nós**, que representam variáveis;
- **setas**, que representam relações causais assumidas;
- ausência de seta, que também é uma hipótese substantiva;
- nenhum ciclo causal dirigido.

O DAG da atividade organiza a seguinte história:

```text
Vulnerabilidade prévia (V) ──► D ──► acesso pós-programa (M) ──► Y
             │                 │                                ▲
             └─────────────────┼────────────────────────────────┘
APS/ICSAP prévia (B) ─────────►D───────────────────────────────►Y
             └─────────────────────────────────────────────────►Y
Capacidade administrativa (G)►D───────────────────────────────►Y

D ──► gasto pós-tratamento (K) ◄── choque de saúde não observado (U) ──► Y
```

O DAG não é descoberto automaticamente pelos dados. Ele formaliza conhecimento
institucional e clínico e permite verificar quais caminhos precisam ser
bloqueados. Uma regressão pode ser calculada sem DAG; uma interpretação causal
responsável não deveria prescindir de uma teoria causal explícita.

## 5. Confundidor, mediador e colisor

### Confundidor

É uma causa comum do tratamento e do desfecho. Por exemplo, vulnerabilidade
prévia \(V\) abre o caminho não causal \(D\leftarrow V\rightarrow Y\). APS/ICSAP
prévia \(B\) e capacidade administrativa \(G\) exercem papel semelhante.
Esses caminhos de **backdoor** entram em \(D\) por uma seta voltada para ele.

### Mediador

É consequência do tratamento que transmite parte de seu efeito. O acesso ou o
número de consultas após a implantação, \(M\), está no caminho
\(D\rightarrow M\rightarrow Y\). Controlá-lo retiraria parte do efeito total e
mudaria o estimando para um efeito direto, que exige hipóteses adicionais. Por
isso, ele não pertence ao ajuste do efeito total.

### Colisor

É uma consequência comum de duas variáveis, como
\(D\rightarrow K\leftarrow U\rightarrow Y\). Sem condicionamento, o caminho é
fechado em \(K\). Controlar o gasto pós-tratamento \(K\), estratificar por ele
ou selecionar observações com base nele abre associação entre \(D\) e \(U\),
criando viés. Um colisor não é necessariamente uma variável irrelevante; ele é
uma variável perigosa para aquele estimando e naquele grafo.

Regra prática: para estimar o efeito total, prefira causas comuns **anteriores**
ao tratamento; não ajuste automaticamente consequências do tratamento. O papel
causal importa mais que correlação, significância estatística ou capacidade
preditiva.

## 6. Critério de backdoor

Um conjunto \(X\) satisfaz o critério de backdoor quando:

1. não contém descendentes do tratamento; e
2. bloqueia todos os caminhos entre \(D\) e \(Y\) que entram em \(D\).

No DAG teórico, \(X=\{V,B,G\}\) é um conjunto plausível. Se essas variáveis
fossem medidas corretamente e as demais hipóteses fossem válidas, teríamos:

\[
Y(0),Y(1)\perp D\mid X.
\]

Essa é a **permutabilidade condicional** ou ausência de confundimento não
medido: dentro de estratos de \(X\), a atribuição seria comparável a um sorteio.
É uma hipótese não testável apenas com o banco observado.

Na aplicação, não há medidas completas de vulnerabilidade, oferta médica/APS
prévia e capacidade fiscal-administrativa. O notebook usa proxies disponíveis:

- taxa prévia de ICSAP;
- taxa prévia de internações clínicas;
- logaritmo da população;
- região de saúde.

Proxies podem reduzir confundimento, mas não garantem o bloqueio integral dos
caminhos. Por isso o resultado é uma estimativa observacional ajustada sob
hipóteses declaradas, e não uma prova de causalidade.

## 7. Hipóteses necessárias para identificar o ATT

### Consistência

Se \(D_i=d\), então o resultado observado deve corresponder a \(Y_i(d)\). Isso
pressupõe versões suficientemente bem definidas do tratamento. Diferenças na
quantidade e permanência de profissionais desafiam essa simplificação.

### Não interferência

O tratamento de um município não deve alterar o resultado potencial de outro.
Deslocamento de pacientes ou profissionais entre municípios pode gerar
spillovers e violar essa hipótese.

### Permutabilidade condicional

Após ajustar \(X\), não deve restar causa comum não controlada de tratamento e
resultado. Essa é a hipótese mais forte na atividade 1.

### Positividade

Para todo perfil de \(X\) presente entre tratados, deve existir probabilidade
positiva de observar controles comparáveis:

\[
0<P(D=1\mid X=x)<1.
\]

Se uma região ou perfil só contém tratados, os dados não identificam o
contrafactual sem extrapolação. Positividade é uma propriedade conjunta da
população, do tratamento e das covariáveis escolhidas.

### Mensuração e ordenação temporal

Tratamento, covariáveis e desfecho devem representar os conceitos pretendidos,
e as covariáveis devem preceder a exposição. A linha de base do notebook usa
jan–out/2013 e anualiza por \(12/10\), mas o lançamento do PMM ocorreu em julho
de 2013. Assim, parte da linha de base está temporalmente próxima ou posterior
ao início nacional do programa, uma limitação que deve ser explicitada.

Sob essas hipóteses, o ATT pode ser escrito como:

\[
ATT=E\left[E(Y\mid D=1,X)-E(Y\mid D=0,X)\mid D=1\right].
\]

## 8. Construção das taxas e comparabilidade temporal

O desfecho é uma taxa de ICSAP por 10 mil habitantes, não uma contagem bruta:

\[
taxa=\frac{internações\ ICSAP}{população}\times10.000.
\]

Taxas tornam municípios de tamanhos distintos mais comparáveis, mas podem ser
instáveis em populações pequenas. A média anual de 2014–2015 reduz parte da
flutuação de um único ano. A linha de base de dez meses é anualizada para ficar
na mesma escala; isso pressupõe que multiplicar por \(12/10\) seja uma
aproximação razoável para a exposição anual.

O SIH/SUS registra internações financiadas pelo SUS, não todas as internações
dos residentes. Mudanças de codificação, acesso hospitalar ou cobertura privada
podem afetar as taxas independentemente da atenção primária.

## 9. Escore de propensão

O escore de propensão é a probabilidade condicional de tratamento:

\[
e(X)=P(D=1\mid X).
\]

O notebook estima \(e(X)\) por regressão logística com ICSAP prévia, internações
clínicas prévias, log da população e região de saúde. O escore resume essas
covariáveis para construir uma população de comparação; ele não corrige
variáveis omitidas, não transforma dados observacionais em experimento e não
deve ser julgado apenas por sua capacidade de prever tratamento.

Para o ATT, os pesos são:

\[
w_i=\begin{cases}
1,&D_i=1,\\
\dfrac{e(X_i)}{1-e(X_i)},&D_i=0.
\end{cases}
\]

Controles muito semelhantes aos tratados recebem mais peso. Uma forma
normalizada do estimador é:

\[
\widehat{ATT}=
\frac{\sum_iD_iY_i}{\sum_iD_i}
-
\frac{\sum_i(1-D_i)w_iY_i}{\sum_i(1-D_i)w_i}.
\]

Escores próximos de 1 produzem pesos extremos para controles, aumentando a
variância e tornando poucos municípios excessivamente influentes. Inspecionar
distribuições, pesos máximos e tamanho efetivo da amostra é tão importante
quanto calcular a estimativa. Trimming ou truncamento podem estabilizar a
análise, mas mudam a população-alvo ou introduzem viés; devem ser
pré-especificados e acompanhados de análise de sensibilidade.

## 10. Balanceamento é diagnóstico, não garantia

Após ponderar, comparam-se as covariáveis entre grupos. A diferença média
padronizada (SMD) é, em termos gerais:

\[
SMD=\frac{\bar X_1-\bar X_0}{s_{pooled}}.
\]

Valores absolutos mais próximos de zero indicam maior equilíbrio; limites como
0,10 são convenções diagnósticas, não teoremas. Deve-se examinar balanceamento
antes e depois da ponderação, para cada covariável e, quando possível, também
variâncias e distribuições.

Na atividade, persistem desequilíbrios regionais relevantes após a ponderação:
Entorno Sul (0,484), Entorno Norte (0,397), Central (0,373) e Pireneus (0,285 em
valor absoluto). Isso é evidência de comparabilidade empírica incompleta e deve
reduzir a confiança causal. Bom balanceamento em variáveis observadas tampouco
prova equilíbrio em variáveis não observadas.

## 11. O que estimam as três comparações do notebook

### Diferença bruta pós-tratamento

Compara a média de 2014–2015 entre tratados e controles. O valor é **−83,16**
ICSAP por 10 mil, com intervalo bootstrap **[−156,36; −2,97]**. É descritivo e
potencialmente confundido.

### Diferença nas mudanças

Calcula, em cada município, pós menos linha de base, e compara essa mudança
entre grupos. O valor é **−11,38**, com intervalo **[−60,86; 33,03]**. Subtrair
a linha de base remove diferenças fixas de nível, mas não elimina tendências
distintas ou confundimento variável no tempo.

Esse cálculo se aproxima da intuição de diferenças-em-diferenças (DiD), mas um
DiD causal requer, sobretudo, a hipótese de **tendências paralelas**: sem o PMM,
os grupos teriam evoluído de modo semelhante. Com uma única linha de base
agregada e sem várias tendências prévias, essa hipótese não pode ser avaliada
de forma convincente. Portanto, o notebook corretamente não trata o resultado
como identificação automática por DiD.

### ATT ponderado pelo escore de propensão

Repondera controles para se parecerem com tratados nas covariáveis observadas.
O valor é **−19,50**, com intervalo **[−83,11; 34,16]**. É o estimador mais
alinhado ao ATT declarado, mas depende de ausência de confundimento não medido,
positividade, especificação do escore e balanceamento adequado.

Os três números não competem para escolher o mais favorável. A mudança entre
−83,16 e −19,50 mostra que composição e ajuste importam. O intervalo do ATT
inclui zero: os dados são compatíveis tanto com redução quanto com pequeno
aumento. Isso significa **imprecisão**, não prova de efeito nulo.

## 12. Bootstrap e incerteza

O bootstrap reamostra municípios dentro dos grupos de tratamento, recalcula o
procedimento e usa a distribuição das estimativas para formar intervalos. A
estratificação preserva a existência dos dois grupos, importante com apenas 29
tratados.

Ele representa incerteza amostral sob o processo de reamostragem e as escolhas
do modelo. Não corrige confundimento não medido, erro de mensuração, falta de
suporte, spillovers ou um DAG incorreto. Um intervalo estreito poderia ser
precisamente enviesado; um intervalo amplo pode refletir informação limitada.

## 13. Validade interna, externa e escopo da conclusão

**Validade interna** pergunta se o contraste identifica o efeito nos municípios
estudados. As ameaças principais são confundimento residual, desequilíbrio,
positividade limitada, temporalidade, mudança posterior de tratamento e
spillovers.

**Validade externa** pergunta para onde o resultado pode ser transportado. A
base cobre municípios de Goiás e uma fase específica do PMM; estados, períodos
e desenhos de implementação diferentes podem ter outros mecanismos e efeitos.
Generalizar exige comparar modificadores de efeito e contextos, não apenas
obter significância estatística.

A formulação defensável é: **sob o DAG, as proxies, o modelo de escore e as
hipóteses declaradas, estima-se uma associação ajustada compatível com o ATT da
presença inicial do PMM em Goiás; os dados não oferecem evidência precisa de
redução nas ICSAP em 2014–2015**.

## 14. Roteiro prático para reproduzir o raciocínio

1. Defina unidade, tratamento, comparação, desfecho, janela e estimando.
2. Desenhe o DAG antes de selecionar controles.
3. Classifique variáveis como pré-tratamento, confundidor, mediador ou colisor.
4. Declare o conjunto de ajuste teórico e compare-o às medidas disponíveis.
5. Verifique temporalidade, dados ausentes, escalas, distribuições e suporte.
6. Estime o escore com covariáveis escolhidas por causalidade, não por p-valor.
7. Construa pesos coerentes com ATT, ATE ou ATU.
8. Examine sobreposição, pesos extremos e tamanho efetivo.
9. Avalie balanceamento antes e depois do ajuste.
10. Estime o efeito e a incerteza, incluindo análises de sensibilidade.
11. Separe resultado descritivo, estimativa ajustada e alegação causal.
12. Discuta violações plausíveis e limite a generalização.

## 15. Erros comuns na avaliação observacional

- chamar toda variável associada de confundidor;
- controlar mediadores ou colisores porque melhoram o ajuste do modelo;
- escolher covariáveis por significância estatística;
- supor que o escore de propensão elimina confundimento não observado;
- reportar somente o histograma do escore, sem balanceamento das covariáveis;
- ignorar pesos extremos e falta de suporte comum;
- chamar uma comparação de mudanças de DiD sem justificar tendências paralelas;
- interpretar intervalo que inclui zero como prova de ausência de efeito;
- tratar o bootstrap como solução para viés de identificação;
- generalizar de Goiás para o Brasil sem argumento de transportabilidade.

## 16. Perguntas para autoavaliação

Você compreendeu esta parte se consegue responder:

1. Por que o ATT, e não o ATE, corresponde à pergunta da atividade 1?
2. Qual é o contrafactual ausente dos 29 municípios tratados?
3. Quais caminhos de backdoor aparecem no DAG?
4. Por que acesso pós-PMM e gasto pós-tratamento não devem ser controlados?
5. O que as proxies disponíveis deixam de medir diretamente?
6. Como os pesos \(e(X)/(1-e(X))\) mudam o grupo controle?
7. Por que equilíbrio após ponderação é necessário, mas não suficiente?
8. O que o intervalo [−83,11; 34,16] permite e não permite concluir?
9. Por que a comparação de mudanças não garante um DiD causal?
10. Que violações de consistência, positividade e não interferência são
    plausíveis neste caso?

## 17. Fontes recomendadas para a atividade 1

### Fundamentos e resultados potenciais

- Hernán, M. A.; Robins, J. M. *Causal Inference: What If*. Livro gratuito e
  referência principal para resultados potenciais, identificação, DAGs,
  padronização e ponderação:
  <https://miguelhernan.org/whatifbook>
- Imbens, G. W.; Rubin, D. B. *Causal Inference for Statistics, Social, and
  Biomedical Sciences*. Cambridge University Press:
  <https://doi.org/10.1017/CBO9781139025751>

### DAG e critério de backdoor

- Pearl, J. *Causality: Models, Reasoning, and Inference*. Referência formal
  para DAGs, d-separação e backdoor:
  <https://doi.org/10.1017/CBO9780511803161>
- Textor, J. et al. “Robust causal inference using directed acyclic graphs: the
  R package dagitty”. *International Journal of Epidemiology*:
  <https://doi.org/10.1093/ije/dyw341>

### Escore de propensão e balanceamento

- Rosenbaum, P. R.; Rubin, D. B. “The central role of the propensity score in
  observational studies for causal effects”. *Biometrika*:
  <https://doi.org/10.1093/biomet/70.1.41>
- Austin, P. C. “Balance diagnostics for comparing the distribution of baseline
  covariates between treatment groups in propensity-score matched samples”.
  *Statistics in Medicine*: <https://doi.org/10.1002/sim.3697>
- Stuart, E. A. “Matching methods for causal inference: a review and a look
  forward”. *Statistical Science*: <https://doi.org/10.1214/09-STS313>

### Diferenças-em-diferenças

- Roth, J. et al. “What’s Trending in Difference-in-Differences? A Synthesis of
  the Recent Econometrics Literature”. *Journal of Econometrics*:
  <https://doi.org/10.1016/j.jeconom.2023.03.008>

# Parte II — Atividade 2: planejamento de um experimento aleatorizado

## 1. O problema que o experimento pretende responder

A intervenção fictícia, mas plausível, é uma **oferta prioritária de expansão
do Programa Mais Médicos (PMM)** para municípios de Goiás. A oferta combina
vagas prioritárias, apoio à adesão e início antecipado do provimento.

A pergunta principal é:

> Qual é o efeito de ser sorteado para receber a oferta prioritária do PMM
> sobre a média da taxa anual de internações por condições sensíveis à atenção
> primária nos dois anos seguintes?

O desfecho são as **internações por condições sensíveis à atenção primária
(ICSAP)** por 10 mil habitantes. Em geral, taxas elevadas sugerem que problemas
tratáveis na atenção primária chegaram ao ponto de exigir internação. A relação
não é mecânica: diagnóstico, acesso hospitalar, composição etária e condições
socioeconômicas também afetam a taxa.

### A cadeia causal esperada

Uma teoria de mudança simplificada é:

```text
oferta prioritária
        ↓
adesão e preenchimento de vagas
        ↓
maior disponibilidade e continuidade do cuidado
        ↓
prevenção, diagnóstico e tratamento oportunos
        ↓
menor taxa de ICSAP
```

O experimento testa o efeito da **oferta**, não cada seta isoladamente. Medir
adesão e implementação ajuda a compreender o mecanismo, mas a análise primária
não deve condicionar o resultado a variáveis posteriores ao sorteio.

## 2. Resultados potenciais e efeito causal

Para cada município (i), imagine dois resultados:

- (Y_i(1)): taxa de ICSAP se o município receber oferta prioritária;
- (Y_i(0)): taxa de ICSAP se permanecer no fluxo regular.

O efeito causal individual seria:

$$
Y_i(1)-Y_i(0).
$$

Só observamos um desses resultados para cada município. O outro é o
**contrafactual**. A randomização cria grupos comparáveis que permitem usar a
média do controle como representação do contrafactual médio do tratamento.

### Por que o sorteio identifica o efeito

Se (Z_i) é a designação aleatória, então, antes da implementação:

$$
Z_i \perp (Y_i(1),Y_i(0)).
$$

Isso significa que a designação não depende dos resultados potenciais. Em
expectativa, vulnerabilidade, oferta anterior, capacidade administrativa e
demais características também ficam distribuídas entre os braços.

O sorteio elimina **viés sistemático de seleção**, mas não garante que toda
realização tenha médias idênticas. Pequenos desequilíbrios por acaso são
esperados. Por isso, balanceamento é um diagnóstico descritivo do sorteio, não
um teste que valide ou invalide a randomização.

## 3. O que precisa ser definido antes de sortear

Um experimento não começa pelo código de randomização. Primeiro devem ser
definidos:

1. população elegível;
2. intervenção e comparação;
3. unidade de randomização;
4. desfecho primário;
5. período de acompanhamento;
6. estimando;
7. regras de implementação e não-conformidade;
8. plano de análise;
9. tamanho amostral;
10. salvaguardas éticas.

A formulação explícita desses elementos evita adaptar a pergunta ao resultado
observado. A orientação contemporânea sobre estimandos também recomenda alinhar
objetivo, desenho, eventos posteriores à designação e análise
([ICH E9(R1)](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e9r1-statistical-principles-clinical-trials-addendum-estimands-and-sensitivity-analysis-clinical)).

## 4. Unidades do experimento

Três unidades podem ser diferentes:

| Unidade | Pergunta | Nesta atividade |
|---|---|---|
| Randomização | Quem participa do sorteio? | município |
| Intervenção | Onde a política é implementada? | rede municipal de atenção básica |
| Análise | Quem forma uma observação do desfecho? | município |

Os pacientes estão aninhados nos municípios, mas a base analítica possui uma
taxa por município. Do ponto de vista das pessoas, o ensaio é por clusters; do
ponto de vista da análise principal, há 246 observações municipais.

O [CONSORT para ensaios por clusters](https://www.bmj.com/content/345/bmj.e5661)
recomenda deixar claro o motivo do desenho, como os clusters foram selecionados
e randomizados, quantos foram perdidos e como o agrupamento foi tratado.

## 5. Desenhos de aleatorização

### 5.1 Aleatorização simples

Cada unidade tem probabilidade conhecida de ir para tratamento, sem considerar
covariáveis.

**Vantagens:** simples, transparente e fácil de auditar.

**Limitação:** em amostras pequenas ou heterogêneas, pode produzir desequilíbrio
casual em variáveis prognósticas.

### 5.2 Aleatorização estratificada ou bloqueada

As unidades são separadas em grupos definidos por características anteriores
ao tratamento. O sorteio ocorre dentro de cada bloco.

**Objetivos:**

- garantir representação dos braços nos principais perfis;
- reduzir variância quando as variáveis de bloqueio predizem o desfecho;
- proteger contra uma realização muito desequilibrada.

Bloquear não corrige confundimento: a randomização já identifica o efeito. O
bloqueio busca **precisão e equilíbrio operacional**. A análise deve respeitar
os blocos usados no desenho.

### 5.3 Aleatorização por clusters

Grupos inteiros — municípios, escolas ou unidades de saúde — são sorteados.
Ela é indicada quando:

- a intervenção é entregue coletivamente;
- pessoas do mesmo local compartilham profissionais ou infraestrutura;
- a randomização individual seria inviável;
- há alto risco de contaminação dentro do grupo.

Cluster não é sinônimo de estrato. Nesta atividade:

- **cluster:** município, unidade que recebe o tratamento;
- **bloco:** combinação de quartil de ICSAP prévia e tercil populacional usada
  para organizar o sorteio dos municípios.

### 5.4 Desenho escolhido

O desenho é **randomização por clusters municipais, bloqueada**, com alocação
1:1:

- quartis da taxa prévia de ICSAP: (Q1,…,Q4);
- tercis de população: (P1,P2,P3);
- 12 blocos (Q \times P);
- aproximadamente metade de cada bloco em cada braço.

A região de saúde **não restringe o sorteio**. Ela entra como covariável
categórica pré-especificada na análise. Cruzar região, risco e porte criaria
blocos com pouquíssimos municípios.

## 6. Intervenção, designação e recebimento

É essencial distinguir:

- (Z_i): designação para oferta prioritária;
- (D_i): implementação efetiva do pacote;
- (Y_i): resultado posterior.

Nesta atividade, (D_i=1) exige:

1. adesão municipal ao pacote;
2. preenchimento de pelo menos 80% das vagas prioritárias;
3. mínimo de um profissional;
4. preenchimento em até 90 dias;
5. manutenção do patamar por pelo menos 12 dos primeiros 18 meses.

Uma definição operacional deve ser:

- fixada antes do sorteio;
- verificável em registros administrativos;
- insensível a decisões tomadas depois de ver os resultados;
- coerente com o mecanismo da intervenção.

Presença pontual de um médico seria uma medida fraca, pois não representa dose,
rapidez nem continuidade suficientes para alterar ICSAP.

## 7. Estimando primário: intenção de tratar

O **ITT** (*intention-to-treat*) é o efeito da designação:

$$
ITT=E[Y_i\mid Z_i=1]-E[Y_i\mid Z_i=0].
$$

Ele responde:

> Qual é o efeito de oferecer prioridade, considerando recusas, atrasos,
> dificuldades de preenchimento e contaminações que ocorrem na implementação?

### Por que o ITT é a análise principal

- preserva a comparabilidade criada pelo sorteio;
- mede a política como ofertada no mundo real;
- incorpora dificuldades operacionais relevantes ao gestor;
- evita selecionar apenas municípios que conseguiram implementar.

Analisar somente quem aderiu é **per protocol** ou **as treated**. Essa
comparação geralmente deixa de ser aleatória: municípios que implementam podem
ter maior capacidade, infraestrutura ou motivação.

O princípio ITT recomenda manter as unidades no braço original mesmo quando
não seguem o tratamento planejado. Isso não significa ignorar a
não-conformidade; significa não deixá-la redefinir a comparação causal
principal.

## 8. Análise primária com ajuste de linha de base

O plano usa uma ANCOVA municipal:

$$
Y_{i,post}=\alpha+\tau Z_i+\gamma Y_{i,pre}
+\lambda_{b(i)}+\rho_{r(i)}+\varepsilon_i.
$$

Onde:

- (	au): ITT;
- (Y_{i,pre}): ICSAP anterior ao sorteio;
- (lambda_{b(i)}): efeitos dos blocos;
- (ho_{r(i)}): efeitos das regiões de saúde, usados apenas para precisão.

### Por que ajustar pela linha de base

Se o desfecho prévio prediz o posterior, incluí-lo reduz a variância residual e
aumenta o poder. O ajuste é legítimo porque a variável foi medida antes da
designação. Dados posteriores, como consultas realizadas após o PMM, podem ser
mediadores e não devem entrar automaticamente.

Na base histórica:

- correlação pré–pós: 0,820;
- (R^2) da taxa prévia: 0,672;
- desvio-padrão bruto posterior: 248,067;
- desvio-padrão residual: 142,281.

O ganho de precisão é plausível, mas foi estimado nos mesmos dados históricos.
Em uma implementação real, o cálculo deve ser atualizado com coorte
contemporânea ou validado fora da amostra. Estudos de desenho mostram que
ANCOVA pode ganhar poder quando existe correlação basal relevante
([McKenzie, 2012](https://blogs.worldbank.org/en/impactevaluations/collecting-more-rounds-of-data-to-boost-power-the-new-stuff)).

## 9. MDE, poder e tamanho de amostra

### 9.1 Conceitos

**Erro tipo I (α):** concluir que existe efeito quando não existe. O desenho
usa α bilateral de 5%.

**Erro tipo II (β):** não detectar um efeito que existe.

**Poder ((1-\beta)):** probabilidade de rejeitar a hipótese nula quando o
efeito verdadeiro tem a magnitude especificada. O desenho usa 80%.

**MDE:** menor efeito verdadeiro que o desenho detecta com o poder e o nível de
significância escolhidos. Não é o menor efeito socialmente importante e não é
uma previsão do efeito.

O guia de poder do [J-PAL](https://www.povertyactionlab.org/resource/power-calculations)
destaca que MDE, tamanho amostral, variância, alocação, adesão e desenho estão
interligados. Não existe um MDE universalmente “bom”; ele depende da relevância
para a política e do custo de oportunidade da pesquisa.

### 9.2 Fórmula usada

Para dois braços igualmente divididos e desfecho contínuo municipal:

$$
N=\frac{4(z_{1-\alpha/2}+z_{1-\beta})^2\sigma_{res}^2}{\delta^2}.
$$

Parâmetros:

| Símbolo | Valor | Significado |
|---|---:|---|
| α | 0,05 | significância bilateral |
| poder | 0,80 | (1-\beta) |
| (z_{0,975}) | 1,960 | crítico bilateral |
| (z_{0,80}) | 0,842 | crítico de poder |
| (sigma_{res}) | 142,281 | DP residual histórico |
| (delta) | 52 | MDE por 10 mil |

Substituindo:

$$
N=\frac{4(1{,}960+0{,}842)^2(142{,}281)^2}{52^2}
\approx235{,}05.
$$

Arredondamento sempre para cima:

$$N=236\text{ municípios}.$$

Com previsão de 5% de perda:

$$
N_{convite}=\left\lceil\frac{236}{0{,}95}\right\rceil=249.
$$

Goiás possui 246 municípios, então todos são convidados, 123 por braço. Com
aproximadamente 234 resultados disponíveis, o MDE alcançável é:

$$
MDE=2(1{,}960+0{,}842)\frac{142{,}281}{\sqrt{234}}
\approx52{,}12.
$$

### 9.3 Por que 52 por 10 mil é relevante

O valor representa cerca de 14% da média histórica de 362 por 10 mil. Em um
município com 20 mil habitantes:

$$
52\times\frac{20.000}{10.000}=104
$$

internações evitadas por ano, ou cerca de 208 em dois anos se o efeito for
sustentado. Essa magnitude pode reduzir:

- ocupação de leitos;
- deslocamentos de pacientes e familiares;
- despesas hospitalares;
- pressão sobre urgência e regulação.

Isso torna plausível justificar recrutamento, instalação e retenção de
profissionais. Uma avaliação econômica definitiva precisaria comparar o custo
real do pacote com custos evitados e benefícios de saúde.

Efeitos menores podem ser relevantes, mas o estudo estadual não consegue
distingui-los com 80% de poder. O MDE é uma propriedade do desenho, não uma
fronteira de importância.

### 9.4 Por que não foi aplicado ICC

O resultado principal é uma taxa por município e a análise tem uma linha por
cluster. Logo, σ já representa variabilidade entre clusters.

Se o resultado fosse individual, pessoas do mesmo município seriam
correlacionadas. Seria necessário usar o efeito de desenho:

$$
DE=1+(m-1)\rho,
$$

em que (m) é o tamanho médio do cluster e ρ é a correlação intraclasse
(ICC). Muitos indivíduos não compensam poucos clusters quando o ICC é
positivo.

## 10. Randomização reproduzível e balanceamento

Um protocolo de sorteio deve registrar:

- lista final de elegíveis;
- variáveis e pontos de corte dos blocos;
- proporção de tratamento;
- regra para blocos ímpares;
- semente aleatória;
- software e versão;
- responsável e testemunha/auditoria;
- momento em que a alocação será revelada.

Na ilustração do notebook, a semente é `20260804`, com 123 municípios por braço.
As diferenças padronizadas foram:

| Variável | Diferença padronizada |
|---|---:|
| ICSAP prévia | -0,068 |
| Internações clínicas prévias | -0,058 |
| Log da população | 0,020 |

### Como interpretar

A diferença padronizada é:

$$
SMD=\frac{\bar X_T-\bar X_C}
{\sqrt{(s_T^2+s_C^2)/2}}.
$$

Valores próximos de zero indicam semelhança. O valor 0,10 é frequentemente
usado como referência descritiva, não como teste rígido.

Não se deve repetir o sorteio até encontrar a tabela “mais bonita”. Se houver
randomização restrita, todas as regras de aceitação precisam ser definidas
antes. O [J-PAL](https://www.povertyactionlab.org/resource/randomization?lang=en)
discute como estratificação e outras restrições podem melhorar equilíbrio e
precisão.

## 11. Não-conformidade

Não-conformidade ocorre quando (D_i\neq Z_i).

### No braço de oferta

- município recusa;
- documentação atrasa;
- vagas não são preenchidas;
- profissionais deixam o município cedo;
- implementação fica abaixo de 80%.

### No controle

- município recebe vaga por outro ciclo;
- emergência ou decisão judicial antecipa atendimento;
- outra modalidade de provimento produz intervenção semelhante.

Esses eventos reduzem o contraste entre os braços e, portanto, diluem o ITT.
Não são motivo para excluir municípios da análise principal.

## 12. Primeiro estágio e LATE

O **primeiro estágio** mede quanto a designação altera o recebimento:

$$
\pi=E[D_i\mid Z_i=1]-E[D_i\mid Z_i=0].
$$

Se a oferta elevar o recebimento de 10% para 80%, então:

$$\pi=0{,}80-0{,}10=0{,}70.$$

O estimador de Wald é:

$$
LATE=\frac{ITT}{\pi}.
$$

Se ∣ITT∣ = 52 e π = 0,70:

$$
|LATE|=\frac{52}{0{,}70}\approx74{,}29.
$$

### O que o LATE responde

O LATE é o efeito da implementação efetiva para os **conformes**: municípios
que implementariam se recebessem prioridade e não implementariam se ficassem
no fluxo regular.

Ele não é automaticamente o ATE de todos os municípios.

### Estratos principais

| Tipo | (D(1)) | (D(0)) | Interpretação |
|---|---:|---:|---|
| Sempre aderente | 1 | 1 | implementa em qualquer braço |
| Conforme | 1 | 0 | implementação muda com a oferta |
| Nunca aderente | 0 | 0 | não implementa em nenhum braço |
| Desafiante | 0 | 1 | faz o oposto da designação |

### Hipóteses para interpretar IV como LATE

1. **Designação aleatória/independência:** (Z) é independente dos resultados
   potenciais e dos tipos de conformidade.
2. **Relevância:** (Z) altera a probabilidade de (D); π não é zero.
3. **Exclusão:** (Z) afeta (Y) somente por meio da implementação definida em
   (D).
4. **Monotonicidade:** não existem desafiantes; oferecer prioridade não reduz a
   implementação para algum município.
5. **SUTVA/interferência controlada:** a designação de um município não altera
   o resultado de outro por canais não modelados.

O artigo clássico de
[Angrist, Imbens e Rubin](https://dash.harvard.edu/entities/publication/73120378-82c1-6bd4-e053-0100007fdf3b)
formaliza a interpretação causal de variáveis instrumentais e do efeito local.

### A exclusão é especialmente delicada aqui

A oferta inclui apoio à adesão e prioridade temporal. Para a exclusão ser
plausível, (D) precisa representar suficientemente o pacote por meio do qual
a oferta afeta ICSAP. Se o apoio administrativo melhorar a atenção básica mesmo
sem preencher o critério de (D), existe um caminho direto (Z\rightarrow Y)
e o LATE de Wald perde sua interpretação.

Por isso:

- ITT permanece o resultado principal;
- LATE é secundário;
- canais diretos da oferta devem ser documentados;
- a definição de (D) não pode ser alterada após observar os dados.

## 13. ITT não resolve dados ausentes

Manter o braço original não recupera um desfecho que não foi observado.
Perda de município, falha de vinculação ou mudança de código pode gerar viés se
a ausência depender do braço e do resultado.

O protocolo deve:

- usar fontes administrativas com cobertura uniforme;
- registrar perdas e motivos por braço;
- evitar excluir municípios por baixa adesão;
- definir regras para mudanças territoriais;
- fazer análises de sensibilidade para dados ausentes;
- distinguir perda do desfecho de não-conformidade do tratamento.

## 14. Interferência e spillovers

SUTVA pressupõe que o resultado de um município não dependa da designação de
outros. Isso pode falhar porque:

- pacientes cruzam fronteiras;
- médicos migram entre municípios;
- redes regionais compartilham hospitais;
- municípios copiam práticas de gestão.

A randomização municipal reduz contaminação dentro do município, mas não
elimina spillovers entre municípios. Medidas práticas:

- registrar fluxos de pacientes e profissionais;
- mapear municípios vizinhos;
- pré-especificar análise de sensibilidade espacial;
- interpretar o ITT como efeito da oferta no sistema existente, que pode incluir
  algum spillover.

## 15. Ética em ensaios por clusters

Ensaios por clusters trazem questões adicionais porque autoridades podem
autorizar a participação institucional, enquanto pessoas dentro do cluster
podem ser afetadas sem participar da decisão de alocação.

A [Diretriz 21 do CIOMS](https://www.ncbi.nlm.nih.gov/books/NBK614412/)
recomenda identificar quem são os participantes, quem é apenas afetado, quando
é necessário consentimento individual e qual autoridade legítima pode permitir
a entrada do cluster. O
[Ottawa Statement](https://pmc.ncbi.nlm.nih.gov/articles/PMC3502500/)
detalha a função e os limites dos *gatekeepers*.

### Condições éticas neste desenho

1. **Equipoise:** existe incerteza legítima sobre o efeito da oferta nas ICSAP.
2. **Escassez real:** não há vagas para todos simultaneamente.
3. **Não retirada:** o experimento não remove médicos ou cuidado existente.
4. **Lista de espera:** controles podem receber expansão depois.
5. **Exceção emergencial:** necessidade grave prevalece sobre o protocolo; a
   unidade continua no ITT.
6. **Critérios públicos:** elegibilidade deve ser definida antes do sorteio.
7. **Justiça:** prioridade aleatória é mais defensável que escolha política
   opaca quando unidades são igualmente elegíveis.
8. **Privacidade:** dados individuais usados para produzir taxas devem ser
   protegidos.
9. **Transparência:** protocolo, plano analítico e resultados devem ser
   publicados, inclusive resultados nulos.

No Brasil, a avaliação precisa considerar o Sistema CEP/Conep e a
[Resolução CNS nº 466/2012](https://www.gov.br/conselho-nacional-de-saude/pt-br/atos-normativos/resolucoes/2012/resolucao-no-466.pdf/view).
A [Declaração de Helsinque de 2024](https://www.wma.net/policies-post/wma-declaration-of-helsinki/)
é referência internacional para pesquisa médica envolvendo participantes e
dados identificáveis.

## 16. Validade interna e validade externa

### Validade interna

Pergunta: o efeito estimado é causal para os municípios participantes?

Ameaças:

- quebra ou manipulação da randomização;
- perda diferencial do desfecho;
- interferência;
- análise não compatível com os blocos;
- mudança pós-hoc do desfecho;
- múltiplas análises selecionadas por significância.

### Validade externa

Pergunta: o resultado pode ser transportado para outros municípios, ciclos ou
estados?

Limitações do estudo:

- Goiás tem rede e epidemiologia próprias;
- municípios que aceitam participar podem ser diferentes;
- emergências são excluídas antes do sorteio;
- uma expansão escassa não equivale a política universal permanente;
- perfil e retenção dos profissionais variam;
- SIH cobre internações financiadas pelo SUS;
- parâmetros de 2013–2015 podem não representar período contemporâneo.

Uma amostra grande não garante generalização. É necessário comparar população
estudada, população-alvo, implementação, mecanismos e contexto.

## 17. Validade estatística e validade política

Um resultado pode ser:

- estatisticamente preciso, mas pequeno demais para justificar custo;
- substantivamente grande, mas impreciso;
- internamente válido, mas pouco generalizável;
- detectável no ITT, mas não no LATE;
- nulo porque não houve efeito ou porque o estudo teve pouco poder.

Por isso, a interpretação deve apresentar conjuntamente:

1. estimativa pontual;
2. intervalo de confiança;
3. MDE planejado;
4. adesão e primeiro estágio;
5. custos e consequências práticas;
6. população à qual o efeito se aplica.

## 18. Protocolo mínimo antes da implementação

### Política e população

- [ ] definir pacote, dose, duração e responsáveis;
- [ ] congelar lista de municípios elegíveis;
- [ ] excluir emergências por regra anterior ao sorteio;
- [ ] documentar capacidade limitada e lista de espera.

### Desenho

- [ ] confirmar município como cluster;
- [ ] construir os 12 blocos com dados pré-tratamento;
- [ ] definir regra para blocos ímpares;
- [ ] registrar semente e algoritmo;
- [ ] proteger sigilo da alocação até o momento adequado.

### Mensuração

- [ ] definir ICSAP, numerador, denominador e janela temporal;
- [ ] registrar taxa basal antes do sorteio;
- [ ] registrar vagas, preenchimento, datas e permanência mensal;
- [ ] acompanhar spillovers e mudanças territoriais.

### Análise

- [ ] declarar ITT como estimando primário;
- [ ] pré-especificar ANCOVA, blocos e região;
- [ ] definir primeiro estágio e LATE secundário;
- [ ] planejar perdas e análises de sensibilidade;
- [ ] registrar protocolo e plano antes dos resultados.

### Ética e transparência

- [ ] obter avaliação ética e autorizações legítimas;
- [ ] definir consentimento ou justificativa de dispensa conforme participantes
  e dados;
- [ ] proteger cuidado padrão e exceções emergenciais;
- [ ] publicar resultados independentemente do sinal.

O [CONSORT 2025](https://www.bmj.com/content/389/bmj-2024-081123)
é a referência geral atual de relato de ensaios; a extensão específica para
clusters deve ser usada conjuntamente enquanto não houver substituição própria
mais recente.

## 19. Erros comuns que você deve saber reconhecer

1. **Confundir cluster com estrato.** Município é cluster; risco × porte forma
   o bloco.
2. **Dizer que randomização garante igualdade exata.** Ela garante equilíbrio
   em expectativa.
3. **Refazer o sorteio porque uma covariável ficou “significativa”.** Isso muda
   o mecanismo sem regra prévia.
4. **Excluir quem não aderiu.** Isso rompe a comparação aleatória.
5. **Chamar LATE de efeito para todos.** Ele se aplica aos conformes.
6. **Usar MDE como previsão.** MDE é capacidade de detecção.
7. **Escolher MDE apenas para caber na amostra.** Ele precisa de justificativa
   política.
8. **Ignorar take-up no poder do LATE.** Primeiro estágio fraco aumenta muito a
   incerteza.
9. **Controlar mediadores pós-sorteio no ITT.** Isso altera o estimando.
10. **Achar que ITT resolve atrito.** ITT preserva designação, não cria dados
    ausentes.
11. **Aplicar design effect duas vezes.** Com uma taxa por cluster, a variância
    já é entre clusters.
12. **Generalizar de Goiás para o Brasil sem argumento de transporte.** Validade
    interna e externa são problemas diferentes.

## 20. Perguntas para autoavaliação

Você compreendeu o material se consegue responder, sem consultar o notebook:

1. Por que pacientes não são randomizados individualmente?
2. Qual é a diferença entre cluster e bloco?
3. Por que a região entra na análise, mas não restringe o sorteio?
4. O que (Z), (D) e (Y) representam?
5. Por que ITT continua válido com não adesão?
6. Por que uma análise apenas entre aderentes é enviesada?
7. O que o primeiro estágio mede?
8. Para quem o LATE é válido?
9. Quais hipóteses são necessárias para o estimador de Wald?
10. Por que exclusão é delicada no pacote proposto?
11. Como se chega aos 236 municípios?
12. Por que 249 seriam desejáveis com 5% de perda?
13. Por que o MDE de 52 não significa que 40 seja irrelevante?
14. Por que não foi usado ICC no cálculo principal?
15. Quais spillovers podem ocorrer entre municípios?
16. Quando o sorteio por lista de espera é eticamente defensável?
17. Qual é a população para a qual o ITT pode ser generalizado diretamente?

## 21. Exercícios práticos

### Exercício 1 — poder

Refaça o cálculo com:

- MDE de 40;
- poder de 90%;
- desvio-padrão residual 20% maior.

Explique qual parâmetro aumenta mais a amostra e por quê.

### Exercício 2 — não-conformidade

Suponha:

- ITT = -30;
- recebimento no tratamento = 75%;
- recebimento no controle = 15%.

Calcule π e LATE. Depois liste situações que violariam exclusão.

### Exercício 3 — ética

Considere que cinco municípios estejam em emergência sanitária. Explique por
que devem ser atendidos antes do sorteio e como isso muda a população-alvo.

### Exercício 4 — interpretação

Imagine estimativa ITT de -20 com IC95% [-60; 20]. Escreva uma conclusão que
diferencie estimativa pontual, incerteza, MDE e relevância política.

## 22. Glossário essencial

| Termo | Definição curta |
|---|---|
| ATE | efeito médio do tratamento na população |
| ATT | efeito médio entre tratados |
| ITT | efeito da designação/oferta original |
| LATE | efeito do recebimento entre conformes |
| Cluster | grupo sorteado como unidade |
| Bloco/estrato | conjunto de unidades semelhantes dentro do qual ocorre sorteio |
| Contrafactual | resultado que teria ocorrido sob outra condição |
| MDE | menor efeito detectável com poder especificado |
| Poder | probabilidade de detectar um efeito da magnitude planejada |
| Primeiro estágio | efeito de (Z) sobre (D) |
| Exclusão | (Z) afeta (Y) somente por (D) |
| Monotonicidade | não existem unidades que fazem o oposto da oferta |
| ICC | semelhança de resultados dentro do cluster |
| Spillover | efeito da designação de uma unidade sobre outra |
| Equipoise | incerteza legítima sobre qual condição é superior |
| ANCOVA | regressão do resultado posterior ajustada pelo resultado basal |
| SMD | diferença de médias em unidades de desvio-padrão |
| Atrito | perda de observações do desfecho |
| Validade interna | credibilidade causal para a amostra estudada |
| Validade externa | possibilidade de transportar o resultado para outro contexto |

## 23. Fontes recomendadas

### Começar por estas

1. [J-PAL — Power calculations](https://www.povertyactionlab.org/resource/power-calculations):
   poder, MDE, tamanho amostral, estratificação e clusters.
2. [J-PAL — Quick guide to power calculations](https://www.povertyactionlab.org/resource/quick-guide-power-calculations):
   escolha substantiva do MDE e uso prático do cálculo.
3. [J-PAL — Randomization](https://www.povertyactionlab.org/resource/randomization?lang=en):
   unidade de randomização, balanceamento, estratificação e spillovers.
4. [World Bank — Impact Evaluation in Practice](https://documents1.worldbank.org/curated/en/823791468325239704/pdf/Impact-evaluation-in-practice.pdf):
   introdução aplicada a desenho experimental e poder.

### Ensaios por clusters

5. [CONSORT 2010 extension to cluster randomised trials](https://www.bmj.com/content/345/bmj.e5661):
   itens específicos de desenho, análise e relato de clusters.
6. [Imai, King e Nall — cluster matching](https://arxiv.org/abs/0910.3752):
   razões de precisão para parear ou bloquear clusters.
7. Hayes, R. J.; Moulton, L. H. *Cluster Randomised Trials*. 2. ed. CRC
   Press, 2017: referência técnica extensa.

### ITT, estimandos e LATE

8. [Angrist, Imbens e Rubin — Identification of Causal Effects Using Instrumental Variables](https://dash.harvard.edu/entities/publication/73120378-82c1-6bd4-e053-0100007fdf3b):
   base formal do LATE.
9. [FDA/ICH E9(R1) — Estimands and Sensitivity Analysis](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e9r1-statistical-principles-clinical-trials-addendum-estimands-and-sensitivity-analysis-clinical):
   alinhamento entre pergunta, eventos pós-designação e análise.
10. Hernán, M. A.; Robins, J. M. *Causal Inference: What If*. 2020:
    resultados potenciais, experimentos e não adesão.

### Ética e transparência

11. [CIOMS — Guideline 21: Cluster Randomized Trials](https://www.ncbi.nlm.nih.gov/books/NBK614412/):
    participantes, pessoas afetadas, consentimento e gatekeepers.
12. [Ottawa Statement](https://pmc.ncbi.nlm.nih.gov/articles/PMC3502500/):
    ética específica de ensaios por clusters.
13. [Declaração de Helsinque, versão 2024](https://www.wma.net/policies-post/wma-declaration-of-helsinki/):
    princípios internacionais atuais.
14. [Resolução CNS nº 466/2012](https://www.gov.br/conselho-nacional-de-saude/pt-br/atos-normativos/resolucoes/2012/resolucao-no-466.pdf/view):
    diretrizes brasileiras para pesquisa envolvendo seres humanos.
15. [CONSORT 2025](https://www.bmj.com/content/389/bmj-2024-081123):
    padrão geral atual de relato transparente de ensaios randomizados.

## Síntese final da Parte II

A lógica completa da atividade pode ser resumida assim:

1. a política atua no município, portanto o município é randomizado;
2. risco basal e porte formam blocos para proteger precisão;
3. a oferta aleatória identifica o ITT;
4. implementação imperfeita não autoriza excluir municípios;
5. o LATE usa a oferta como instrumento, mas exige hipóteses adicionais;
6. a taxa basal reduz a variância da análise e do cálculo de poder;
7. 246 municípios permitem detectar aproximadamente 52 ICSAP por 10 mil com
   80% de poder sob as premissas usadas;
8. detectabilidade não é sinônimo de relevância;
9. o sorteio só é ético se organizar escassez real sem retirar cuidado;
10. validade causal em Goiás não garante generalização nacional.

# Síntese integrada das duas atividades

A atividade 1 pergunta o que pode ser aprendido de uma implantação já
observada. Seu ponto crítico é a **identificação**: tornar explícito por que os
controles ponderados poderiam representar o resultado contrafactual dos
tratados. O DAG, o critério de backdoor, o suporte e o balanceamento sustentam
esse argumento, mas não eliminam a fragilidade causada por confundidores não
medidos.

A atividade 2 pergunta como produzir evidência mais forte em uma nova expansão.
Seu ponto crítico é o **desenho**: usar o sorteio para criar comparabilidade,
dimensionar a amostra antes de observar efeitos e preservar o ITT diante da
implementação imperfeita. O LATE responde a uma pergunta complementar e mais
restrita, sob hipóteses adicionais.

Assim, o aprendizado central é que nenhum estimador é causal apenas por sua
fórmula. A interpretação depende de uma pergunta bem definida, de um estimando
coerente, de um desenho capaz de identificá-lo, de diagnósticos compatíveis com
esse desenho e de uma exposição transparente das ameaças à validade. Na
atividade observacional, as hipóteses substituem a aleatorização; no
experimento, a aleatorização fortalece a validade interna, mas não resolve
automaticamente não conformidade, perdas, interferência, ética ou
generalização.

# Parte III — Atividade 3: Bolsa Família e evasão escolar

## 1. Pergunta, população e estimando

A terceira atividade retorna à AIBF II e estende a análise de pareamento e
escore de propensão feita em aula. O desfecho da aula era `p_attend7`, a
proporção de dias frequentados na última semana. A entrega usa `dropout`, que
vale 1 para abandono escolar e 0 para permanência entre crianças e adolescentes
que estudavam no ano anterior.

Os elementos da pergunta são:

| Elemento | Definição |
|---|---|
| Unidade | pessoa de 6 a 17 anos |
| Tratamento | viver em domicílio com ao menos um titular do cartão do PBF |
| Controle | C1: domicílio cadastrado, mas não beneficiário |
| Desfecho | evasão escolar, `dropout` |
| População analítica | pessoas com `dropout` observado e covariáveis completas |
| Estimando | ATT entre beneficiários com suporte comum |

Formalmente:

\[
ATT=E[Y(1)-Y(0)\mid D=1].
\]

O ATT responde o que teria acontecido com os beneficiários se, contrariando o
observado, seus domicílios não tivessem recebido o programa. Como `Y=1` é um
resultado ruim, ATT negativo favorece o programa. O efeito é uma **diferença de
risco**: `-0,011` corresponde a menos 1,1 ponto percentual, não a menos 1,1% de
risco relativo.

## 2. Por que usar somente o controle C1

A AIBF II distingue beneficiários, controles cadastrados (C1) e controles não
cadastrados (C2). Inscrição no Cadastro Único pode refletir informação,
motivação, acesso a serviços e capacidade de lidar com a burocracia. Comparar
beneficiários com C2 acrescentaria esse mecanismo de seleção ao mecanismo de
concessão do benefício.

Beneficiários e C1 atravessaram ao menos o filtro comum do cadastro. Isso não
garante ignorabilidade, mas torna a comparação substantivamente mais plausível.
No código, a filtragem por `estrato_amostral` deve ocorrer explicitamente; não
basta classificar toda observação sem titular como controle.

## 3. Por que evasão e qual é a população implícita

`p_attend7` é muito concentrada em 1 e oferece pouca variação. Evasão é um
desfecho de política claro, binário e diretamente interpretável. Entretanto,
`dropout` só existe para quem estudava no ano anterior. A conclusão, portanto,
não vale para toda criança pobre, mas para beneficiários que pertencem a essa
subpopulação e têm dados completos.

Essa restrição também pode causar **viés de seleção**. Se o tratamento anterior
afetou a chance de estudar no ano anterior, condicionar nessa condição seleciona
uma variável potencialmente pós-tratamento. A base transversal usada na aula
não permite resolver isso. Na defesa, essa limitação deve ser mencionada antes
de generalizar o resultado.

## 4. Conjunto de ajuste e temporalidade

O notebook usa as mesmas sete covariáveis da aula:

- idade;
- sexo;
- escolaridade do chefe do domicílio;
- número de moradores;
- número de cômodos;
- número de dormitórios;
- água canalizada.

Elas representam composição demográfica e vulnerabilidade socioeconômica, que
podem influenciar tanto a concessão do benefício quanto a evasão. Não entram
frequência recente, faltas, série atual, renda contemporânea ou mecanismos como
merenda: variáveis posteriores ao tratamento podem ser mediadores, colisores ou
descendentes e mudar o efeito total pretendido.

O princípio é escolher covariáveis pelo papel causal e pela precedência
temporal, não por correlação com `Y`, significância estatística ou ganho de AUC.
A limitação é que o extrato não mede completamente renda prévia, qualidade e
distância da escola, motivação familiar, oferta local e choques domésticos.

## 5. Ignorabilidade, positividade, consistência e interferência

A hipótese central é:

\[
(Y(0),Y(1))\perp D\mid X.
\]

Ela afirma que, dentro de perfis iguais de `X`, beneficiários e controles C1
seriam permutáveis. É uma hipótese sobre resultados potenciais não observados e
não pode ser testada pelo love plot. Balancear `X` mostra que o método executou
o ajuste pretendido; não mostra que `X` contém todos os confundidores.

Também são necessárias:

- **positividade:** todo perfil tratado relevante possui chance positiva de
  aparecer como controle;
- **consistência:** `D=1` representa uma versão suficientemente definida do
  tratamento, embora valor e duração do benefício possam variar;
- **não interferência:** o benefício de um domicílio não altera os resultados
  potenciais de outro, hipótese ameaçada por redes familiares ou efeitos locais;
- **mensuração adequada:** tratamento, abandono e covariáveis precisam
  representar os conceitos pretendidos.

## 6. Escore de propensão

O escore é:

\[
e(X)=P(D=1\mid X).
\]

Sob ignorabilidade dado `X`, unidades com o mesmo escore têm, em expectativa,
a mesma distribuição de `X` nos dois grupos. O escore reduz um vetor de
covariáveis a uma dimensão, mas não cria informação onde não há suporte e não
corrige confundidores ausentes.

Não existe um escore intrínseco da família. Ele depende da definição de
tratamento, amostra, rodada, controles e covariáveis. Nesta entrega são
comparados:

1. **regressão logística**, com relação linear aditiva no logito;
2. **random forest calibrado**, capaz de representar interações e não
   linearidades.

Ambos produzem previsões out-of-fold em cinco partições. O random forest usa
folhas mínimas para regularização e calibração sigmoide interna. Separar treino
e previsão reduz o otimismo do ajuste. Calibração importa porque IPW interpreta
o escore como probabilidade, não apenas como ranking.

### Por que AUC não escolhe o melhor escore

AUC mede discriminação do tratamento. Um valor muito alto pode significar que
tratados e controles são fáceis de separar e, portanto, que há pouca
sobreposição. O objetivo causal é produzir balanceamento depois do ajuste. Na
atividade, o random forest tem AUC um pouco maior, mas seu IPW deixa uma
covariável acima do limiar de SMD; a logística é mais convincente para o uso
causal.

## 7. Pareamento para ATT

Cada tratado é associado ao controle de escore mais próximo. A busca parte dos
tratados porque o contrafactual desejado é `Y(0)` para quem recebeu o programa.
Parear no sentido contrário estimaria o ATU.

A entrega usa um vizinho e reposição. Reposição permite que um bom controle
represente mais de um tratado, importante quando há menos controles que
beneficiários. O ATT é:

\[
\widehat{ATT}_{match}=\frac{1}{N_1}\sum_{i:D_i=1}
\{Y_i-Y_{j(i)}\}.
\]

O peso de cada controle no diagnóstico é o número de vezes em que foi usado.
Pareamento pode ter menor tamanho efetivo e ser sensível à especificação do
escore. Perfis diferentes também podem compartilhar o mesmo escore; por isso o
balanceamento deve ser verificado nas covariáveis originais.

## 8. IPW correto para ATT

Os pesos de ATT são:

\[
w_i^{ATT}=D_i+(1-D_i)\frac{e(X_i)}{1-e(X_i)}.
\]

Tratados recebem peso 1. Controles com perfil comum entre tratados recebem
maior peso. A forma normalizada de Hájek calcula:

\[
\widehat{ATT}_{IPW}=
\frac{\sum_iD_iY_i}{\sum_iD_i}-
\frac{\sum_i(1-D_i)w_iY_i}{\sum_i(1-D_i)w_i}.
\]

Esses pesos não são os pesos de ATE `1/e(X)` e `1/[1-e(X)]` usados no exemplo
didático da aula. Misturar pesos de ATE com uma pergunta de ATT produz
estimandos incoerentes.

Escores de controle próximos de 1 geram pesos grandes. Deve-se inspecionar peso
máximo, distribuição e tamanho efetivo da amostra, e não truncar pesos apenas
porque o resultado ficou instável. Truncamento muda a população implícita e
precisa ser declarado.

## 9. Suporte comum e tamanho efetivo

A análise restringe cada modelo à interseção dos intervalos de escore de
tratados e controles. Quase todos os tratados permanecem, mas a conclusão
formal passa a ser o ATT dos beneficiários com suporte observado.

O tamanho efetivo é:

\[
ESS=\frac{(\sum_iw_i)^2}{\sum_iw_i^2}.
\]

Mesmo com milhares de linhas, pesos concentrados podem equivaler a uma amostra
muito menor. No pareamento, o ESS dos controles fica próximo de mil; no IPW,
próximo de dois mil. Isso ajuda a explicar por que o pareamento varia mais entre
logística e random forest.

## 10. SMD e love plot

Para uma covariável contínua, a SMD antes do ajuste é:

\[
SMD=\frac{\bar X_1-\bar X_0}
{\sqrt{(s_1^2+s_0^2)/2}}.
\]

Depois do ajuste, as médias são ponderadas, mas a entrega mantém o desvio-padrão
pré-ajuste no denominador. Isso torna a escala comparável antes e depois. Para
indicadores binários, a interpretação é análoga. `|SMD|<0,1` é uma regra
prática, não um teste ou garantia causal.

O love plot coloca `|SMD|` de todas as covariáveis antes e depois em um mesmo
gráfico. Na amostra bruta, quatro das sete covariáveis superam 0,1, sobretudo
escolaridade do chefe, moradores, água e cômodos. Depois:

- logística + pareamento: máximo `|SMD|=0,035`;
- logística + IPW: máximo `|SMD|=0,041`;
- random forest + pareamento: máximo `|SMD|=0,035`;
- random forest + IPW: máximo `|SMD|=0,108`, em água canalizada.

O diagnóstico favorece o escore logístico. Um love plot bonito, porém, só fala
sobre as colunas mostradas.

## 11. Resultados empíricos

A amostra final contém 8.484 pessoas: 6.054 beneficiárias e 2.430 controles C1.
A evasão observada é 6,89% nos beneficiários e 7,86% nos controles, diferença
bruta de `-0,97` ponto percentual.

| Escore | Método | ATT aproximado |
|---|---|---:|
| Logística | pareamento 1:1 | -1,55 p.p. |
| Logística | IPW-ATT | -1,11 p.p. |
| Random forest calibrado | pareamento 1:1 | -2,33 p.p. |
| Random forest calibrado | IPW-ATT | -1,11 p.p. |

O IPW é estável à troca do modelo; o pareamento é mais sensível. A especificação
principal mais defensável é logística + IPW: produz bom balanceamento, maior ESS
que o pareamento e ATT de aproximadamente `-1,11` p.p. O notebook apresenta
intervalos normais aproximados com erro-padrão agrupado por domicílio. Eles
capturam dependência intradomiciliar, mas condicionam nos escores estimados e
podem subestimar a incerteza total. Para a especificação principal, o IC95%
aproximado é `[-2,62; 0,41]` p.p. e inclui zero: a direção é compatível com
redução da evasão, mas a estimativa não é suficientemente precisa para afastar
efeito nulo nesse nível de confiança.

## 12. Como defender a interpretação

Uma formulação adequada é:

> Entre beneficiários de 6 a 17 anos, com evasão observada, casos completos e
> suporte nos controles cadastrados, o ajuste por escore é compatível com uma
> redução de cerca de 1,1 ponto percentual na evasão pelo estimador principal.
> Essa leitura é causal somente se as sete covariáveis tornarem tratamento
> ignorável e se consistência, positividade e não interferência forem válidas.

Não se deve dizer que o love plot provou causalidade, que ML descobriu o escore
verdadeiro, que ausência de significância prova efeito zero ou que o resultado
vale para todas as crianças brasileiras.

### Perguntas prováveis na apresentação

**Por que ATT, e não ATE?**  
Porque a pergunta retrospectiva é se o programa funcionou para quem o recebeu.
O ATT também evita extrapolar o efeito para famílias não beneficiárias com
perfis possivelmente distintos.

**Por que não usar C2?**  
Porque não cadastrados não passaram pelo mesmo processo de seleção para o
Cadastro Único. C1 reduz, embora não elimine, diferenças não observadas ligadas
à iniciativa de se cadastrar.

**Por que logística se o random forest prevê melhor?**  
Porque previsão do tratamento não é o objetivo. A logística produziu melhor
balanceamento no IPW; esse é o diagnóstico pertinente ao desenho causal.

**Por que calibrar o random forest?**  
Porque IPW usa probabilidades em razões de chances. Um ranking correto com
probabilidades mal calibradas gera pesos errados ou extremos.

**Por que os métodos dão números diferentes?**  
Pareamento reutiliza controles locais e descarta informação efetiva; IPW usa
todos os controles no suporte com pesos contínuos. Ambos também respondem às
aproximações dos respectivos modelos de escore.

**Balanceamento confirma ignorabilidade?**  
Não. Confirma equilíbrio somente nas covariáveis observadas. Ignorabilidade
inclui a afirmação não testável de que não restou confundimento relevante.

**Qual é a principal ameaça?**  
Confundimento residual por renda prévia detalhada, qualidade da escola,
motivação familiar e condições locais, além da seleção de quem possui
`dropout` observado.

**Por que agrupar a incerteza por domicílio?**  
Tratamento é domiciliar e irmãos compartilham ambiente e choques; tratá-los como
independentes produziria erro-padrão excessivamente otimista.

## 13. Síntese integrada das três atividades

A atividade 1 usa DAG e backdoor para explicitar como uma avaliação
observacional depende de confundidores medidos. A atividade 2 mostra como um
sorteio cria comparabilidade e desloca o foco para ITT, poder, não conformidade
e ética. A atividade 3 aprofunda a primeira estratégia: alinha todos os métodos
ao ATT, compara especificações do escore, verifica sobreposição, pesos, ESS e
SMD, e demonstra por que desempenho preditivo não substitui diagnóstico causal.

As três chegam à mesma regra: o número final não carrega causalidade sozinho.
Pergunta, estimando, desenho, temporalidade, suporte, diagnóstico e hipóteses
substantivas precisam permanecer alinhados do início à interpretação.
