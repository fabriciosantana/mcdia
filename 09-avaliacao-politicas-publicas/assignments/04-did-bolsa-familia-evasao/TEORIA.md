# Guia teórico e prático — DiD do Bolsa Família sobre evasão escolar

Este texto reúne o que é necessário para compreender, executar, interpretar e
defender a atividade implementada em
`atividade_did_bolsa_familia_evasao.ipynb`. A análise estima o efeito do Bolsa
Família sobre `dropout_med`, a evasão escolar média no domicílio, usando o
painel da AIBF II de 2005 e 2009.

## 1. Pergunta causal e desenho

A pergunta é:

> Entre os domicílios beneficiários em 2009, quanto a evasão escolar média
> mudou entre 2005 e 2009 além da mudança observada entre domicílios inscritos
> no Cadastro Único que não recebiam o Bolsa Família?

Os elementos do desenho são:

| Elemento | Definição |
|---|---|
| Unidade | domicílio (`cod_dtm`) |
| Período pré | 2005 |
| Período pós | 2009 |
| Tratados | `T1`: recebiam Bolsa Família em 2009 |
| Controle principal | `C1`: inscritos no Cadastro Único, mas não beneficiários |
| Placebo | `C1` artificialmente tratado versus `C2`, não inscrito |
| Desfecho | `dropout_med`: evasão média no domicílio |
| Estimando | efeito médio DiD na amostra de domicílios com desfecho nas duas rodadas |

O controle C1 é mais defensável que C2 para a análise principal porque T1 e C1
passaram por um filtro administrativo semelhante. Ainda assim, essa escolha não
torna os grupos automaticamente comparáveis.

### Associação, estimativa DiD e efeito causal

É importante distinguir três afirmações:

1. **Associação:** T1 e C1 apresentam resultados diferentes.
2. **Estimativa DiD:** a mudança observada em T1 difere da mudança em C1.
3. **Efeito causal:** a diferença das mudanças foi causada pelo Bolsa Família.

O banco identifica diretamente as duas primeiras. A terceira depende das
hipóteses de identificação discutidas adiante.

## 2. Por que não comparar apenas os níveis de 2009

Uma comparação transversal pós-tratamento seria:

$$
E[Y_{2009}\mid T1]-E[Y_{2009}\mid C1].
$$

Ela mistura o possível efeito do programa com diferenças que já existiam antes
dele. Famílias beneficiárias e não beneficiárias podem diferir em pobreza,
composição familiar, acesso à escola, localização, expectativas e outros
fatores.

O DiD usa a mudança dentro de cada grupo. Assim, remove:

- diferenças entre grupos que permanecem constantes no tempo; e
- choques temporais que afetam os dois grupos igualmente.

Ele não remove fatores não observados que mudem diferentemente entre T1 e C1.

## 3. O estimador de diferenças em diferenças

No desenho com dois grupos e dois períodos, há quatro médias:

| Grupo | 2005, pré | 2009, pós | Variação |
|---|---:|---:|---:|
| T1 | $\bar Y_{T,pré}$ | $\bar Y_{T,pós}$ | $\Delta_T$ |
| C1 | $\bar Y_{C,pré}$ | $\bar Y_{C,pós}$ | $\Delta_C$ |

em que:

$$
\Delta_T=\bar Y_{T,pós}-\bar Y_{T,pré}
$$

e

$$
\Delta_C=\bar Y_{C,pós}-\bar Y_{C,pré}.
$$

Logo:

$$
\widehat{DiD}=\Delta_T-\Delta_C.
$$

Na atividade:

| Grupo | 2005 | 2009 | Variação |
|---|---:|---:|---:|
| T1 | 0,0232 | 0,0753 | +5,22 p.p. |
| C1 | 0,0295 | 0,0873 | +5,78 p.p. |

Mais precisamente, a variação de T1 foi aproximadamente 5,22 p.p. Portanto:

$$
\widehat{DiD}=5,22-5,78=-0,56\text{ p.p.}
$$

Como evasão é um resultado desfavorável, um coeficiente negativo tem direção
favorável: o aumento da evasão foi menor em T1 do que em C1.

### Pontos percentuais não são porcentagem relativa

Um efeito de `-0,0056` na escala de proporção equivale a **-0,56 ponto
percentual**. Não significa redução de 0,56% no risco relativo. Para converter
uma proporção em pontos percentuais, multiplica-se por 100.

## 4. Hipótese central: tendências paralelas

