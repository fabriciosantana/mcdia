# Trabalho de Giovanni Brígido — minuta técnica para revisão do autor

Tema: **Auditoria da completude temporal dos dados abertos de arrecadação federal por UF com Python**.

O objetivo é verificar qualidade da publicação, considerando mudanças históricas
nas colunas. Não é fiscalização de contribuintes nem estudo de evasão fiscal.
A técnica de qualidade e cruzamento de dados está prevista no enunciado da
disciplina. Este projeto é independente do trabalho sobre discursos do Senado.

## Decisão metodológica

Escolheu-se a base oficial [Arrecadação por estado](https://www.gov.br/receitafederal/dados/arrecadacao-estado.csv/view),
acessível a partir do portal de dados abertos da Receita. O dicionário identifica
intervalos de publicação que tornam inadequada a interpretação de todos os
campos vazios como defeitos. Isso permite um experimento delimitado, verificável
e sem inferência sobre a conduta de pessoas ou empresas.

O recorte é 2000–2025; a completude temporal cobre nove colunas de Cofins,
PIS/Pasep e CSLL. As outras 33 colunas monetárias são submetidas apenas a
checagem lexical. A mudança de categorias de 2004 não é tratada como criação
ou extinção de tributo. Não há soma de colunas ou imputação de zero.

Não são necessários OpenAI, embeddings, LLM como juiz, Hugging Face, chaves de
API ou `.env`. A avaliação usa regras documentadas e defeitos introduzidos em
cópias. O notebook explica e executa o procedimento.

## Artefatos

- `Guia e Orientações do Trabalho Final.pdf`: cópia do enunciado da disciplina.
- `main.tex`, `referencias.bib`, `latexmkrc`: short paper LaTeX, referências ABNT,
  citações azuis; o e-mail permanece explicitamente pendente.
- `revisao/minuta_giovanni_brigido.pdf`: PDF de cinco páginas para revisão.
- `analise_arrecadacao.ipynb`: notebook executável e comentado.
- `scripts/baixar_dados.py`: aquisição e validação de hashes.
- `scripts/analisar_qualidade.py`: análise reproduzível e figura.
- `scripts/validar_controles.py`: 13 cenários de validação em cópias.
- `scripts/verificar_entrega.py`: conferência de resultados e bibliografia.
- `config/regras_temporais.json`: intervalos transcritos do dicionário.
- `dados/brutos/`: CSV e dicionário oficiais congelados; sem dados individuais.
- `dados/proveniencia.json`: URLs, datas e hashes dos dois arquivos.
- `resultados/`: resumo, classificação célula a célula, ocorrências e testes.
- `figuras/`: comparação das medidas de completude.
- `NOTA_METODOLOGICA.md`: justificativa e riscos de interpretação.
- `REVISAO_AUTOR.md`: leitura orientada, informações pendentes e rubrica.

## Reprodução

```bash
cd 10-adap/assignments/final-giovanni
python -m pip install -r requirements.txt
python scripts/baixar_dados.py
python scripts/analisar_qualidade.py
python scripts/validar_controles.py
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
python scripts/verificar_entrega.py
```

O primeiro script reutiliza e verifica a cópia congelada. Se um hash divergir,
ele interrompe a execução. Novas versões devem ser adquiridas em pasta separada,
sem sobrescrever a evidência desta análise. Os dados baixados e as regras
foram preservados para reprodução mesmo que os endereços públicos mudem.
O ambiente efetivamente executado está em `resultados/ambiente.json`.

Para executar o notebook: `jupyter nbconvert --to notebook --execute --inplace
analise_arrecadacao.ipynb --ExecutePreprocessor.timeout=300`.

## Estado

Minuta preparada com pesquisa, execução e verificação técnica. A submissão
depende do e-mail e da revisão de Giovanni, conforme o caráter individual do
enunciado. O documento não afirma que ele realizou atividades institucionais,
que as regras foram homologadas pela Receita ou que houve validação externa.
