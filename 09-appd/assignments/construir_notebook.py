"""Gera a versão final do notebook com a aplicação empírica."""

from pathlib import Path

import nbformat as nbf


BASE = Path(__file__).resolve().parent
DESTINO = BASE / "atividade_inferencia_causal_mais_medicos.ipynb"
nb = nbf.v4.new_notebook()
cells = []


def md(text: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(text.strip()))


def code(text: str) -> None:
    cells.append(nbf.v4.new_code_cell(text.strip()))


md(
    r"""
**Instituto Brasileiro de Ensino, Desenvolvimento e Pesquisa**

Programa de Pós-Graduação em Administração Pública — Mestrado Profissional

**Disciplina:** Avaliação de Políticas Públicas com Dados  
**Atividade:** Resultados potenciais e critério de backdoor  
**Grupo:** Analécia Borato, Fabricio Santana, Giovane, Paulo Cézar

# Programa Mais Médicos e internações evitáveis em Goiás

Este notebook aplica o quadro de resultados potenciais e o critério de
backdoor a dados administrativos reais. O estudo avalia a entrada inicial do
**Programa Mais Médicos (PMM)** e as internações por condições sensíveis à
atenção primária (**ICSAP**) nos 246 municípios de Goiás.

> **Conclusão em uma frase:** os dados permitem uma ilustração empírica do
> ajuste por backdoor, mas não sustentam, sozinhos, uma afirmação causal forte,
> porque alguns confundidores do DAG são medidos apenas por proxies.
"""
)

md(
    r"""
## 1. Política, pergunta e desenho

O PMM foi instituído em 2013 para ampliar o provimento médico em áreas com
dificuldade de atração e fixação de profissionais. Uma cadeia causal plausível
é:

$$\text{PMM}\rightarrow\text{acesso à atenção básica}
\rightarrow\text{prevenção e manejo precoce}\rightarrow\text{menos ICSAP}.$$

**Pergunta causal:** qual foi o efeito de participar da primeira fase do PMM
sobre a taxa de ICSAP, em 2014–2015, nos municípios goianos que receberam
profissionais até 29 de novembro de 2013?

| Elemento | Definição operacional |
|---|---|
| Unidade | município de Goiás |
| População | 246 municípios existentes no período |
| Tratamento $D_i$ | 1 se havia ao menos um profissional ativo do PMM em 29/11/2013; 0 caso contrário |
| Linha de base | janeiro–outubro de 2013, antes da fotografia do tratamento |
| Resultado $Y_i$ | média da taxa anual de ICSAP por 10 mil habitantes em 2014 e 2015 |
| Estimando | ATT da entrada inicial no programa |

A definição é semelhante a uma análise por atribuição inicial: municípios do
grupo de comparação podem ter ingressado depois. Isso tende a reduzir o
contraste entre os grupos e deve ser lembrado na interpretação.
"""
)

md(
    r"""
## 2. Resultados potenciais e estimando

Para cada município $i$:

$$Y_i(1)=\text{taxa de ICSAP em 2014–2015 sob entrada inicial no PMM},$$

$$Y_i(0)=\text{taxa de ICSAP em 2014–2015 sem entrada inicial no PMM}.$$

Observamos apenas:

$$Y_i=D_iY_i(1)+(1-D_i)Y_i(0).$$

O estimando é:

$$ATT=E[Y(1)-Y(0)\mid D=1].$$

Ele responde à decisão substantiva de interesse: **quanto a taxa de ICSAP dos
municípios inicialmente atendidos teria mudado, em média, se esses mesmos
municípios não tivessem entrado na fase inicial?** O ATT é preferível ao ATE
porque a política selecionou localidades específicas e não há razão para supor
efeitos homogêneos em todos os municípios.
"""
)

md(
    r"""
## 3. DAG e critério de backdoor

O DAG abaixo representa hipóteses causais. Variáveis com sufixo “pré” são
anteriores ao tratamento.
"""
)

