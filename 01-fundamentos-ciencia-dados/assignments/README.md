# Documentação dos Notebooks sobre Discursos do Senado

Este README descreve o pipeline de coleta, exploração, modelagem supervisionada e análise temática construído nos notebooks `01-preparar-base-discursos.ipynb`, `02-analisar-discursos.ipynb`, `03-analisar-discursos-aprendizado-supervisionado.ipynb` e `04-analisar-discursos-aprendizado-nao-supervisionado.ipynb`, localizados em `01-icd/assignments`.

## 0. Arquivos de suporte

- Notebook 01: `01-preparar-base-discursos.ipynb` – coleta e higienização dos pronunciamentos.
- Notebook 02: `02-analisar-discursos.ipynb` – análise exploratória e visualizações quantitativas.
- Notebook 03: `03-analisar-discursos-aprendizado-supervisionado.ipynb` – classificação de partidos com TF-IDF e modelos lineares.
- Notebook 04: `04-analisar-discursos-aprendizado-nao-supervisionado.ipynb` – extração de tópicos com NMF e TF-IDF.
- Documento síntese: `02-tarefa-ia-setor-publico.md` – discussão de riscos e benefícios de IA no setor público.

## 1. Visão geral do pipeline

- **Fonte dos dados**: Portal de Dados Abertos do Senado Federal (`https://legis.senado.leg.br/dadosabertos`), com coleta via `plenario/lista/discursos/{AAAAMMDD}/{AAAAMMDD}.json` e `discurso/texto-integral/{CodigoPronunciamento}`.
- **Cobertura**: pronunciamentos da 56ª Legislatura (01/02/2019 a 31/01/2023), 15.729 discursos com metadados e texto integral quando disponível.
- **Produtos principais**: arquivo parquet com discursos (`_data/discursos_<ini>_<fim>.parquet`), painéis quantitativos, classificadores para prever partido e modelos NMF para agrupamento temático.
- **Problemas tratados**: entendimento do volume e da autoria dos discursos, identificação de padrões temporais e semânticos, e avaliação de modelos de PLN para tarefas de classificação.

## 2. Configuração do ambiente

- Utilize Python 3.10+ com dependências: `requests`, `pandas`, `pyarrow`, `datasets`, `scikit-learn`, `matplotlib`, `seaborn`, `plotly` e `tqdm`.
- Instalação rápida:

  ```bash
  pip install requests pandas pyarrow datasets scikit-learn matplotlib seaborn plotly tqdm
  ```

- Para reproduzir as análises sem acesso à internet, aponte `DATA_FILE_HF` nos notebooks 02, 03 e 04 para o parquet gerado pelo Notebook 01 em vez do repositório Hugging Face (`fabriciosantana/discursos-senado-legislatura-56`).
- Os notebooks são compatíveis com Google Colab (botão disponível em cada arquivo) e com ambientes Jupyter locais.

## 3. Notebook 01 – Preparar base de discursos

### Implementação

1. Cria sessão HTTP com retries exponenciais (`requests.Session` + `Retry`) para tolerar códigos 429/5xx.
2. Divide intervalos maiores que 31 dias em janelas menores (`montar_intervalo_de_datas`) conforme restrição da API.
3. Normaliza a resposta JSON com `pd.json_normalize`, preservando hierarquias de `TipoUsoPalavra`, `Publicacoes` e `Apartes`.
4. Filtra discursos com link válido para texto integral (`preparar_discursos_para_download`) e padroniza colunas obrigatórias.
5. Faz download assíncrono dos textos (`fazer_download_texto_discursos`) usando `ThreadPoolExecutor`, registrando campos `ok`, `status` e `msg` para auditoria.
6. Persiste o resultado em `_data/` com compressão `zstd` e reutiliza arquivos existentes mediante confirmação do usuário.

### Como executar

1. Garanta as dependências instaladas e execute as células em ordem; `_data/` é criado automaticamente.
2. Informe data inicial e final quando solicitado (`2019-03-29` a `2019-03-31` são usados se pressionar ENTER).
3. Caso o parquet do intervalo já exista, escolha entre reutilizá-lo ou refazer o download.
4. O notebook pode ser executado iterativamente para cobrir toda a legislatura; basta ajustar as datas ou orquestrar várias execuções sequenciais.

### Resultados

- Gera arquivos `discursos_<ini>_<fim>.parquet` contendo metadados e texto integral (quando disponível) de cada pronunciamento.
- Execução completa (01/02/2019 a 31/01/2023) resultou em 15.729 linhas, com 15.039 textos baixados (`ok=True`) e 690 URLs indisponíveis (`status=404`).
- Campos auxiliares (`__janela_inicio`, `__janela_fim`, `ok`, `status`, `msg`) facilitam a auditoria da coleta e a reexecução seletiva.

