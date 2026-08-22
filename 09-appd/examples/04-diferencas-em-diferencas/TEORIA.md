# Diferenças em diferenças: conceito e implementação no `DiD.ipynb`

## Conceito de diferenças em diferenças

O método de **diferenças em diferenças** — DiD, do inglês *difference-in-differences* — estima o efeito de uma política comparando a evolução de um grupo tratado com a evolução de um grupo de controle.

A ideia não é simplesmente perguntar se, depois da política, os tratados apresentam resultados melhores que os controles. Essa comparação poderia refletir diferenças preexistentes entre os grupos. O DiD pergunta:

> Quanto o resultado mudou entre antes e depois para os tratados, em comparação com a mudança observada nos controles?

No caso canônico, há dois grupos e dois períodos:

| Grupo | Antes | Depois | Variação |
|---|---:|---:|---:|
| Tratado | $\bar Y_{T,pré}$ | $\bar Y_{T,pós}$ | $\bar Y_{T,pós}-\bar Y_{T,pré}$ |
| Controle | $\bar Y_{C,pré}$ | $\bar Y_{C,pós}$ | $\bar Y_{C,pós}-\bar Y_{C,pré}$ |

O estimador é:

$$
\widehat{DiD}
=
(\bar Y_{T,pós}-\bar Y_{T,pré})
-
(\bar Y_{C,pós}-\bar Y_{C,pré})
$$

A primeira diferença remove características permanentes de cada grupo. A segunda desconta mudanças temporais comuns aos dois grupos. O que sobra é interpretado como efeito do tratamento.

## Hipótese de tendências paralelas

A interpretação causal depende da hipótese de que, **na ausência da política**, tratados e controles teriam apresentado a mesma evolução média:

$$
E[Y_T(0)_{pós}-Y_T(0)_{pré}]
=
E[Y_C(0)_{pós}-Y_C(0)_{pré}]
$$

Isso não exige que os grupos tenham o mesmo nível inicial. Eles podem começar diferentes; o necessário é que seus resultados seguissem trajetórias paralelas sem o tratamento.

Essa hipótese não pode ser testada diretamente, pois envolve o resultado contrafactual dos tratados. Pode-se apenas reunir evidências favoráveis por meio de:

- tendências observadas antes do tratamento;
- testes placebo;
- controles comparáveis;
- análises de sensibilidade;
- verificação de mudanças na composição da amostra.

O DiD deixa de ser convincente quando ocorre, por exemplo, um choque específico no grupo tratado simultaneamente à política, antecipação do tratamento, transbordamentos para o controle ou atrito seletivo no painel.

## Aplicação no notebook

O notebook `DiD.ipynb` utiliza o painel domiciliar da AIBF II, com observações de 2005 e 2009. Cada linha corresponde a um domicílio em uma rodada.

A comparação principal é:

- `T1`: domicílios beneficiários do Bolsa Família em 2009;
- `C1`: domicílios inscritos no CadÚnico, mas não beneficiários.

O grupo `C1` é escolhido como controle principal porque passou por um filtro administrativo semelhante ao dos beneficiários. O grupo `C2`, não inscrito no CadÚnico, é posteriormente utilizado em um placebo.

As variáveis fundamentais são:

- `cod_dtm`: identificador do domicílio;
- `tratado`: indicador de pertencimento ao grupo `T1`;
- `pos`: indicador do ano de 2009;
- `attend_med`: matrícula média das crianças;
- `dropout_med`: evasão média;
- `grade_now_med`: série escolar média.

### Cálculo manual

Para a matrícula escolar, o notebook encontra:

| Grupo | 2005 | 2009 | Variação |
|---|---:|---:|---:|
| Tratado (`T1`) | 0,9339 | 0,8965 | −0,0374 |
| Controle (`C1`) | 0,9209 | 0,8747 | −0,0462 |

Portanto:

$$
\widehat{DiD}
=
(-0{,}0374)-(-0{,}0462)
=
0{,}0088
$$

A matrícula caiu nos dois grupos, possivelmente porque as crianças do painel envelheceram. Entretanto, caiu aproximadamente **0,9 ponto percentual menos** entre os beneficiários.

Esse resultado é diferente da comparação simples de 2009, que seria:

$$
0{,}8965-0{,}8747=0{,}0218
$$

A diferença simples é de 2,18 pontos percentuais, mas parte dela já existia em 2005. O DiD desconta essa diferença inicial e estima 0,88 ponto percentual.

No código, a função `tabela_2x2` agrupa os dados por período e tratamento, calcula as quatro médias e executa as duas subtrações.

## Implementação por regressão

O mesmo estimador é obtido pela regressão:

$$
Y_{it}
=
\alpha
+\beta Tratado_i
+\gamma Pós_t
+\delta(Tratado_i\times Pós_t)
+\varepsilon_{it}
$$

