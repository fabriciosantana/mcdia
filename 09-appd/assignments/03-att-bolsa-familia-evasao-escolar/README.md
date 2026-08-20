# Atividade 03 - ATT do Bolsa Familia sobre evasao escolar

Esta pasta e uma entrega autocontida da atividade de pareamento e escore de
propensao. O arquivo principal e
`atividade_att_bolsa_familia_evasao_escolar.ipynb`, entregue com todas as
celulas executadas e suas saidas.

## Conteudo

- `atividade_att_bolsa_familia_evasao_escolar.ipynb`: analise e conclusoes;
- `atividade_att_bolsa_familia_evasao_escolar.html`: versao pronta para leitura;
- `data/aibf_ii_educacao.csv`: extrato local da AIBF II usado pelo notebook;
- `data/DICIONARIO.md`: definicoes das variaveis efetivamente utilizadas;
- `MEMORIA.md`: resumo das decisoes, resultados e verificacoes.

## Reproducao

A avaliacao nao depende de download nem de arquivo fora desta pasta. A partir
do diretorio da atividade, execute:

```bash
jupyter nbconvert --to notebook --execute \
  atividade_att_bolsa_familia_evasao_escolar.ipynb \
  --output atividade_att_bolsa_familia_evasao_escolar.ipynb \
  --ExecutePreprocessor.timeout=600
```

O notebook, a versao HTML e a base local bastam para a avaliacao. Nenhum arquivo
de outro diretorio ou download externo e necessario.