A interpretação causal exige que, sem o Bolsa Família, T1 tivesse apresentado
a mesma mudança média que C1:

$$
E[Y_{T,pós}(0)-Y_{T,pré}(0)]
=
E[Y_{C,pós}(0)-Y_{C,pré}(0)].
$$

Isso é a hipótese de **tendências paralelas**. Ela não exige níveis iguais em
2005. Os grupos podem começar em patamares distintos; o necessário é que, na
ausência do tratamento, evoluíssem de forma paralela.

A hipótese não pode ser comprovada com os resultados observados porque a
trajetória pós-2005 de T1 sem o programa é contrafactual. Evidências auxiliares
podem aumentar ou reduzir sua plausibilidade:

- trajetórias semelhantes em vários períodos anteriores;
- ausência de efeitos em períodos ou grupos placebo;
- estabilidade a controles pré-tratamento razoáveis;
- ausência de mudanças diferenciais na composição da amostra;
- conhecimento institucional sobre outros eventos ocorridos entre as rodadas.

Nesta base há apenas um período pré. Portanto, não é possível avaliar
visualmente nem testar pré-tendências. Duas linhas ligando 2005 a 2009 mostram a
mudança observada, mas não constituem teste de tendências paralelas.

## 5. Outras hipóteses necessárias

Tendências paralelas não é a única exigência.

### Ausência de antecipação

O comportamento de T1 antes do tratamento não deve ter mudado porque as
famílias previram o recebimento. Antecipação contaminaria a linha de base.

### Não interferência e ausência de transbordamentos

O tratamento de uma família não deveria alterar o desfecho do controle. Por
exemplo, mudanças locais de oferta escolar induzidas pelo programa poderiam
beneficiar também C1 e reduzir o contraste.

### Consistência do tratamento

O indicador T1 deve representar uma intervenção suficientemente bem definida.
Na prática, duração, valor e regularidade do benefício podem variar. O
coeficiente resume essa exposição heterogênea.

### Ausência de choques simultâneos específicos de grupo

Não pode existir outro evento entre 2005 e 2009 que afete T1 de modo diferente
de C1 e seja confundido com o programa, como mudança seletiva na oferta escolar,
choque econômico local ou programa complementar direcionado aos beneficiários.

### Composição comparável e atrito não seletivo

O notebook mantém domicílios com `dropout_med` observado nas duas rodadas. Se a
permanência no painel ou a disponibilidade do desfecho estiver relacionada ao
tratamento e ao resultado, a amostra pode ser seletiva.

## 6. Especificação 1: regressão com interação

A regressão canônica é:

$$
Y_{it}=\alpha+\beta Tratado_i+\gamma Pós_t
+\delta(Tratado_i\times Pós_t)+\varepsilon_{it}.
$$

Cada coeficiente tem interpretação direta:

| Coeficiente | Interpretação |
|---|---|
| $\alpha$ | média de C1 em 2005 |
| $\beta$ | diferença T1 menos C1 em 2005 |
| $\gamma$ | mudança de C1 entre 2005 e 2009 |
| $\delta$ | mudança adicional de T1; estimativa DiD |

No `statsmodels`, a atividade usa:

```python
smf.ols(
    "dropout_med ~ tratamento + pos + tratamento:pos",
    data=dados
).fit(
    cov_type="cluster",
    cov_kwds={"groups": dados["cod_dtm"]}
)
```

Em um desenho 2 × 2 sem covariáveis, o coeficiente da interação coincide
algebricamente com o cálculo manual usando as quatro médias.

## 7. Especificação 2: TWFE

O modelo com efeitos fixos de duas vias é:

$$
Y_{it}=\alpha_i+\gamma_t+\delta D_{it}+\varepsilon_{it},
$$

em que:

- $\alpha_i$ é o efeito fixo do domicílio;
- $\gamma_t$ é o efeito fixo do ano;
- $D_{it}=Tratado_i\times Pós_t$ indica exposição efetiva;
- $\delta$ é o coeficiente de interesse.

Os efeitos fixos domiciliares absorvem todas as características do domicílio
que não mudam no tempo, observadas ou não. Os efeitos fixos de ano absorvem
choques comuns a todos os domicílios.

No `linearmodels`:

```python
painel = dados.set_index(["cod_dtm", "ano"])
modelo = PanelOLS(
    painel["dropout_med"],
    painel[["D"]],
    entity_effects=True,
    time_effects=True
)
resultado = modelo.fit(
    cov_type="clustered",
    cluster_entity=True,
    auto_df=False,
    count_effects=False
)
```

