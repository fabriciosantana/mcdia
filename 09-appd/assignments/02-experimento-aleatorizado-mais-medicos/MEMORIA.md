# Memória de trabalho — experimento aleatorizado do Programa Mais Médicos

Última atualização: 4 de agosto de 2026.

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
  e tercil de população; região de saúde entra como restrição/covariável.
- Comparação: fluxo regular/lista de espera, sem retirada do cuidado existente.
- Desfecho: média da taxa anual de ICSAP por 10 mil nos dois anos posteriores.
- Estimando primário: ITT da oferta prioritária.
- Estimando secundário: LATE do recebimento para conformes.

## Uso da base anterior

A base da atividade 1 é reutilizada apenas para planejamento. Ela não provém de
um experimento real. Caminho:

`../01-inferencia-causal-mais-medicos/data/processed/mais_medicos_icsap_go.csv`

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
- `MEMORIA.md`: decisões e contexto da atividade;
- a base permanece na atividade 1, sem duplicação.

O gerador temporário foi removido após a criação. O notebook é a fonte
principal e deve ser editado diretamente.

## Estado validado

- notebook com 25 células;
- 8 células de código, todas executadas em sequência;
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
2. confirmar se o MDE de 52 por 10 mil é substantivamente aceitável;
3. corrigir nome completo de “Giovane” quando informado;
4. exportar HTML apenas se necessário para a entrega;
5. ajustar o botão do Colab caso o caminho final mude;
6. versionar a nova pasta após a revisão final.