## 4. Notebook 02 – Analisar discursos (análise quantitativa)

### Implementação

- Carrega o parquet via `datasets.load_dataset`, converte para `pandas` e audita tipos, valores faltantes e consistência dos metadados.
- Deriva variáveis temporais (`ano`, `mes`, `dia_semana`) e de tamanho textual (contagem de palavras e caracteres).
- Produz painéis com `matplotlib`/`seaborn` para frequência por ano, mês, dia da semana, autor, partido, UF e tipo de uso da palavra.
- Resume a distribuição do tamanho dos discursos e destaca disponibilidade do texto integral.

### Como executar

1. Ajuste `DATASET_HF_REPO` e `DATA_FILE_HF` para o dataset remoto ou para o caminho local (`_data/discursos_*.parquet`).
2. Execute as células sequencialmente; tabelas intermediárias são exibidas com `display()` e gráficos são renderizados inline.
3. Para exportar figuras, utilize `plt.savefig` conforme necessário (os comandos-base estão comentados no notebook).

### Resultados observados

- Os discursos concentram-se entre 2019 e 2022, com picos mensais em períodos de intensa atividade legislativa.
- Lideranças partidárias e relatorias respondem pelo maior volume de falas; PT, Podemos e MDB figuram entre os partidos mais prolíficos.
- A maioria dos discursos possui texto integral disponível, mediana de ~464 palavras (≈2,8 mil caracteres) e cauda longa de pronunciamentos extensos.
- Sessões plenárias ocorrem majoritariamente entre terça e quinta-feira; sábados e domingos apresentam volume residual.
- A combinação de tabelas e gráficos sustenta análises posteriores (supervisionadas e temáticas) ao revelar padrões de autoria e calendário.

## 5. Notebook 03 – Análise com aprendizado supervisionado

### Implementação

- Filtra os oito partidos com maior volume de discursos e limita cada classe a 800 amostras (`sample` estratificado) para balancear o conjunto.
- Consolida o texto (`df_balanceado['texto']`), aplica divisão treino/teste estratificada (`test_size=0.2`, `random_state=42`).
- Usa `TfidfVectorizer` com unigramas e bigramas (`ngram_range=(1, 2)`, `max_features=20000`, `min_df=5`, `strip_accents='unicode'`).
- Treina quatro pipelines de classificação e gera relatórios de desempenho (`classification_report`) e matrizes de confusão (`ConfusionMatrixDisplay`).

### Algoritmos e aplicabilidade

- **Regressão Logística (one-vs-rest)**: minimiza perda logística para separar classes linearmente; fornece probabilidades interpretáveis e funciona bem em espaços esparsos de alta dimensionalidade como TF-IDF.
- **SVM Linear (`LinearSVC`)**: maximiza a margem entre classes usando perda hinge; robusto a features redundantes e eficaz para texto devido à propriedade de margem larga.
- **Multinomial Naive Bayes**: modelo generativo que assume distribuição multinomial das contagens de termos; rápido e competitivo em cenários com vocabulário grande, servindo como baseline leve.
- **Passive Aggressive Classifier**: algoritmo on-line de margem máxima que atualiza o hiperplano apenas quando erra; indicado para fluxos de texto e para lidar com leve desbalanceamento mantendo custo computacional baixo.

### Como executar

1. Garanta o parquet carregado (via Hugging Face ou `_data`) e execute as células na ordem indicada.
2. Ajuste `max_por_partido`, `ngram_range` ou `max_features` para testar outras configurações; os pipelines compartilham o mesmo vetor TF-IDF.
3. Utilize os relatórios e matrizes de confusão para identificar classes com maior confusão e justificar ajustes futuros.

### Resultados observados

- A regressão logística com TF-IDF alcançou acurácia de 0,973 na execução de referência, seguida de SVM linear com desempenho similar.
- Naive Bayes e Passive Aggressive apresentaram acurácia ligeiramente menor, porém superior a 0,90, confirmando que o vocabulário diferencia bem os partidos analisados.
- As matrizes de confusão mostram confusões residuais entre legendas com agendas próximas, apontando a necessidade de features adicionais ou divisão temporal.

## 6. Notebook 04 – Análise temática com NMF

### Implementação

- Seleciona até 6.000 discursos para acelerar a vetorização mantendo representatividade temporal e política.
- Tokeniza e vetorializa com `TfidfVectorizer` (unigramas e bigramas, `min_df=5`), removendo stopwords customizadas em português.
- Ajusta `NMF` com 12 componentes para decompor a matriz TF-IDF em temas latentes (`W` documentos × temas, `H` temas × termos).
- Atribui a cada discurso o tema dominante e gera análises: ranking de termos, evolução temporal, participação percentual, temas líderes por mês, Sankey (senador/partido/UF × tema) e heatmap partido × tema.

### Algoritmo (NMF) e aplicabilidade

