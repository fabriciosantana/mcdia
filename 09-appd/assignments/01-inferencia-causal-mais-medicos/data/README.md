# Dados da atividade

O notebook usa diretamente `processed/mais_medicos_icsap_go.csv`, uma base
analítica com uma linha para cada um dos 246 municípios de Goiás.

Ela foi construída por `../preparar_dados_reais.py` a partir de três fontes:

1. Ministério da Saúde, **Programa de Provimento Federal – Programa Mais
   Médicos**, série histórica municipal:
   `https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/MaisMedicos/csv/ppf_mais_medicos_serie_historica.csv.zip`;
2. Secretaria de Estado da Saúde de Goiás, **Internações por Condições
   Sensíveis à Atenção Primária**, derivadas do SIH/DATASUS:
   `https://dadosabertos.go.gov.br/dataset/436edce3-5c43-4c79-8ba4-d9a48e8e1d1c/resource/b9c62bb7-dbd7-492e-a3be-822de01992fd/download/internacoes-icsap.csv`;
3. IBGE/SIDRA, tabela 6579, estimativas populacionais municipais:
   `https://apisidra.ibge.gov.br/values/t/6579/n6/in%20n3%2052/v/9324/p/2013-2015?formato=json`.

Os arquivos brutos somam centenas de megabytes e são ignorados pelo Git. Para
reconstruir a base, baixe-os com os nomes esperados pelo script para
`data/raw/` e execute:

```bash
python 09-appd/assignments/preparar_dados_reais.py
```

Definições:

- tratamento: presença de ao menos um profissional ativo do PMM em
  29/11/2013;
- linha de base: internações de janeiro a outubro de 2013, anualizadas;
- período posterior: média das taxas anuais de 2014 e 2015;
- taxa: internações classificadas como numerador de ICSAP por 10 mil
  habitantes.
