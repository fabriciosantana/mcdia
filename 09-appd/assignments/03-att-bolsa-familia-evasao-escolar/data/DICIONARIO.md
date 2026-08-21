# Dicionario minimo da base AIBF II

O arquivo `aibf_ii_educacao.csv` contem o extrato desidentificado usado na aula.
A analise utiliza somente as colunas abaixo.

| Coluna | Definicao e uso |
|---|---|
| `cod_dtm` | Identificador desidentificado do domicilio; usado para definir o tratamento domiciliar. |
| `estrato_amostral` | Grupo do desenho: `beneficiario`, `controle` C1 ou ausente para observacoes fora do recorte. |
| `s02a10` | Indicador de titularidade do cartao do Bolsa Familia: 1 sim, 2 nao. |
| `dropout` | Evasao: 1 abandonou, 0 permaneceu; definido para quem estudava no ano anterior. |
| `s02af` | Idade em anos. |
| `s02ad` | Sexo: o notebook recodifica o valor 2 como `feminino=1`. |
| `educ_chefe` | Escolaridade do chefe do domicilio, conforme construcao do extrato da aula. |
| `n_moradores` | Numero de moradores do domicilio. |
| `n_comodos` | Numero de comodos. |
| `n_dormitorios` | Numero de dormitorios. |
| `agua_canalizada` | Acesso a agua canalizada: 1 sim; o notebook recodifica os demais valores como 0. |

## Variaveis construidas

- `D`: 1 se ao menos uma pessoa do domicilio possui `s02a10=1`;
- `Y`: copia de `dropout` na amostra analitica;
- `feminino`: 1 quando `s02ad=2`;
- `agua`: 1 quando `agua_canalizada=1`;
- `ps_logit` e `ps_rf`: escores out-of-fold estimados no notebook.

O recorte inclui somente `beneficiario` e `controle`, idades de 6 a 17 anos,
desfecho observado e casos completos nas sete covariaveis de ajuste.