A interpretação dos coeficientes é:

- $\alpha$: média do controle antes da política;
- $\beta$: diferença inicial entre tratados e controles;
- $\gamma$: mudança temporal do grupo de controle;
- $\delta$: diferença adicional ocorrida no grupo tratado, isto é, o DiD.

O notebook implementa isso com:

```python
formula = f"{outcome} ~ tratado + pos + tratado:pos"
```

Para `attend_med`, os resultados são:

- intercepto: 0,9209;
- diferença inicial dos tratados: 0,0130;
- variação temporal do controle: −0,0462;
- interação `tratado:pos`: 0,0089.

A pequena diferença entre 0,0088 no cálculo manual e 0,0089 na regressão decorre do arredondamento prévio das médias na função `tabela_2x2`.

## Resultados dos três desfechos

| Desfecho | DiD | Erro-padrão | Valor-p | Interpretação |
|---|---:|---:|---:|---|
| Matrícula | +0,0089 | 0,0107 | 0,407 | queda menor entre tratados |
| Evasão | −0,0080 | 0,0094 | 0,393 | aumento menor entre tratados |
| Série atual | +0,1527 | 0,1038 | 0,141 | progressão maior entre tratados |

Os três coeficientes apresentam sinais compatíveis com um efeito educacional favorável. Contudo, nenhum é estatisticamente significativo nos níveis convencionais.

Assim, a conclusão adequada é que as estimativas são positivas na direção esperada, mas imprecisas. Não se deve interpretar um valor-p elevado como prova de efeito exatamente igual a zero.

## Erros-padrão clusterizados

Como o mesmo domicílio aparece em mais de um período, suas observações não são independentes. O notebook usa:

```python
.fit(
    cov_type="cluster",
    cov_kwds={"groups": d["cod_dtm"].values}
)
```

Isso permite correlação arbitrária dos erros dentro de cada domicílio. Para matrícula, o erro-padrão da interação passa de 0,0102, no cálculo ingênuo, para 0,0107 quando clusterizado.

A clusterização não altera o coeficiente estimado; altera a avaliação de sua incerteza.

## Generalização com efeitos fixos de duas vias

O notebook apresenta também o modelo TWFE (*two-way fixed effects*):

$$
Y_{it}=\alpha_i+\gamma_t+\delta D_{it}+\varepsilon_{it}
$$

Nesse modelo:

- $\alpha_i$ controla todas as características do domicílio constantes no tempo;
- $\gamma_t$ controla choques comuns a cada período;
- $D_{it}$ indica quando o domicílio está efetivamente tratado.

Depois de restringir a amostra a 3.419 domicílios com observações completas em 2005 e 2009, o `PanelOLS` estima:

$$
\hat\delta=0{,}0083
$$

O valor é próximo dos 0,0089 da regressão anterior. A diferença resulta da utilização de uma amostra balanceada e do tratamento dos valores ausentes.

## Placebo

O notebook compara `C1` com `C2`, dois grupos de controle, atribuindo artificialmente a `C1` a condição de “tratado”. O resultado para matrícula é:

$$
DiD_{placebo}=-0{,}0010,\qquad p=0{,}924
$$

O valor próximo de zero é uma evidência favorável: o procedimento não identifica uma mudança diferencial relevante entre os dois controles. Ainda assim, o placebo não prova tendências paralelas entre `T1` e `C1`; funciona apenas como diagnóstico indireto.

## Tratamento escalonado e métodos modernos

O notebook alerta que o TWFE pode falhar quando diferentes grupos começam o tratamento em momentos distintos e os efeitos variam entre grupos ou ao longo do tempo. Nessa situação, unidades já tratadas podem ser indevidamente usadas como controles para unidades tratadas mais tarde.

Na simulação apresentada:

- ATT verdadeiro: 2,90;
- TWFE: 3,57;
- Callaway–Sant’Anna: 2,95.

O estimador de Callaway–Sant’Anna calcula efeitos por coorte e período, usando grupos nunca tratados ou ainda não tratados como controles. Para a AIBF, que possui somente dois períodos e um único momento de tratamento, ele praticamente coincide com o DiD tradicional:

- Callaway–Sant’Anna: 0,0083;
- TWFE: 0,0083;
- regressão DiD: 0,0089.

## Síntese

O DiD estima o efeito do Bolsa Família comparando mudanças, não apenas níveis. A aplicação sugere efeitos educacionais modestos na direção esperada, mas com incerteza suficiente para impedir uma conclusão estatística firme.

Para sustentar uma interpretação causal, é essencial que as tendências paralelas sejam plausíveis, que os erros-padrão respeitem a dependência dentro dos domicílios e que não existam choques específicos, antecipação, transbordamentos ou mudanças seletivas na composição dos grupos.
