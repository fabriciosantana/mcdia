# Vozes do Senado — storytelling com dados

Dashboard interativo da 56ª legislatura, em português, com dados reais do corpus de [Fabricio Fernandes Santana](https://huggingface.co/datasets/fabriciosantana/discursos-senado-legislatura-56), derivado dos dados abertos do Senado Federal. Primeira versão funcional: HTML, CSS e JavaScript, com preparação reproduzível em Python.

## Como visualizar

No terminal, a partir da raiz deste repositório:

```bash
python3 -m http.server 8000 --bind 0.0.0.0 --directory exercicios/04-storytelling-discursos
```

Abra **http://localhost:8000** no navegador. Em Codespaces/VS Code remoto, abra **Portas / Ports**, encaminhe a porta **8000** e selecione **Abrir no navegador**. Mantenha o terminal aberto; `Ctrl+C` encerra o servidor. Se a porta estiver ocupada, troque `8000` por `8001` no comando e no endereço.

Não abra `index.html` por duplo clique: o navegador precisa de HTTP para carregar o módulo JavaScript e o JSON. Para visualizar, basta Python 3 e um navegador moderno. **Não é necessário instalar pacotes, obter token do Hugging Face ou ter internet após baixar este diretório.** Os links de fonte original exigem internet. O servidor acima serve somente este exercício; não o diretório inteiro do repositório.

## O que foi construído

- Narrativa em quatro partes: ritmo temporal, distribuição da palavra, assuntos exploratórios e consulta aos registros.
- Filtros combináveis de mês inicial/final, tipo de uso da palavra, partido na data, UF, orador, tema e busca por expressão em resumo/indexação.
- Indicadores e títulos calculados para o recorte ativo; contagem e percentual na série mensal.
- Barras selecionáveis por mouse ou teclado, tabelas acessíveis para meses e oradores, dicionário temático exposto, estados vazio/erro e layout responsivo.
- Resumos completos disponíveis no corpus, paginação de oito registros, ordenação por data e links para os pronunciamentos oficiais.
- Download CSV UTF-8 com BOM, separado por ponto e vírgula, contendo **todos** os registros filtrados, não só a página visível. Importar como UTF-8 / delimitador `;` se necessário. Fórmulas potenciais são neutralizadas.
- Snapshot local com 12.414 registros elegíveis, manifesto e hashes; sem bibliotecas, fontes ou gráficos carregados de CDN.

A visão inicial mostra **4.045 registros da categoria Discurso**, de **106 oradores distintos** ao longo da janela. Os dez mais frequentes somam **1.955 registros (48,3%)**. **620** desses discursos não têm texto integral no corpus. Use “Todos os usos” para explorar os demais tipos de pronunciamento.

## Como explorar

1. Observe o recorte descrito acima dos indicadores. A visão inicial cobre fev/2019–jan/2023.
2. Selecione uma barra mensal para isolar aquele mês, ou use os campos de período.
3. Selecione um orador ou tema para combinar esse filtro aos demais.
4. Leia o resumo e consulte o registro no Senado antes de interpretar o conteúdo.
5. Baixe o recorte em CSV; use **Restaurar visão inicial** para recomeçar.

As opções de filtro mostram o universo elegível completo; combinações incompatíveis resultam em estado vazio explícito. Busca é uma expressão contínua, sem diferenciar maiúsculas ou acentos, em resumo + indexação; não pesquisa o texto integral. O CSV contém os filtros materializados nos registros, mas não é um registro persistente da configuração do painel.

## Atualizar / reproduzir os dados

A reconstrução precisa de internet apenas se os arquivos brutos ainda não estiverem presentes. O Parquet (~27 MB) fica em `data/raw/` e é ignorado no Git; o JSON pronto (~9,6 MB), o card e o manifesto estão incluídos.

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
node --test tests/analytics.test.mjs
```

Testes de navegador opcionais, com o servidor em execução, Playwright e Chrome instalados:

```bash
npm install --prefix /tmp/vozes-senado-qa --no-audit --no-fund playwright
NODE_PATH=/tmp/vozes-senado-qa/node_modules node tests/browser.cjs
```

O teste usa `/opt/google/chrome/chrome`; defina `CHROME_PATH` para outro executável e `DASHBOARD_URL` para outra porta. Neste contêiner, o Chrome precisa de `--no-sandbox` por restrição de namespaces; essa opção pertence somente ao teste local, não ao dashboard. Capturas de QA são gravadas em `/tmp/vozes-senado-desktop.png` e `/tmp/vozes-senado-mobile.png`.

Consulte [VALIDACAO.md](VALIDACAO.md) para os resultados e limites.

## Arquivos e método

| Arquivo | Função |
|---|---|
| `index.html`, `styles.css` | Estrutura narrativa, textos e layout |
| `app.js` | Interações, visualizações SVG e renderização segura |
| `analytics.mjs` | Filtros, agregações e CSV compartilhados com testes |
| `scripts/prepare_data.py` | Download fixado, auditoria e dicionário temático |
| `data/dashboard.json` | Dados prontos para visualização offline |
| `data/manifest.json` | Proveniência, métricas de auditoria e SHA-256 |
| `data/raw/dataset-card.md`, `collection.json` | Documentação do produtor na revisão utilizada |
| `tests/` | Verificações analíticas e de navegador |
| [PLANEJAMENTO.md](PLANEJAMENTO.md) | Plano registrado antes da implementação |
| [METODOLOGIA.md](METODOLOGIA.md) | Fórmulas, exclusões, limitações e decisões |
| [REFERENCIAS.md](REFERENCIAS.md) | Literatura e escopo de consulta |

Esta é uma análise descritiva de um corpus, não uma avaliação de desempenho parlamentar. Não há publicação externa, integração com modelos de IA em execução ou rastreamento de visitantes.