### Por que as duas estimativas coincidem

Com dois grupos, dois períodos, tratamento iniciado no mesmo momento e a mesma
amostra balanceada, regressão com interação e TWFE representam a mesma
comparação causal. Por isso os coeficientes são iguais nesta atividade.

Se os resultados fossem diferentes, os primeiros itens a verificar seriam:

1. valores ausentes tratados de maneiras distintas;
2. painel balanceado em apenas uma especificação;
3. definição incorreta de `D`;
4. duplicatas de domicílio-ano;
5. grupos ou anos diferentes entre as amostras.

### Ajuste de graus de liberdade do `PanelOLS`

Efeitos fixos absorvem muitos parâmetros. Pacotes podem aplicar correções de
pequena amostra diferentes ao erro-padrão. Como a covariância já é agrupada
pela entidade, o notebook usa `auto_df=False, count_effects=False` para não
recontar os efeitos fixos absorvidos no ajuste e tornar a inferência comparável
à regressão canônica. Essa opção altera erro-padrão e valor-p, não o coeficiente.

## 8. Por que agrupar os erros-padrão

Cada domicílio aparece em 2005 e 2009. Os erros das duas observações podem ser
correlacionados por características familiares, escola, bairro e choques
persistentes. O erro-padrão usual da OLS pressupõe independência entre linhas e
pode superestimar a precisão.

Agrupar por `cod_dtm` permite correlação arbitrária dentro do domicílio. A regra
é agrupar no nível em que o tratamento ou a dependência se organiza. Nesta
atividade, o domicílio é simultaneamente a unidade do painel e a unidade de
tratamento disponível.

A clusterização:

- não muda o coeficiente estimado;
- muda erro-padrão, intervalo e valor-p;
- não corrige viés por tendências não paralelas, atrito ou má definição do
  tratamento.

## 9. Painel balanceado, valores ausentes e população-alvo

O notebook prepara separadamente as duas comparações:

```python
d = base[base["grupo"].isin(grupos)].dropna(subset=["dropout_med"])
rodadas = d.groupby("cod_dtm")["ano"].nunique()
completos = rodadas[rodadas == 2].index
d = d[d["cod_dtm"].isin(completos)]
```

O balanceamento tem duas vantagens práticas:

- a variação é calculada para os mesmos domicílios;
- interação e TWFE usam exatamente as mesmas observações.

Por outro lado, muda o estimando: a conclusão passa a valer para domicílios com
evasão média observada nas duas rodadas. Não necessariamente vale para todos os
domicílios originalmente amostrados.

`dropout_med` também depende de quem integra a média domiciliar em cada ano. Os
indivíduos não são ligados entre rodadas; o painel é de domicílios. Assim, parte
da mudança pode refletir alteração da composição das crianças e adolescentes
dentro da casa, não apenas mudança de comportamento das mesmas pessoas.

## 10. Placebo C1 × C2

O placebo repete o desenho entre dois grupos de controle:

- `C1` recebe artificialmente `tratamento=1`;
- `C2` recebe `tratamento=0`;
- `D_placebo=C1\times Pós`.

Como nenhum dos grupos representa beneficiários no contraste, espera-se uma
DiD próxima de zero. Um placebo grande e preciso indicaria que C1 e C2 já
possuem mudanças distintas por razões alheias ao Bolsa Família.

Na atividade:

| Comparação placebo | 2005 | 2009 | Variação |
|---|---:|---:|---:|
| C1, artificialmente tratado | 2,95% | 8,73% | +5,78 p.p. |
| C2, controle | 2,27% | 8,49% | +6,22 p.p. |

Logo:

$$
DiD_{placebo}=5,78-6,22=-0,43\text{ p.p.}
$$

O IC95% da regressão com interação é aproximadamente `[-2,32; 1,45]` p.p. e
o valor-p é `0,652`. Não há mudança diferencial estatisticamente detectável.

### O que o placebo não demonstra

O placebo C1 × C2 examina a evolução relativa de dois controles. Ele não
observa o contrafactual de T1 e, portanto, não prova tendências paralelas entre
T1 e C1. Além disso, C2 pode ser menos comparável a C1 porque não passou pelo
mesmo filtro cadastral. O resultado é um diagnóstico indireto, não um teste
definitivo da hipótese central.

## 11. Resultados completos

