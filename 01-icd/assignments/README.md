# Documentação dos Notebooks sobre Discursos do Senado

Este documento consolida as análises realizadas nos notebooks `01_preparar_base_discursos.ipynb`, `02_analise_quantitativa_discursos.ipynb` e `03-analise-aprendizado-supervisionado.ipynb`, localizados em `01-icd/assignments`. Ele descreve a preparação da base de discursos do Senado Federal, a análise quantitativa exploratória e os experimentos com modelos supervisionados para classificação partidária.

## 1. Contexto, fonte de dados e problema de pesquisa

- **Fonte oficial**: Portal de Dados Abertos do Senado Federal (`https://legis.senado.leg.br/dadosabertos`). Os notebooks consomem os endpoints `plenario/lista/discursos/{AAAAMMDD}/{AAAAMMDD}.json` (lista de discursos) e `discurso/texto-integral/{CodigoPronunciamento}` (texto em formato `.txt`).
- **Período coberto**: pronunciamentos de 01/02/2019 a 10/01/2023 (56ª Legislatura), totalizando 15.729 discursos no arquivo `data/hf_discursos/data/full/discursos_2019-02-01_2023-01-31.parquet`.
- **Objetivo analítico**: compreender padrões discursivos dos senadores (volume, conteúdo e metadados) e avaliar a capacidade de modelos de PLN para prever o partido do orador a partir do texto integral.
- **Granularidade**: uma linha por pronunciamento, com metadados do autor, contexto de fala e texto integral quando disponível.

## 2. Preparação da base (Notebook 01)

1. **Sessão HTTP robusta**: utiliza `requests.Session` com retries exponenciais (`Retry` do `requests.adapters`) para minimizar falhas temporárias (status 429/5xx). Timeouts configurados em 90 s para JSON e 60 s para TXT.
2. **Janelas de coleta**: a API limita consultas a 31 dias; o notebook gera janelas deslizantes e registra `__janela_inicio` e `__janela_fim` para auditoria.
3. **Download do catálogo**: cada janela é normalizada com `pd.json_normalize`, preservando hierarquias de `TipoUsoPalavra`, `Publicacoes` e `Apartes`.
4. **Seleção para download de texto**: `preparar_discursos_para_download` garante URL válida no campo `TextoIntegralTxt` e normaliza colunas críticas.
5. **Coleta do texto integral**: paraleliza downloads com `ThreadPoolExecutor` (8 workers). Indicadores `ok`, `status` e `msg` registram sucesso ou falha (690 respostas 404 sinalizam ausência de texto).
6. **Persistência**: o dataframe final é salvo em `_data/discursos_<ini>_<fim>.parquet` (compressão `zstd`) e reutilizado se já existir.

## 3. Caracterização da base consolidada

- **Tamanho**: 15.729 discursos, 30 campos (ver dicionário). 
- **Autores**: 1.794 nomes únicos. A maioria é `Senador(a)`, mas existem `Deputado(a)` (sessões conjuntas) e `Autor Externo`.
- **Partidos**: 32 siglas registradas; 2.074 discursos sem informação de partido/UF (principalmente convidados).
- **Cobertura do texto integral**: 15.039 discursos com download bem-sucedido (`ok=True`, status 200), 690 sem texto (`status=404`).
- **Tamanho dos discursos**: mediana de 464 palavras (≈ 2.842 caracteres); média de 728 palavras com desvio-padrão 880; máximo de 17.602 palavras.
- **Distribuição temporal**: picos em setembro/2021 (949 discursos), agosto/2021 (792) e maio/2022 (753); queda em 2020 devido à pandemia (mínimo em novembro/2020 com 46).
- **Dias da semana**: terça (4.421) e quarta-feira (4.667) concentram a atividade; sábados são raros (48 discursos).

## 4. Dicionário de dados

