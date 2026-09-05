# Decisões e limites da análise

## Adequação ao contexto profissional

A necessidade delimitada é assegurar o uso correto de uma série pública antes
de sua incorporação a relatórios. É uma aplicação de governança e qualidade de
dados, não uma afirmação sobre as atribuições específicas ou os processos
internos da unidade de Giovanni. Não presumimos sua lotação ou especialidade.

O guia aceita qualidade e cruzamento de dados como técnica principal. A
complexidade de IA generativa não é requisito. A escolha se sustenta em uma
característica verificável da fonte: intervalos históricos explícitos.

## Alternativas consideradas

| Alternativa | Limitação neste trabalho |
| --- | --- |
| RAG e julgamento por LLM | A base escolhida é tabular e as regras são explícitas; avaliação determinística é suficiente. |
| Detecção de anomalias na arrecadação | Exigiria controlar calendário, inflação, mudanças legais, eventos excepcionais e diferenças territoriais; uma anomalia não prova erro ou evasão. |
| Cruzamento de CNPJ e benefícios | Aumenta a escala e a necessidade de regras sobre elegibilidade, identificação e datas; não é necessário ao problema delimitado. |
| Completude temporal | Permite confrontar diretamente metadados oficiais com uma cópia congelada e testar defeitos de forma controlada. Selecionada. |

## Evidência e limites

O catálogo [Resultado da arrecadação](https://dados.gov.br/dados/conjuntos-dados/resultado-da-arrecadacao)
é alcançado pelo [portal da Receita](https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/arrecadacao/arrecadacao).
Sua aplicação web exige JavaScript; CSV e PDF estão acessíveis diretamente no
domínio oficial. Os endereços exatos e hashes estão em `dados/proveniencia.json`.

Regras: páginas 2 e 3 do PDF, nove colunas de três grupos. Os intervalos são
inclusivos e descrevem **publicação**, não vigência jurídica. Não foram
deduzidos das posições vazias. Os meses de 2026 foram excluídos a priori do
recorte de anos completos 2000–2025.

O painel de 8.424 linhas cobre 312 meses × 27 UFs. A auditoria temporal possui
75.816 células, sendo 46.656 aplicáveis e 29.160 vazios previstos. A completude
simples é 61,54%; a condicionada é 100%. Esses valores não demonstram exatidão
da arrecadação, ausência de sonegação ou qualidade global da base.

### Formatos numéricos

A inspeção encontrou convenções numéricas diferentes no mesmo arquivo. Por
exemplo, há valores com múltiplas vírgulas em 2001–2002 e valores com pontos de
milhar em outros períodos. O detector aceita sintaxes estritas das duas
convenções e reporta sua presença no resumo. Existem 3.120 células cujo texto
com separador é compatível com ambas, sem que isso determine seu significado.
Nenhum valor foi convertido para cálculo de arrecadação. Uma análise monetária
futura exige interpretação confirmada e controles adicionais.

### Validação

Treze cenários: original; nulo aplicável; presença fora do intervalo; número
inválido; mês inválido; UF inválida; zero; agrupamento/decimal; negativo;
fronteiras dezembro/2003 e janeiro/2004; duplicação; remoção de registro.
Todas as modificações ocorrem em memória. O teste compara o conjunto exato de
classes de ocorrência esperado e observado.

Os testes verificam defeitos conhecidos, não constituem amostra de erros reais
nem validação independente. Também não provam que a interpretação manual do
dicionário é correta em todos os contextos. Revisões do dicionário podem exigir
novas regras. A passagem dos testes não autoriza decisões automáticas sobre
tributos ou pessoas.

## Referências examinadas

- RFB: CSV e dicionário oficiais (cópias preservadas).
- Wang e Strong (1996), DOI 10.1080/07421222.1996.11518099: qualidade contextual;
  autores, volume 12, número 4 e páginas 5–33 conferidos no registro DOI e artigo.
- GAO (2019), [Assessing Data Reliability](https://www.gao.gov/products/gao-20-283g):
  relação entre confiabilidade e finalidade da auditoria. Orientação técnica
  estrangeira, não norma obrigatória para a Receita.
- W3C (2016), [Data Quality Vocabulary](https://www.w3.org/TR/vocab-dqv/): métricas
  e proveniência. Working Group Note, não certificação de conformidade.

Referências da disciplina diretamente ligadas a IA e grafos não foram
transplantadas automaticamente. O conjunto bibliográfico foi escolhido para
o problema de qualidade, evitando referências sem função argumentativa.
