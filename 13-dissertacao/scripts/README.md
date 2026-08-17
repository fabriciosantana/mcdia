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
  --dias-por-lote 31 \
  --tamanho-lote-textos 250 \
  --trabalhadores 5 \
  --tentativas 10 \
  --backoff 1 \
  --pausa-entre-lotes 2
```

Cada janela é salva em `<diretorio-saida>/lotes/`. Ao executar novamente o
mesmo comando, os lotes existentes são reutilizados. Use `--sobrescrever` para
refazê-los. Consulte todas as opções com:

```bash
python 01_preparar_base_discursos_batch.py --help
```