| Variavel | Nome | Tipo | Unidade | Dominio | Descricao | Obs |
| --- | --- | --- | --- | --- | --- | --- |
| id | Identificador interno do discurso | Texto | - | Valores numéricos em texto; único por pronunciamento | Chave primária do dataset fornecida pela API | Duplicado em CodigoPronunciamento |
| CodigoPronunciamento | Código do pronunciamento | Texto | - | Identificadores únicos (ex.: 451286) | Código oficial usado nas APIs de discurso do Senado | Igual ao id na versão atual da base |
| Casa | Casa legislativa | Texto | - | {"Senado Federal","Congresso Nacional"} | Indica a casa ou plenário em que o pronunciamento ocorreu | Predominantemente "Senado Federal" |
| Data | Data do pronunciamento | Data | YYYY-MM-DD | 2019-02-01 a 2023-01-10 | Data oficial registrada para o pronunciamento | Armazenada como texto; converter para datetime para análises |
| Resumo | Resumo do discurso | Texto | - | Texto livre | Resumo curto produzido pela secretaria do Senado | 57 registros ausentes (~0,4%) |
| Indexacao | Palavras-chave indexadas | Texto | - | Lista de termos separados por vírgula | Vocabulário controlado com temas associados ao discurso | 35 registros ausentes (~0,2%) |
| TextoIntegral | URL do texto integral (HTML) | Texto | - | URL https:// | Link para a página web do pronunciamento | Sempre preenchido |
| TextoIntegralTxt | URL do texto integral (TXT) | Texto | - | URL https:// | Endpoint direto para o arquivo .txt do discurso | Utilizado para baixar o texto bruto |
| UrlTextoBinario | URL do texto binário | Texto | - | URL https:// | Link para versão binária (PDF) quando disponível | Nem todos os links retornam arquivo |
| TipoAutor | Tipo do autor | Categórico (nominal) | - | {"Senador(a)","Deputado(a)","Autor Externo"} | Classificação do tipo de participante que fez o discurso | Autores externos incluem convidados e autoridades |
| FuncaoAutor | Função do autor | Categórico (nominal) | - | {"SENADOR","DEPUTADO","EXTERNO"} | Função/cargo institucional associado ao autor | Correlacionado com TipoAutor |
| NomeAutor | Nome do autor | Texto | - | 1.794 nomes distintos | Nome completo do parlamentar ou convidado | Não padroniza acentuação em alguns casos |
| CodigoParlamentar | Código do parlamentar | Texto | - | 233 códigos numéricos em texto | Identificador numérico interno do senador/deputado | Ausente em autores externos (2.074 registros) |
| Partido | Sigla do partido | Categórico (nominal) | - | 32 siglas (ex.: PT, MDB, PODEMOS) | Partido associado ao autor na data do discurso | Ausente em 2.074 registros; necessário padronizar siglas extintas |
| UF | Unidade da Federação | Categórico (nominal) | - | 27 UF; vazio para autores externos | Estado de representação do autor | Mesma contagem de ausentes de Partido |
| TipoUsoPalavra.Codigo | Código do uso da palavra | Texto | - | 22 códigos numéricos | Código interno para a finalidade do pronunciamento | Usado para unir com dicionários auxiliares |
| TipoUsoPalavra.Sigla | Sigla do uso da palavra | Texto | - | Siglas como "DIS", "PO", "DISP" | Abreviação do tipo de uso da palavra | Correspondência direta com a descrição |
| TipoUsoPalavra.Descricao | Descrição do uso da palavra | Categórico (nominal) | - | 22 descrições (ex.: Discurso, Pela ordem) | Categoria textual da finalidade do pronunciamento | Campo utilizado nas análises de frequência |
| TipoUsoPalavra.IndicadorAtivo | Uso da palavra ativo | Categórico (nominal) | - | {"Sim","Não"} | Marca se a categoria está ativa na tipologia do Senado | Padrão "Sim"; algumas categorias históricas marcadas como "Não" |
| Publicacoes.Publicacao | Metadados de publicação | Texto | - | Lista de dicionários com DataPublicacao, Fonte etc. | Registra onde o discurso foi publicado no Diário do Senado | Ausente em 734 registros; requer normalização (explode) para análises |
| Apartes.Aparteante | Lista de aparteantes | Texto | - | Listas de nomes ou vazio | Relaciona parlamentares que fizeram apartes durante o discurso | Somente 868 discursos contêm apartes |
| __janela_inicio | Início da janela de coleta | Data | YYYY-MM-DD | 2019-02-01 a 2023-01-01 | Data inicial usada na coleta em blocos de até 31 dias | Armazenada como string; útil para auditoria |
| __janela_fim | Fim da janela de coleta | Data | YYYY-MM-DD | 2019-03-03 a 2023-01-31 | Data final da janela correspondente | Armazenada como string; útil para auditoria |
| CargoAutor | Cargo explicitado | Texto | - | 459 cargos distintos | Cargo/título informado para autores externos | Presente em 904 registros apenas |
| OrgaoAutor | Órgão de origem do autor | Texto | - | 558 órgãos distintos | Órgão ou entidade representada por autor externo | Somente 811 registros preenchidos |
| PaisAutor | País do autor | Texto | - | {Brasil, Portugal, Canadá, EUA, Suécia, Reino Unido} | País de origem quando não é parlamentar brasileiro | Preenchido em 97 registros |
| TextoDiscursoIntegral | Texto integral do discurso | Texto | - | Até 106.610 caracteres | Corpo completo do pronunciamento após download | Log de sucesso indicado por ok/status; pode estar vazio quando download falha |
| ok | Indicador de download bem-sucedido | Categórico (nominal) | - | {True, False} | Sinaliza se o texto integral foi recuperado com sucesso | 690 discursos registram False (texto ausente) |
| status | Status HTTP do download | Numérico (inteiro) | Código HTTP | {200, 404} | Código retornado pela API ao tentar baixar o texto | 404 acompanha ausências de texto |
| msg | Mensagem de download | Texto | - | "" ou "404 (sem texto integral)" | Mensagem auxiliar para diagnósticos de download | Preenchido apenas em casos de falha |

