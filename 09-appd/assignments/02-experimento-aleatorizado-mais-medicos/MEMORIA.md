# Memória de trabalho — experimento aleatorizado do Programa Mais Médicos

Última atualização: 7 de agosto de 2026.

## Objetivo

Planejar um experimento aleatorizado para uma intervenção de política pública,
justificando o desenho, calculando tamanho amostral para um MDE, antecipando
não-conformidade com ITT e LATE e discutindo ética e validade externa.

## Decisão substantiva

- Política: Programa Mais Médicos.
- Intervenção: oferta prioritária de vagas, apoio à adesão e início do
  provimento em uma expansão com capacidade limitada.
- População de planejamento: 246 municípios de Goiás.
- Randomização: clusters municipais, 1:1, bloqueada por quartil de ICSAP prévia
  e tercil de população.
- Região de saúde: não restringe o sorteio; entra apenas como covariável
  categórica pré-especificada na análise.
- Comparação: fluxo regular/lista de espera, sem retirada do cuidado existente.
- Desfecho: média da taxa anual de ICSAP por 10 mil nos dois anos posteriores.
- Estimando primário: ITT da oferta prioritária.
- Estimando secundário: LATE do recebimento para conformes.
- Recebimento `D=1`: adesão ao pacote, pelo menos 80% das vagas prioritárias
  preenchidas — respeitado o mínimo de um profissional — em até 90 dias e
  manutenção desse patamar por ao menos 12 dos primeiros 18 meses.

## Uso da base anterior

A base da atividade 1 é reutilizada apenas para planejamento. Ela não provém de
um experimento real. Para execução autônoma do notebook, há uma cópia local em:

`data/processed/mais_medicos_icsap_go.csv`

Essa cópia é idêntica à base processada da atividade 1. Ambas tinham, na última
verificação, SHA-256:

`0166335fe214af70855ecaa51392064d0115d96b6b340a2fac1b2c7e59fdcd87`

A proveniência, os arquivos brutos e o script de reconstrução permanecem na
atividade 1. Se a base original for atualizada, copiar novamente o arquivo e
registrar o novo hash para evitar divergência silenciosa.

Parâmetros históricos:

- média posterior: `362,055` por 10 mil;
- desvio-padrão bruto: `248,067`;
- correlação pré–pós: `0,820`;
- R² da taxa prévia: `0,672`;
- desvio-padrão residual da ANCOVA simples: `142,281`.

## Poder e amostra

- alfa bilateral: 5%;
- poder: 80%;
- alocação: 1:1;
- MDE-alvo: 52 por 10 mil, cerca de 14,4% da média histórica;
- necessários sem perda: 236 clusters;
- necessários com 5% de perda: aproximadamente 249;
- disponíveis: 246;
- decisão: convidar todos, 123 por braço;
- com 5% de perda, efetivos ≈234 e MDE alcançável ≈52,1.

Justificativa substantiva: em município com 20 mil habitantes, redução de 52
por 10 mil equivale a cerca de 104 internações evitadas ao ano e 208 em dois
anos, se sustentada. A magnitude pode reduzir ocupação de leitos, deslocamentos
e despesas hospitalares o suficiente para justificar recrutamento e retenção.
Uma avaliação econômica real ainda precisaria comparar custos do pacote e das
internações. O MDE é limite de detecção do desenho, não limite de relevância.

O cálculo é municipal; não usa design effect. Se o desfecho mudar para nível
individual, será necessário ICC e tamanho médio do cluster.

## Não-conformidade

- tratamento: recusa, atraso, vaga não preenchida ou baixa retenção;
- controle: entrada por outro ciclo, reposição, emergência ou decisão judicial;
- não fazer análise per protocol como principal;
- ITT preserva a designação;
- primeiro estágio: diferença de recebimento por designação;
- LATE = ITT / primeiro estágio sob relevância, independência, exclusão e
  monotonicidade;
- LATE vale para conformes, não para todos os municípios.

## Ética e validade externa

O sorteio deve ordenar escassez real, não retirar profissionais existentes.
Usar lista de espera, manter cuidado padrão, proteger emergências, documentar
exceções e oferecer expansão posterior se possível. Generalização é limitada a
municípios elegíveis/participantes e depende do ciclo, escala, adesão e
spillovers.

## Arquivos

- `atividade_experimento_aleatorizado_mais_medicos.ipynb`: documento principal;
- `../TEORIA.md`: guia integrado de estudo das atividades 1 e 2; a Parte II
  cobre randomização por clusters, MDE/poder, ANCOVA, ITT/LATE,
  não-conformidade, ética e validade;
- `MEMORIA.md`: decisões e contexto da atividade;
- `data/processed/mais_medicos_icsap_go.csv`: cópia local da base processada da
  atividade 1, mantida para execução autônoma.

O gerador temporário foi removido após a criação. O notebook é a fonte
principal e deve ser editado diretamente.

## Estado validado

- notebook com 29 células;
- 9 células de código, todas executadas em sequência;
- nenhuma saída de erro;
- alocação ilustrativa: 123 municípios por braço;
- diferenças padronizadas no sorteio ilustrativo:
  - ICSAP prévia: `-0,068`;
  - internações clínicas prévias: `-0,058`;
  - log da população: `0,020`;
- tabela de planejamento confirma 236 clusters sem perda, 249 com inflação de
  5%, 246 disponíveis e MDE alcançável de aproximadamente `52,12` com 234
  clusters efetivos.

## Próximos passos

1. revisar a formulação da intervenção com o grupo/professor;
2. corrigir nome completo de “Giovane” quando informado;
3. exportar HTML apenas se necessário para a entrega;
4. ajustar o botão do Colab caso o caminho final mude;
5. versionar a nova pasta após a revisão final.
