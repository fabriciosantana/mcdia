# Memoria da atividade 04

## Entrega

O notebook estima o efeito do Bolsa Familia sobre `dropout_med`, desfecho de
painel diferente de `attend_med`, desenvolvido como exemplo principal na aula.
Ele compara T1 com C1 e repete o desenho como placebo entre C1 e C2.

## Decisoes do desenho

- unidade: domicilio;
- periodos: 2005 (pre) e 2009 (pos);
- amostra: casos com `dropout_med` observado e domicilio presente nas duas
  rodadas, definida separadamente para cada comparacao;
- principal: T1 tratado versus C1 controle;
- placebo: C1 artificialmente tratado versus C2 controle;
- especificacoes: regressao com `tratamento x pos` e TWFE com efeitos fixos de
  domicilio e ano;
- inferencia: erros-padrao agrupados por domicilio;
- escala: coeficientes tambem apresentados em pontos percentuais.

Usar a mesma amostra balanceada em ambas as especificacoes faz os coeficientes
da interacao e do TWFE coincidirem no desenho 2 x 2. No `PanelOLS`, a correcao
de graus de liberdade foi configurada para nao recontar efeitos fixos absorvidos
quando a covariancia ja e agrupada por entidade.

## Resultados centrais

| Comparacao | Domicilios | DiD | EP agrupado | IC95% | p-valor |
|---|---:|---:|---:|---:|---:|
| T1 x C1 | 3.201 | -0,56 p.p. | 1,00 p.p. | [-2,52; 1,39] p.p. | 0,573 |
| C1 x C2 (placebo) | 4.101 | -0,43 p.p. | 0,96 p.p. | [-2,32; 1,45] p.p. | 0,652 |

O aumento da evasao foi 0,56 ponto percentual menor em T1 do que em C1. O
sinal e compativel com efeito educacional favoravel, mas o intervalo inclui
zero e efeitos de ambos os sinais. O placebo e pequeno e impreciso, sem
evidencia de trajetoria diferencial detectavel entre C1 e C2.

## Interpretacao defensavel

O placebo e tranquilizador, mas nao prova tendencias paralelas entre T1 e C1.
Com apenas um periodo anterior, pre-tendencias nao podem ser examinadas. Uma
leitura causal ainda requer ausencia de antecipacao, transbordamentos, choques
simultaneos especificos de grupo e atrito seletivo. A conclusao correta e de
evidencia sugestiva, mas nao conclusiva, de menor evasao.

## Arquivos

- `atividade_did_bolsa_familia_evasao.ipynb`: fonte executavel;
- `atividade_did_bolsa_familia_evasao.html`: versao renderizada;
- `build_notebook.py`: gerador reproduzivel do notebook;
- `TEORIA.md`: guia teorico, pratico e roteiro de defesa da atividade;
- dados: reutilizados de `examples/04-diferencas-em-diferencas/data/`.