## 5. Análises descritivas iniciais (Notebook 02)

### Medidas de posição e dispersão
- **Comprimento do texto**: média 728 palavras (desvio 880), mediana 464, quartil superior 912. Em caracteres: média 4.451, mediana 2.842, máximo 106.610.
- **Volume por autor**: top 5 — Izalci Lucas (704), Paulo Paim (676), Eduardo Girão (593), Rodrigo Pacheco (496), Jorge Kajuru (458).
- **Participação partidária**: PT (1.890 discursos), Podemos (1.743), MDB (1.675), PSD (1.330), PSDB (1.179), PP (919), PL (832), DEM (779).

### Exploração gráfica e padrões
- **Séries temporais mensais**: gráficos de linhas revelam pico em 2021 (agenda pandêmica e CPI), queda em 2020 (sessões remotas) e nova alta no fim de 2022.
- **Barplots por partido e UF**: mostram concentração em estados como RS, DF, RN, MG e CE; partidos de liderança ocupam maior fatia.
- **Tipos de uso da palavra**: `Discurso` (5.668) é majoritário, seguido de `Pela ordem` (2.620), `Discussão` (1.618) e `Orientação à bancada` (1.340), evidenciando predominância de falas regimentais.
- **Distribuição de comprimento**: histogramas exibem cauda longa; boxplots indicam outliers extensos associados a relatórios e pronunciamentos especiais.
- **Dia da semana**: terça e quarta concentram 57% dos discursos, refletindo o calendário de sessões deliberativas.

## 6. Discussão preliminar e qualidade dos dados

- **Ausências estruturadas**: campos `Partido`, `UF`, `CodigoParlamentar` e metadados de autores externos têm cerca de 13% de missing, exigindo decisões de imputação ou exclusão conforme o objetivo analítico.
- **Cobertura do texto**: 4,4% das linhas não possuem texto integral (status 404). É necessário decidir entre excluir essas linhas, buscar fontes alternativas (PDF) ou sinalizar lacunas nos resultados.
- **Padronização**: siglas partidárias extintas ou trocas de partido aparecem sem normalização temporal; `NomeAutor` pode apresentar variações em acentuação. Recomenda-se aplicar tabelas de referência para identificar fusões (ex.: DEM → União Brasil) conforme o recorte temporal.
- **Campos aninhados**: `Publicacoes.Publicacao` e `Apartes.Aparteante` são listas; para análises detalhadas, é preciso explodir essas colunas.
- **Qualidade de datas**: `Data`, `__janela_inicio` e `__janela_fim` chegam como texto e devem ser convertidas para `datetime` antes de cálculos.

## 7. Análise exploratória avançada (Notebook 02)

- **Matriz de ausência e heatmaps**: (células preparadas) permitem visualizar onde há falhas sistemáticas de dados, especialmente em autores externos.
- **Agregações multivariadas**: combinações `Partido × TipoUsoPalavra` e `Partido × Mês` indicam agendas distintas (por exemplo, PT com mais `Discurso` e `Fala da Presidência`, Podemos com maior proporção de `Discussão`).
- **Comprimento × Categoria**: scatterplots relacionam tamanho do texto com tipo de uso, sugerindo que `Como Relator` gera discursos mais extensos.
- **Indicadores derivados**: criação de `texto_len_palavras`, `texto_len_caracteres` e `resumo_len_palavras` serve para detectar outliers e subsidiar engenharia de atributos.

## 8. Pré-processamento e transformação para modelagem (Notebook 03)