code(
    r"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sns.set_theme(style="whitegrid")
RANDOM_SEED = 20260723

def desenhar_dag():
    pos = {
        "V": (0.04, .82), "B": (.04, .54), "G": (.04, .25),
        "D": (.38, .54), "M": (.66, .78), "K": (.66, .25),
        "U": (.38, .05), "Y": (.95, .54)
    }
    labels = {
        "V": "Vulnerabilidade\nprévia",
        "B": "Oferta de APS\ne ICSAP prévias",
        "G": "Capacidade\nadministrativa prévia",
        "D": "Entrada inicial\nno PMM",
        "M": "Acesso/consultas\npós-PMM (mediador)",
        "K": "Gasto em saúde\npós-PMM (colisor)",
        "U": "Choque de saúde\nnão observado",
        "Y": "ICSAP\n2014–2015",
    }
    edges = [
        ("V","D"), ("V","Y"), ("B","D"), ("B","Y"), ("G","D"), ("G","Y"),
        ("D","M"), ("M","Y"), ("D","Y"), ("D","K"), ("U","K"), ("U","Y")
    ]
    colors = {"D":"#2878b5", "Y":"#16836b", "M":"#e6952e", "K":"#cc4c4c"}
    fig, ax = plt.subplots(figsize=(12, 6))
    for a, b in edges:
        ax.annotate("", xy=pos[b], xytext=pos[a],
                    arrowprops={"arrowstyle":"-|>", "lw":1.5, "color":"#555",
                                "shrinkA":28, "shrinkB":28})
    for node, (x, y) in pos.items():
        ax.text(x, y, labels[node], ha="center", va="center", fontsize=9.5,
                color="white" if node in colors else "#222",
                bbox={"boxstyle":"round,pad=.48", "fc":colors.get(node,"#dce8f1"),
                      "ec":"#345"})
    ax.set(xlim=(-.09, 1.08), ylim=(-.08, .95), title="DAG causal proposto")
    ax.axis("off")
    plt.show()

desenhar_dag()
"""
)

md(
    r"""
Os caminhos de backdoor postulados são:

$$D\leftarrow V\rightarrow Y,\qquad
D\leftarrow B\rightarrow Y,\qquad
D\leftarrow G\rightarrow Y.$$

Logo, $Z=\{V,B,G\}$ é um conjunto de ajuste suficiente **no DAG teórico**:
não contém descendentes de $D$ e bloqueia todos os caminhos que entram em $D$
por uma seta. Sob

$$(Y(1),Y(0))\perp D\mid Z,$$

o ATT pode ser identificado por:

$$ATT=E\{E[Y\mid D=1,Z]-E[Y\mid D=0,Z]\mid D=1\}.$$

### O que controlar — e o que não controlar

| Variável | Papel | Controlar para efeito total? | Justificativa |
|---|---|---:|---|
| Vulnerabilidade socioeconômica prévia ($V$) | confundidor | sim | afeta priorização e risco de internação |
| Oferta de APS/ICSAP prévias ($B$) | confundidor | sim | afeta seleção e resultado |
| Capacidade administrativa prévia ($G$) | confundidor | sim | afeta adesão, execução e saúde |
| Acesso/consultas depois do PMM ($M$) | mediador | não | bloquearia parte do efeito total |
| Gasto em saúde posterior ($K$) | colisor plausível | não | condicioná-lo abre $D\to K\leftarrow U\to Y$ |
| Choque de saúde ($U$) | causa do resultado | não no DAG | não causa $D$; associa-se a $D$ se $K$ for condicionado |

O banco empírico mede bem a ICSAP prévia e o porte populacional, mas não contém
medidas completas de $V$, $B$ e $G$. A utilização hospitalar prévia e a região
de saúde são proxies imperfeitas. Por isso, a ignorabilidade condicional é uma
hipótese substantiva forte, não um resultado demonstrado pelos dados.
"""
)

md(
    r"""
## 4. Dados reais e construção das variáveis

As fontes são:

1. **Ministério da Saúde:** série histórica municipal do Programa de
   Provimento Federal/PMM;
2. **SES-GO, com dados do SIH/DATASUS:** internações classificadas conforme a
   lista brasileira de ICSAP;
3. **IBGE/SIDRA (tabela 6579):** estimativas populacionais municipais.

O arquivo analítico tem uma linha por município e acompanha o notebook, de
modo que sua execução não depende da internet. O script
`preparar_dados_reais.py` documenta a transformação dos arquivos brutos.

A linha de base usa janeiro–outubro de 2013 e é anualizada por $12/10$. O
resultado posterior é a média das taxas anuais de 2014 e 2015. A taxa é:

$$\text{taxa de ICSAP}_{it}=
\frac{\text{internações ICSAP}_{it}}{\text{população}_{it}}\times10.000.$$
"""
)

code(
    r"""
def localizar_base():
    candidatos = [
        Path("data/processed/mais_medicos_icsap_go.csv"),
        Path("09-appd/assignments/data/processed/mais_medicos_icsap_go.csv"),
    ]
    for caminho in candidatos:
        if caminho.exists():
            return caminho
    raise FileNotFoundError("Base processada não encontrada.")

df = pd.read_csv(localizar_base(), dtype={"cod_mun": str})
print(f"Municípios: {len(df)}")
print(df["tratado"].value_counts().rename(index={0:"Comparação", 1:"PMM inicial"}))
df.head()
"""
)

md("## 5. Diagnóstico descritivo e suporte comum")

code(
    r"""
variaveis = ["taxa_icsap_pre", "taxa_clinicas_pre", "populacao_2014"]
resumo = df.groupby("tratado")[variaveis].mean().T
resumo.columns = ["Comparação", "PMM inicial"]
resumo["Diferença"] = resumo["PMM inicial"] - resumo["Comparação"]
resumo.round(2)
"""
)

code(
    r"""
fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
sns.boxplot(data=df, x="tratado", y="taxa_icsap_pre", ax=axes[0],
            palette=["#9ecae1", "#2878b5"], hue="tratado", legend=False)
axes[0].set(xlabel="Entrada inicial no PMM", ylabel="ICSAP prévia / 10 mil",
            xticks=[0,1], xticklabels=["Não", "Sim"])
sns.scatterplot(data=df, x="taxa_icsap_pre", y="taxa_icsap_pos",
                hue="tratado", palette={0:"#8c8c8c",1:"#2878b5"}, ax=axes[1])
lim = [0, max(df["taxa_icsap_pre"].max(), df["taxa_icsap_pos"].max())]
axes[1].plot(lim, lim, "--", color="black", lw=1)
axes[1].set(xlabel="ICSAP prévia / 10 mil", ylabel="ICSAP 2014–2015 / 10 mil")
axes[1].legend(title="PMM inicial", labels=["Não", "Sim"])
plt.tight_layout()
plt.show()
"""
)

md(
    r"""
Diferenças na linha de base confirmam que o tratamento não foi aleatório. O
balanceamento descritivo não prova nem refuta identificação; ele apenas mostra
que a comparação bruta não deve ser interpretada automaticamente como causal.

Estimamos a probabilidade de entrada inicial com variáveis **pré-tratamento**:
taxa prévia de ICSAP, taxa prévia de internações clínicas, log da população e
região de saúde. O escore serve como diagnóstico de sobreposição e para
ponderação do grupo de comparação.
"""
)

code(
    r"""
numericas = ["taxa_icsap_pre", "taxa_clinicas_pre", "log_populacao"]
categoricas = ["regiao_saude_residencia"]
X = df[numericas + categoricas]

preprocessador = ColumnTransformer([
    ("num", StandardScaler(), numericas),
    ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), categoricas),
])
modelo_ps = make_pipeline(
    preprocessador,
    LogisticRegression(C=1.0, max_iter=5_000, random_state=RANDOM_SEED),
)
modelo_ps.fit(X, df["tratado"])
df["escore"] = modelo_ps.predict_proba(X)[:, 1]

