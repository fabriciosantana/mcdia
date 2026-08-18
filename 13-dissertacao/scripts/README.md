# Scripts da dissertação

Este diretório é reservado aos scripts Python usados na preparação, validação e análise das bases de dados da dissertação.

Os scripts devem registrar entradas, saídas, parâmetros e versões relevantes. Dados brutos, resultados experimentais e credenciais não devem ser incorporados ao código; seus caminhos e regras de versionamento serão definidos quando cada fluxo for implementado.

## Preparação da base de discursos

O script `01_preparar_base_discursos_batch.py` adapta o notebook original para
execução não interativa, com lotes intermediários retomáveis:

```bash
python -m pip install -r requirements.txt
```

```bash
python 01_preparar_base_discursos_batch.py \
  --data-inicio 2019-02-01 \
  --data-fim 2023-01-31 \
  --diretorio-saida ../dados/ \
  --tamanho-lote-textos 250 \
  --trabalhadores 5 \
  --tentativas 10 \
  --backoff 1 \
  --pausa-entre-lotes 2
```

Cada janela é salva em `<diretorio-saida>/lotes/`. Ao executar novamente o
mesmo comando, os lotes existentes são reutilizados. Use `--sobrescrever` para
refazê-los. Consulte todas as opções com:

O padrão é `--modo-lotes calendario`: cada consulta fica contida em um mês
civil e aproveita corretamente meses de 28, 29, 30 ou 31 dias. Se o período
começar ou terminar no meio do mês, somente o primeiro ou o último lote será
parcial.

O modo alternativo `--modo-lotes dias` usa janelas de tamanho fixo. Nesse caso,
`--dias-por-lote` aceita de 1 a 29 dias; 29 é o padrão conservador, pois a API
rejeita algumas janelas fixas de 30 ou 31 dias que atravessam meses de durações
diferentes.

```bash
python 01_preparar_base_discursos_batch.py \
  --data-inicio 2019-02-01 \
  --data-fim 2019-04-15 \
  --modo-lotes dias \
  --dias-por-lote 15
```

```bash
python 01_preparar_base_discursos_batch.py --help
```