| Comparação | Domicílios | DiD | EP-padrão agrupado | IC95% | Valor-p |
|---|---:|---:|---:|---:|---:|
| T1 × C1 | 3.201 | -0,56 p.p. | 1,00 p.p. | [-2,52; 1,39] p.p. | 0,573 |
| C1 × C2 | 4.101 | -0,43 p.p. | 0,96 p.p. | [-2,32; 1,45] p.p. | 0,652 |

As linhas da regressão com interação e do TWFE têm o mesmo coeficiente em cada
comparação. Pequenas diferenças nos últimos dígitos de erro-padrão e valor-p
podem surgir das correções finitas próprias de cada pacote.

### Interprete o intervalo, não apenas o valor-p

Para T1 × C1, o intervalo inclui:

- redução da evasão de até aproximadamente 2,52 p.p.;
- efeito zero;
- aumento de até aproximadamente 1,39 p.p.

Portanto, os dados não permitem distinguir com precisão entre esses cenários.
Um valor-p acima de 0,05 significa que a evidência é insuficiente para rejeitar
efeito zero sob o modelo; não prova que o efeito verdadeiro seja exatamente
zero.

## 12. Interpretação substantiva adequada

Uma formulação cuidadosa é:

> Entre os domicílios observados nas duas rodadas, a evasão média aumentou 0,56
> ponto percentual menos em T1 do que em C1. A direção é compatível com efeito
> protetivo do Bolsa Família, mas o intervalo de confiança é amplo e inclui
> zero. O placebo C1 × C2 também é pequeno e impreciso. Sob tendências
> paralelas e as demais hipóteses do desenho, a estimativa pode ser interpretada
> como efeito causal; empiricamente, a evidência é sugestiva e não conclusiva.

Devem ser evitadas frases como:

- “o Bolsa Família reduziu a evasão em 0,56%” — unidade incorreta e excesso de
  certeza;
- “não houve efeito porque `p>0,05`” — ausência de significância não é prova de
  ausência;
- “o placebo confirmou tendências paralelas” — o placebo não testa T1 × C1;
- “efeitos fixos resolvem todo confundimento” — eles removem apenas fatores
  invariantes no tempo e choques temporais comuns.

## 13. Checklist prático de execução

Antes de estimar:

1. confirmar que os anos são 2005 e 2009;
2. confirmar uma linha por `cod_dtm` e `ano`;
3. verificar que o grupo do domicílio não muda entre rodadas;
4. conferir a codificação de `pos`;
5. criar `tratamento` conforme a comparação;
6. criar `D=tratamento*pos`;
7. tratar ausências e definir explicitamente o painel balanceado;
8. registrar quantos domicílios foram mantidos por grupo.

Durante a estimação:

1. calcular as quatro médias e a DiD manual;
2. estimar a regressão com interação;
3. agrupar erros por domicílio;
4. estimar TWFE na mesma amostra;
5. verificar igualdade dos coeficientes;
6. repetir todo o processo para o placebo.

Depois da estimação:

1. converter o coeficiente para pontos percentuais;
2. apresentar erro-padrão, IC95% e valor-p;
3. interpretar a direção considerando que evasão é indesejável;
4. comparar magnitude principal e placebo;
5. discutir tendências paralelas e ameaças à validade;
6. delimitar a população efetivamente representada pela amostra balanceada.

## 14. Checagens de código importantes

O notebook contém assertivas que funcionam como proteção contra mudanças
silenciosas:

```python
assert set(aibf["ano"].unique()) == {2005, 2009}
assert not aibf.duplicated(["cod_dtm", "ano"]).any()
assert d.groupby("cod_dtm")["ano"].nunique().eq(2).all()
assert d.groupby("cod_dtm")["tratamento"].nunique().eq(1).all()
assert np.isclose(did_manual, coef_interacao)
assert np.isclose(coef_interacao, coef_twfe)
```

Se alguma falhar, não se deve simplesmente removê-la. É preciso verificar
duplicatas, filtros, valores ausentes, codificação do tratamento e indexação do
painel.

## 15. Robustez e extensões possíveis

Sem mudar a atividade principal, análises adicionais úteis seriam:

- comparar painel balanceado e todas as observações disponíveis;
- reportar atrito por grupo e diferenças observáveis entre retidos e excluídos;
- repetir a análise com `grade_now_med`;
- acrescentar covariáveis estritamente pré-tratamento para melhorar precisão,
  sem condicionar em mediadores;