fig, ax = plt.subplots(figsize=(9, 4))
for d, cor, rotulo in [(0,"#8c8c8c","Comparação"), (1,"#2878b5","PMM inicial")]:
    sns.kdeplot(df.loc[df.tratado.eq(d), "escore"], fill=True, alpha=.35,
                color=cor, label=rotulo, ax=ax, cut=0)
ax.set(xlabel="Probabilidade estimada de entrada inicial", title="Sobreposição dos escores")
ax.legend()
plt.show()

df.groupby("tratado")["escore"].agg(["min","median","max"]).round(3)
"""
)

md(
    r"""
## 6. Estimação do ATT

São mostradas três quantidades:

1. **diferença bruta** entre as taxas posteriores;
2. **diferença em mudanças**, que desconta a taxa prévia;
3. **ATT ponderado**, no qual municípios de comparação recebem peso
   $e(Z)/(1-e(Z))$ e os pesos são normalizados para representar a distribuição
   de $Z$ entre os tratados.

O terceiro estimador implementa o ajuste proposto com as covariáveis
disponíveis, mas só tem interpretação causal se o conjunto observado bloquear
todo confundimento relevante. Intervalos percentis são obtidos por bootstrap
municipal e representam incerteza amostral, não incerteza sobre o DAG.
"""
)

code(
    r"""