1. **Seleção de colunas**: utiliza `Data`, `NomeAutor`, `Partido`, `UF`, `TextoDiscursoIntegral`; renomeia `TextoDiscursoIntegral` para `texto` e `NomeAutor` para `nome_autor`.
2. **Limpeza**:
   - remove registros com `Partido` ou `texto` nulos;
   - trim de espaços e exclusão de textos vazios (após strip);
   - filtro para discursos com pelo menos 20 palavras (`n_palavras ≥ 20`), reduzindo ruído de falas protocolares.
3. **Balanceamento**:
   - identifica os 8 partidos com maior volume;
   - amostra até 800 discursos por partido para balancear (`groupby().sample()`), resultando em 6.322 registros (DEM possui apenas 722 disponíveis).
4. **Features textuais**: vetoriza com `TfidfVectorizer` (máx. 20.000 features, n-gramas 1–2, `min_df=5`, normalização com remoção de acentos).

## 9. Divisão treino/teste

- `train_test_split` estratificado (seed 42), proporção 80/20:
  - **Treino**: 5.057 discursos.
  - **Teste**: 1.265 discursos.
- Mantém a distribuição balanceada entre os 8 partidos (cada grupo com 578–640 instâncias de treino; teste proporcional ~145–160).
- Métrica principal: acurácia; relatórios incluem precisão, revocação e F1 por partido.

## 10. Modelos supervisionados testados

| Modelo | Representação | Principais hiperparâmetros | Acurácia (teste) | Destaques |
| --- | --- | --- | --- | --- |
| Regressão Logística multinomial | TF-IDF (1-2 gramas, max_features=20k, min_df=5) | `max_iter=200`, `multi_class='multinomial'` | 0,957 | F1 entre 0,94 e 0,98; menor recall para PODEMOS (0,92) e PL (0,94). |
| Linear SVM (LinearSVC) | TF-IDF (1-2 gramas, max_features=20k, min_df=5) | `C` padrão (1.0), `random_state=42` | 0,973 | F1 ≥ 0,96 para todos os partidos; melhor desempenho para DEM (0,99) e PT (0,98). |

- As matrizes de confusão (geradas nos notebooks) mostram baixa confusão entre partidos ideologicamente distintos; erros concentram-se em partidos de centro (MDB, PSD) versus legendas próximas (PP, PSDB).

## 11. Otimização de hiperparâmetros

- Os notebooks atuais ainda não executam busca sistemática. Recomenda-se implementar:
  1. **Grid Search** (`GridSearchCV`) sobre `C`, `penalty` e `class_weight` na logística, e `C`, `max_df`, `min_df` para TF-IDF.
  2. **Random Search** (`RandomizedSearchCV`) para explorar combinações mais amplas (ex.: limites superiores de `max_features`, inclusão de trigramas, uso de `sublinear_tf`).
  3. **Validação cruzada estratificada (k=5)** para reduzir variância na estimativa e comparar incrementalmente com o baseline atual.
- Deve-se monitorar tempo de execução (TF-IDF denso) e aplicar `n_jobs=-1` quando disponível.

## 12. Avaliação final e discussão crítica

- **Desempenho elevado** (acurácia até 0,973) indica que o vocabulário distingue bem os partidos principais, mas limita-se a oito legendas mais prolíficas; generalização para partidos minoritários precisa de dados adicionais.
- **Risco de sobreajuste temporal**: discursos do mesmo orador em períodos próximos podem cair em treino e teste; considerar divisão temporal (por ano) para avaliar robustez.
- **Cobertura parcial**: 2.074 discursos sem partido/UF não entram na modelagem. Essas linhas podem ser usadas em cenários de predição real (dados sem rótulo), mas é necessário tratar ausência de metadados.
- **Explicabilidade**: coeficientes da logística e pesos da SVM podem ser inspecionados para identificar termos-chave por partido; documentar essas interpretações ajuda na transparência do modelo.
- **Próximos passos sugeridos**:
  1. Enriquecer a base com variáveis derivadas (`ano`, `mês`, `tamanho`, indicadores de cargo) para análises multivariadas.
  2. Testar modelos não lineares (Random Forest, Gradient Boosting) e embeddings pré-treinados (BERTimbau) com fine-tuning.
  3. Implementar monitoramento de qualidade do texto (detecção de duplicatas e discursos truncados) antes de novas versões do dataset.

---

Este README resume os principais achados e recomendações para continuidade do projeto, servindo como referência rápida para quem precisar replicar ou evoluir as análises dos notebooks acima.
