# Vozes do Senado — storytelling com dados

Dashboard interativo da 56ª legislatura, em português, com dados reais do corpus de [Fabricio Fernandes Santana](https://huggingface.co/datasets/fabriciosantana/discursos-senado-legislatura-56), derivado dos dados abertos do Senado Federal. Segunda versão funcional (2.0.0): HTML, CSS e JavaScript, com preparação reproduzível em Python.

## Como visualizar

No terminal, a partir da raiz deste repositório:

```bash
python3 -m http.server 8000 --bind 0.0.0.0 --directory exercicios/04-storytelling-discursos
```

Abra **http://localhost:8000** no navegador. Em Codespaces/VS Code remoto, abra **Portas / Ports**, encaminhe a porta **8000** e selecione **Abrir no navegador**. Mantenha o terminal aberto; `Ctrl+C` encerra o servidor. Se a porta estiver ocupada, troque `8000` por `8001` no comando e no endereço.

Não abra `index.html` por duplo clique: o navegador precisa de HTTP para carregar o módulo JavaScript e o JSON. Para visualizar, basta Python 3 e um navegador moderno. **Não é necessário instalar pacotes, obter token do Hugging Face ou ter internet após baixar este diretório completo, incluindo `data/details/`.** Os links de fonte original exigem internet. O servidor acima serve somente este exercício; não o diretório inteiro do repositório.

## O que foi construído

- Narrativa em quatro partes: ritmo temporal, distribuição da palavra, assuntos exploratórios e consulta aos registros.
- Filtros combináveis de mês inicial/final, tipo de uso da palavra, partido na data, UF, orador, tema e busca por expressão em resumo/indexação.
- Indicadores e títulos calculados para o recorte ativo; contagem e percentual na série mensal.
- Barras selecionáveis por mouse ou teclado, tabelas acessíveis para meses e oradores, dicionário temático exposto, estados vazio/erro e layout responsivo.
- Resumos completos disponíveis no corpus, paginação de oito registros, ordenação por data e links para os pronunciamentos oficiais.
- Download CSV UTF-8 com BOM, separado por ponto e vírgula, contendo **todos** os registros filtrados, não só a página visível. Importar como UTF-8 / delimitador `;` se necessário. Fórmulas potenciais são neutralizadas.
- Snapshot local com 12.414 registros elegíveis, manifesto e hashes; sem bibliotecas, fontes ou gráficos carregados de CDN.

## Melhorias da versão 2

1. **Comparação A/B:** dois intervalos independentes do período principal, botão para os mesmos meses no ano seguinte, contagens, média mensal, variação absoluta/relativa e tabelas de temas/oradores. Avisos para durações diferentes, meses do ano diferentes, sobreposição e janeiro de 2023.
2. **Evolução temática:** série mensal de percentual com denominador próprio por mês, escala de 0–100%, lacunas quando não há base, tabela e seleção de ponto para abrir os registros.
3. **Anotações:** pico, concentração e ausências recalculados com os filtros; contexto da primeira votação remota em 20/03/2020 com fonte do Senado e sem afirmação causal.
4. **Auditoria dos temas:** palavras acionadoras e campo de origem em cada registro; amostra fixa de 60 pares; leitura assistida por IA com justificativas; formulário de revisão humana com persistência local e importação/exportação JSON. Não há revisão humana pré-preenchida.
5. **Distribuição:** curva acumulada da maior para a menor frequência, tabela completa, número de oradores necessário para alcançar metade dos registros e comparação de dois oradores com base comum.
6. **Reprodutibilidade:** filtros e controles na URL, botão de cópia, Voltar/Avançar do navegador; pacote ZIP com os CSVs completos do recorte e dos períodos A/B, filtros, regras, denominadores, revisão e hashes em `analise.json`.
7. **Desempenho e leitura:** índice de cerca de 540 KB, textos mensais carregados sob demanda com cache e recuperação de falhas; letras auxiliares maiores, controles de 44 px e barras mensais verticais agrupadas por ano no celular.
8. **Qualidade:** ausência de texto integral, resumo e indexação, por mês ou tipo de fala, com contagens e percentuais; botão para comparar todos os tipos.

A visão inicial mostra **4.045 registros da categoria Discurso**, de **106 oradores distintos** ao longo da janela. Os dez mais frequentes somam **1.955 registros (48,3%)**. **620** desses discursos não têm texto integral no corpus. Use “Todos os usos” para explorar os demais tipos de pronunciamento.

## Como explorar

1. Observe o recorte descrito acima dos indicadores. A visão inicial cobre fev/2019–jan/2023.
2. Selecione uma barra mensal para isolar aquele mês, ou use os campos de período.
3. Selecione um orador ou tema para combinar esse filtro aos demais.
4. Leia o resumo e consulte o registro no Senado antes de interpretar o conteúdo.
5. Baixe o recorte em CSV; use **Restaurar visão inicial** para recomeçar.

As opções de filtro mostram o universo elegível completo; combinações incompatíveis resultam em estado vazio explícito. Busca é uma expressão contínua, sem diferenciar maiúsculas ou acentos, em resumo + indexação; não pesquisa o texto integral. O CSV simples contém os registros filtrados. Para preservar a configuração, use o pacote ZIP: `recorte.csv`, `periodo-a.csv`, `periodo-b.csv`, `analise.json` e `LEIA-ME.txt`. A URL reproduz os filtros na mesma versão do dashboard e precisa de acesso à mesma hospedagem; `localhost` não é um endereço público.

## Atualizar / reproduzir os dados

A reconstrução precisa de internet apenas se os arquivos brutos ainda não estiverem presentes. O Parquet (~27 MB) fica em `data/raw/` e é ignorado no Git; o índice compacto, os 45 fragmentos mensais com registros, o card e o manifesto estão incluídos. Meses vazios não precisam de fragmento. O JSON completo (~9,6 MB) permanece como artefato de auditoria e compatibilidade, mas nunca é carregado pela interface.

```bash
cd exercicios/04-storytelling-discursos
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/prepare_data.py
```

Para baixar novamente a mesma revisão fixada:

```bash
python scripts/prepare_data.py --download
```

A revisão é `c20b4e1ea45bbbfb408167cc07c6f79789c7c345` (v1.1.1). O script verifica o SHA-256 do Parquet antes de gerar dados. Não atualiza silenciosamente para `main`: uma mudança de revisão exige revisar o hash esperado e os testes. `builtAt` e o hash do JSON mudam a cada reconstrução; os registros e os agregados permanecem iguais para a mesma revisão e regras.

## Validação

Testes analíticos (Node.js 20+):

```bash
node --test tests/*.test.mjs
```

Testes de navegador opcionais, com o servidor em execução, Playwright e Chrome instalados:

```bash
npm install --prefix /tmp/vozes-senado-qa --no-audit --no-fund playwright
NODE_PATH=/tmp/vozes-senado-qa/node_modules node tests/browser.cjs
```

O teste usa `/opt/google/chrome/chrome`; defina `CHROME_PATH` para outro executável e `DASHBOARD_URL` para outra porta. Neste contêiner, o Chrome precisa de `--no-sandbox` por restrição de namespaces; essa opção pertence somente ao teste local, não ao dashboard. Capturas de QA são gravadas em `/tmp/vozes-v2-desktop.png` e `/tmp/vozes-v2-mobile.png`.

Consulte [VALIDACAO.md](VALIDACAO.md) para os resultados e limites.

## Arquivos e método

| Arquivo | Função |
|---|---|
| `index.html`, `styles.css` | Estrutura narrativa, textos e layout |
| `app.js`, `views.mjs`, `ui.mjs` | Estado, visualizações, interações e renderização segura |
| `state.mjs` | Serialização/validação da URL |
| `data-store.mjs` | Carregamento sob demanda com cache e retentativa |
| `export.mjs` | Pacote ZIP local, sem CDN |
| `review.mjs` | Revisão humana, importação/exportação e persistência |
| `analytics.mjs` | Filtros, agregações e CSV compartilhados com testes |
| `scripts/prepare_data.py` | Download fixado, auditoria e dicionário temático |
| `data/catalog.json`, `data/details/` | Índice leve e textos mensais usados pelo navegador |
| `data/dashboard.json` | Snapshot completo para testes e auditoria, não carregado pela interface |
| `data/review-sample.json`, `assisted-review.json` | Amostra fixa e leitura assistida por IA, separadas dos rótulos humanos |
| `data/manifest.json` | Proveniência, métricas de auditoria e SHA-256 |
| `data/raw/dataset-card.md`, `collection.json` | Documentação do produtor na revisão utilizada |
| `tests/` | Verificações analíticas e de navegador |
| [PLANEJAMENTO.md](PLANEJAMENTO.md) | Plano registrado antes da implementação |
| [METODOLOGIA.md](METODOLOGIA.md) | Fórmulas, exclusões, limitações e decisões |
| [REFERENCIAS.md](REFERENCIAS.md) | Literatura e escopo de consulta |

Esta é uma análise descritiva de um corpus, não uma avaliação de desempenho parlamentar. Não há publicação externa, integração com modelos de IA em execução ou rastreamento de visitantes.

## Como revisar os temas

Abra **Auditoria → Abrir amostra e revisão temática**. Informe um identificador de revisor, leia resumo/indexação e escolha Sim, Não ou Em dúvida, acrescentando justificativa. A previsão pode ser revelada em um painel separado. As anotações são salvas no armazenamento local do navegador e não são enviadas a nenhum servidor. Exporte o JSON para preservar ou compartilhar; a importação **substitui** a revisão local e exige a mesma revisão do dataset e versão de regras.

A amostra é fixa e independente dos filtros principais, com 5 detecções positivas e 5 negativas por tema. Métricas referem-se somente aos pares decididos dessa amostra. A leitura assistida por IA encontrou cinco divergências possíveis; não é validação humana, revisão cega ou estimativa de desempenho no corpus. Consulte [AUDITORIA-TEMATICA.md](AUDITORIA-TEMATICA.md).

## Limites que continuam importantes

A comparação entre oradores usa contagens, não taxas por dias efetivos de exercício. A investigação das fontes adicionais não recuperou os intervalos completos de exercício/substituição; mandato nominal e licenças isoladas não são denominador suficiente. Esse ajuste, mencionado como etapa posterior na proposta, não foi simulado. Nenhuma validação humana foi fabricada: a ferramenta para realizá-la está funcional, com a amostra e os critérios documentados.
