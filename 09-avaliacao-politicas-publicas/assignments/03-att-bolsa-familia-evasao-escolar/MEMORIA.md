# Memoria da atividade 03

## Entrega

O notebook estima o ATT do Bolsa Familia sobre evasao escolar na AIBF II. Ele
foi executado integralmente, sem erros, e usa apenas a base presente em `data/`.
A versao HTML preserva texto, tabelas e figuras para leitura sem Jupyter.

## Decisoes do desenho

- desfecho: `dropout`, igual a 1 para abandono escolar;
- unidade: pessoa de 6 a 17 anos;
- tratamento: domicilio com ao menos um titular do cartao do Bolsa Familia;
- comparacao: apenas controle cadastrado C1;
- estimando: ATT dos beneficiarios com desfecho, casos completos e suporte;
- ajuste: idade, sexo, escolaridade do chefe, moradores, comodos, dormitorios e
  agua canalizada;
- escores: logistica e random forest calibrado, ambos out-of-fold;
- metodos: pareamento 1:1 com reposicao e IPW de Hajek para ATT;
- inferencia: erro-padrao sandwich aproximado, agrupado por domicilio e
  condicional ao escore estimado.

## Resultados centrais

A amostra final tem 8.484 pessoas: 6.054 beneficiarias e 2.430 controles C1.
A diferenca bruta e `-0,97` ponto percentual.

| Escore | Metodo | ATT | IC95% aproximado |
|---|---|---:|---:|
| Logistica | pareamento | -1,55 p.p. | [-3,53; 0,43] |
| Logistica | IPW-ATT | -1,11 p.p. | [-2,62; 0,41] |
| Random forest calibrado | pareamento | -2,33 p.p. | [-4,37; -0,29] |
| Random forest calibrado | IPW-ATT | -1,11 p.p. | [-2,58; 0,35] |

A especificacao principal e logistica + IPW: tem ATT estavel, todas as SMDs
abaixo de 0,1 e ESS de controles maior que o pareamento. O intervalo inclui
zero; a evidencia e compativel com reducao, mas imprecisa.

## Balanceamento

- antes: quatro de sete covariaveis com `|SMD| >= 0,1`;
- logistica + pareamento: maximo `|SMD|=0,035`;
- logistica + IPW: maximo `|SMD|=0,041`;
- random forest + pareamento: maximo `|SMD|=0,035`;
- random forest + IPW: maximo `|SMD|=0,108`, em agua canalizada.

O random forest tem AUC ligeiramente maior, mas nao produz o melhor
balanceamento por IPW. Isso ilustra que previsao de tratamento e qualidade do
ajuste causal sao objetivos diferentes.

## Limites a enfatizar

O resultado somente admite leitura causal sob ignorabilidade, positividade,
consistencia e nao interferencia. SMD e love plot nao avaliam confundidores nao
medidos. `dropout` existe apenas para quem estudava no ano anterior, o que
restringe a populacao e pode introduzir selecao. A medida de tratamento nao
captura duracao nem intensidade do beneficio. Os intervalos agrupam domicilios,
mas nao incorporam a reestimacao dos escores.

## Validacao final esperada

- todas as celulas de codigo executadas;
- nenhuma saida do tipo `error`;
- duas figuras de suporte/calibracao e um love plot com dois paineis;
- base, dicionario, notebook, HTML e memoria na mesma pasta;
- `TEORIA.md` atualizado com uma Parte III e roteiro de defesa.