def estimativas(data, seed=RANDOM_SEED):
    Xb = data[numericas + categoricas]
    ps = make_pipeline(
        preprocessador,
        LogisticRegression(C=1.0, max_iter=5_000, random_state=seed),
    )
    ps.fit(Xb, data["tratado"])
    e = np.clip(ps.predict_proba(Xb)[:, 1], .01, .99)
    tratados = data["tratado"].eq(1).to_numpy()
    y = data["taxa_icsap_pos"].to_numpy()
    mudanca = data["mudanca_taxa_icsap"].to_numpy()
    pesos_controle = e[~tratados] / (1 - e[~tratados])
    return np.array([
        y[tratados].mean() - y[~tratados].mean(),
        mudanca[tratados].mean() - mudanca[~tratados].mean(),
        y[tratados].mean() - np.average(y[~tratados], weights=pesos_controle),
    ])

nomes = ["Diferença bruta", "Diferença em mudanças", "ATT ponderado"]
ponto = estimativas(df)

rng = np.random.default_rng(RANDOM_SEED)
boots = []
for b in range(500):
    # Reamostragem estratificada preserva tratados e controles em cada réplica.
    partes = []
    for d in [0, 1]:
        grupo = df.loc[df.tratado.eq(d)]
        idx = rng.integers(0, len(grupo), len(grupo))
        partes.append(grupo.iloc[idx])
    amostra = pd.concat(partes, ignore_index=True)
    try:
        boots.append(estimativas(amostra, seed=RANDOM_SEED + b + 1))
    except ValueError:
        continue
boots = np.asarray(boots)

resultado = pd.DataFrame({
    "Estimativa": ponto,
    "IC 2,5%": np.quantile(boots, .025, axis=0),
    "IC 97,5%": np.quantile(boots, .975, axis=0),
}, index=nomes)
resultado.round(2)
"""
)

code(
    r"""
fig, ax = plt.subplots(figsize=(9, 4.5))
ypos = np.arange(len(resultado))
ax.errorbar(resultado["Estimativa"], ypos,
            xerr=[resultado["Estimativa"]-resultado["IC 2,5%"],
                  resultado["IC 97,5%"]-resultado["Estimativa"]],
            fmt="o", color="#2878b5", capsize=4)
ax.axvline(0, color="black", ls="--", lw=1)
ax.set(yticks=ypos, yticklabels=resultado.index,
       xlabel="Diferença na taxa de ICSAP por 10 mil habitantes",
       title="Estimativas observacionais e IC bootstrap de 95%")
ax.invert_yaxis()
plt.tight_layout()
plt.show()
"""
)

md(
    r"""
### Leitura correta dos resultados

- A diferença bruta mistura o possível efeito do programa com seleção dos
  municípios.
- A diferença em mudanças desconta níveis prévios, mas exigiria tendências
  paralelas para uma interpretação causal longitudinal.
- O ATT ponderado compara os tratados a controles reponderados segundo as
  covariáveis observadas. Ele é a principal **ilustração do backdoor**, não uma
  validação de que o backdoor foi inteiramente bloqueado.
- Um intervalo que inclua zero indica imprecisão compatível tanto com redução
  quanto com aumento da taxa. Mesmo que não inclua zero, confundimento residual
  ainda poderia explicar parte da associação.