- **Non-negative Matrix Factorization** decompõe a matriz de frequências em fatores não-negativos, resultando em representações aditivas que facilitam interpretar conjuntos de palavras correlacionadas.
- Adequado para descobrir tópicos latentes em textos parlamentares, pois produz componentes esparsos que destacam agendas específicas (ex.: previdência, saúde, educação) preservando a aditividade dos pesos.

### Como executar

1. Confirme dependências adicionais (`plotly`) e a disponibilidade do parquet com discursos.
2. Ajuste `MAX_DISCURSOS`, `N_TEMAS` ou listas de stopwords conforme a granularidade desejada.
3. Execute as células em ordem; gráficos `matplotlib` são renderizados inline e figuras `plotly` retornam estruturas interativas compatíveis com Colab.

### Resultados observados

- A NMF identificou doze agrupamentos; dois deles concentram discursos protocolares (`Debates Gerais`).
- Os temas mais frequentes destacam agendas sobre medidas provisórias, debates gerais, segurança pública e reforma da previdência.
- A linha do tempo evidencia o pico de saúde e vacinação em 2020-2021 (pandemia) e a predominância de previdência em 2019, enquanto Sankeys conectam autores, partidos e estados às pautas dominantes.

| Tema aproximado | Principais termos (amostra) | Discursos |
| --- | --- | --- |
| Medidas Provisórias | `emenda`, `medida provisoria`, `provisoria`, `medida`, `texto` | 962 |
| Debates Gerais (procedimentais) | `possa`, `muita`, `sei`, `estava`, `tempo` | 823 |
| Segurança Pública | `nacional`, `convido`, `deputado`, `vida`, `deus` | 801 |
| Reforma da Previdência | `reforma`, `previdencia`, `paim`, `paulo paim`, `pais` | 612 |
| Saúde e Vacinação | `saude`, `vacina`, `vacinas`, `covid`, `pandemia` | 565 |
| Judiciário e STF | `supremo`, `tribunal`, `tribunal federal`, `ministro`, `stf` | 550 |
| Meio Ambiente e Amazônia | `amazonia`, `meio ambiente`, `energia`, `ibama`, `parque` | 521 |
| Educação | `educacao`, `ensino`, `escola`, `escolas`, `professores` | 341 |
| Direitos das Mulheres | `mulheres`, `mulher`, `violencia`, `feminina`, `direitos` | 321 |
| Energia e Combustíveis | `preco`, `petrobras`, `combustiveis`, `petroleo`, `diesel` | 262 |
| Agronegócio | `estado`, `wellington fagundes`, `mato grosso`, `produtores`, `agro` | 242 |
| Debates Gerais (homenagens) | `esperidiao amin`, `santa catarina`, `homenagem`, `sessao`, `agradeco` | — |

## 7. Caracterização global da base consolidada

- **Tamanho**: 15.729 discursos, 30 variáveis observadas.
- **Autores**: 1.794 nomes únicos (principalmente senadores, mas inclui convidados externos e deputados em sessões conjuntas).
- **Partidos**: 32 siglas registradas; 2.074 discursos sem informação de partido/UF (majoritariamente convidados).
- **Cobertura do texto integral**: 15.039 discursos com download bem-sucedido (`ok=True`), 690 anotações com falha (`status=404`).
- **Comprimento dos textos**: mediana ≈464 palavras (≈2.842 caracteres), média 728 palavras, máximo 17.602 palavras.
- **Distribuição temporal**: picos em setembro/2021 (949 discursos), agosto/2021 (792) e maio/2022 (753); novembro/2020 apresenta o menor volume (46 discursos).
- **Dias da semana**: terça (4.421) e quarta-feira (4.667) concentram pronunciamentos; sábados somam apenas 48 discursos.

## 8. Dicionário de dados

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

## 9. Avaliação e próximos passos

- Modelos lineares com TF-IDF distinguiram bem os oito partidos mais ativos (acurácia até 0,973); ampliar cobertura exige incorporar partidos com menos discursos e avaliar divisões temporais.
- O desbalanceamento residual e a proximidade temporal entre discursos do mesmo autor podem inflar métricas; recomenda-se validação cruzada estratificada e cortes por ano.
- A análise temática revela agendas prioritárias e enseja validações qualitativas com especialistas para consolidar rótulos dos tópicos (especialmente os dois clusters gerais).
- Próximas etapas sugeridas:
  1. Enriquecer o dataset com variáveis derivadas (`ano`, `mês`, tamanho do texto, cargo) e metadados do processo legislativo.
  2. Testar embeddings pré-treinados (ex.: BERTimbau) e modelos não lineares (Random Forest, Gradient Boosting) para comparação com o baseline linear.
  3. Automatizar monitoramento de qualidade (duplicatas, textos truncados) antes de novas versões públicas do dataset.