- estimar heterogeneidade previamente justificada, como sexo ou área rural,
  reconhecendo o problema de múltiplos testes;
- usar mais períodos pré-tratamento, caso existam, para visualizar trajetórias;
- aplicar inferência por randomização ou bootstrap por cluster como
  sensibilidade, quando tecnicamente adequado.

Com apenas dois períodos e adoção em um único momento, métodos modernos para
tratamento escalonado não acrescentam identificação. Callaway–Sant'Anna ou
Sun–Abraham seriam relevantes se diferentes unidades começassem a receber o
programa em anos distintos e houvesse vários períodos.

## 16. Roteiro curto para apresentação oral

Uma defesa de dois minutos pode seguir esta ordem:

1. “Usei evasão média domiciliar, diferente da matrícula trabalhada em aula.”
2. “Comparei a mudança de T1 entre 2005 e 2009 com a mudança de C1.”
3. “Mantive domicílios observados nas duas rodadas e agrupei erros por
   domicílio.”
4. “A DiD manual, a interação e o TWFE produziram -0,56 p.p.”
5. “O IC95% inclui zero; a direção é favorável, mas a evidência é imprecisa.”
6. “O placebo C1 × C2 foi -0,43 p.p. e também impreciso.”
7. “O placebo é tranquilizador, mas não prova tendências paralelas; com um só
   período pré, essa hipótese permanece substantiva.”

## 17. Perguntas que você deve saber responder

### Por que C1 é o controle principal?

Porque, diferentemente de C2, estava inscrito no Cadastro Único e passou por
filtro administrativo semelhante ao de T1. Isso aumenta a comparabilidade
institucional, embora não garanta tendências paralelas.

### Por que o sinal negativo é favorável?

Porque o desfecho é evasão. Valor menor significa resultado educacional melhor.

### Por que usar TWFE se há apenas dois períodos?

Para mostrar a formulação de painel com efeitos fixos e confirmar sua
equivalência ao DiD canônico neste desenho. O TWFE torna-se especialmente útil
como notação geral em painéis maiores, embora exija cautela com adoção
escalonada e efeitos heterogêneos.

### Efeitos fixos removem confundidores não observados?

Removem os que são constantes no tempo dentro do domicílio. Não removem
confundidores que mudem ao longo do tempo de modo diferente entre grupos.

### O resultado não significativo prova que o programa não funcionou?

Não. O intervalo é amplo. A análise é compatível com efeito protetivo modesto,
efeito nulo ou pequeno efeito adverso.

### O placebo valida o modelo?

Não sozinho. Ele não detectou divergência entre C1 e C2, mas não observa a
trajetória contrafactual de T1.

### Por que os tamanhos das amostras principal e placebo diferem?

Cada comparação contém pares de grupos diferentes e exige desfecho observado
nas duas rodadas. T1 × C1 possui 3.201 domicílios; C1 × C2 possui 4.101.

## 18. Conclusão

O DiD não compara apenas quem recebeu e quem não recebeu o Bolsa Família. Ele
compara **mudanças** e usa a mudança de C1 como contrafactual para T1. Na
amostra balanceada, o aumento da evasão foi 0,56 p.p. menor entre beneficiários,
mas a incerteza é grande. O placebo foi pequeno e não significativo. A leitura
causal é possível somente sob tendências paralelas e as demais hipóteses do
desenho; por isso, a conclusão deve enfatizar magnitude, intervalo, população
analisada e limitações, não apenas o sinal ou o valor-p.

## Referências

- BERTRAND, M.; DUFLO, E.; MULLAINATHAN, S. How Much Should We Trust
  Differences-in-Differences Estimates? *Quarterly Journal of Economics*,
  2004.
- BRASIL. Ministério do Desenvolvimento Social. *Avaliação de Impacto do
  Programa Bolsa Família — 2ª rodada (AIBF II)*. Brasília: MDS, 2012.
- CUNNINGHAM, S. *Causal Inference: The Mixtape*. Yale University Press, 2021.
- DE BRAUW, A. et al. The Impact of Bolsa Família on Schooling. *World
  Development*, v. 70, p. 303–316, 2015.
- HUNTINGTON-KLEIN, N. *The Effect: An Introduction to Research Design and
  Causality*. CRC Press, 2022.
- ROTH, J. et al. What's Trending in Difference-in-Differences? A Synthesis of
  the Recent Econometrics Literature. *Journal of Econometrics*, 2023.