Em particular, não devemos escrever “o PMM causou uma redução de X” apenas com
esta análise. A formulação defensável é: “a estimativa ajustada foi X, sob as
hipóteses declaradas e com as limitações de mensuração descritas”.
"""
)

md(
    r"""
## 7. Hipóteses e ameaças à validade

- **Consistência:** “entrada inicial” reúne doses e perfis profissionais
  diferentes. O tratamento precisa ser interpretado como a política tal como
  implementada, não como uma dose homogênea.
- **Positividade:** deve haver municípios tratados e não tratados comparáveis
  em cada perfil de covariáveis. A distribuição dos escores deve ser examinada;
  extrapolação para tratados sem controles semelhantes fragiliza o ATT.
- **Ausência de confundimento não observado:** é a hipótese mais fraca da
  aplicação. Vulnerabilidade, oferta prévia de médicos e capacidade
  administrativa não estão integralmente medidas.
- **Não interferência:** pacientes e médicos podem atravessar fronteiras
  municipais, violando SUTVA.
- **Ordenação temporal:** somente variáveis anteriores a 29/11/2013 entram no
  ajuste. Consultas, cobertura e gastos posteriores foram deliberadamente
  excluídos.
- **Adoção posterior:** municípios classificados como comparação podem receber
  o PMM em 2014–2015, reduzindo o contraste.
- **Mensuração:** o SIH cobre internações financiadas pelo SUS; erros de
  residência, codificação diagnóstica e população afetam as taxas.
- **Poucos tratados:** há apenas 29 municípios na coorte inicial em Goiás, o
  que limita precisão e flexibilidade do modelo.
- **Validade externa:** o ATT goiano não se transporta automaticamente para o
  Brasil ou para municípios não tratados.

Uma avaliação de impacto mais forte acrescentaria dados pré-tratamento de
CNES/ESF, vulnerabilidade do Censo/Atlas Brasil e capacidade fiscal e
administrativa; verificaria suporte comum; examinaria a data exata de entrada;
e exploraria um painel com adoção escalonada e tendências prévias.
"""
)

md(
    r"""
## 8. Conclusão

O trabalho definiu o ATT da entrada inicial no Programa Mais Médicos sobre as
ICSAP e explicitou por que a comparação observada não é automaticamente
causal. No DAG, vulnerabilidade, oferta prévia de atenção básica e capacidade
administrativa devem ser controladas porque abrem caminhos de backdoor.
Consultas posteriores não devem ser controladas ao estimar o efeito total,
pois são mediadoras; gasto posterior também não deve ser condicionado quando
funciona como colisor entre o PMM e choques de saúde.

A aplicação com 246 municípios goianos mostra como construir taxas reais,
diagnosticar seleção e estimar uma comparação ponderada. Seu principal
resultado metodológico é também seu principal limite: **identificação causal
depende do DAG e da mensuração adequada dos confundidores, não apenas da
execução de uma regressão ou da disponibilidade de dados administrativos.**
"""
)

md(
    r"""
## Referências e fontes

- BRASIL. Lei nº 12.871, de 22 de outubro de 2013. Institui o Programa Mais
  Médicos.
- BRASIL. Ministério da Saúde. *Programa de Provimento Federal – Programa Mais
  Médicos para o Brasil: série histórica*. Portal de Dados Abertos do SUS.
- BRASIL. Ministério da Saúde. Portaria SAS/MS nº 221, de 17 de abril de 2008.
  Publica a Lista Brasileira de Internações por Condições Sensíveis à Atenção
  Primária.
- GOIÁS. Secretaria de Estado da Saúde. *Internações por Condições Sensíveis à
  Atenção Primária*, dados derivados do SIH/DATASUS.
- IBGE. SIDRA, tabela 6579. *População residente estimada*.
- ANGRIST, J.; PISCHKE, J. *Mastering 'Metrics*. Princeton University Press,
  2015.
- PEARL, J.; MACKENZIE, D. *The Book of Why*. Basic Books, 2018.

Os endereços completos e as instruções de reprodução estão em
`data/README.md`.
"""
)

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {"name": "python", "version": "3"},
}
nbf.write(nb, DESTINO)
print(f"Notebook criado: {DESTINO}")
