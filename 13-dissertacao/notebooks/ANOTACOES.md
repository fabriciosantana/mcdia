# Anotações para defesa da análise exploratória do corpus de discursos

## 1. Finalidade do notebook

O notebook `01-analisar-base-discursos-rag.ipynb` não implementa um sistema RAG completo. Sua finalidade é anterior: conhecer, auditar e caracterizar o corpus que alimentará os experimentos de recuperação e geração.

Essa distinção é metodologicamente importante. Um sistema RAG pode produzir respostas ruins por pelo menos três grupos de causas:

1. problemas no corpus, como ausência, ruído, duplicidade ou metadados incompletos;
2. problemas na recuperação, como chunking inadequado, embeddings pouco apropriados ou baixa cobertura dos resultados;
3. problemas na geração, como desconsideração do contexto recuperado, alucinação ou citação incorreta.

Este notebook concentra-se no primeiro grupo e fornece parâmetros preliminares para o segundo. A avaliação efetiva da recuperação será tratada no notebook 02.

### Argumento central para a defesa

> Antes de avaliar um recuperador ou um modelo generativo, é necessário demonstrar que o corpus tem cobertura, integridade, granularidade e metadados suficientes. Caso contrário, atribuiríamos ao modelo falhas que podem ter origem nos dados.

O notebook responde a cinco perguntas:

- Qual é a cobertura e a integridade do corpus?
- Como os discursos estão distribuídos no tempo e entre autores, partidos e unidades federativas?
- Quais características textuais afetam indexação e chunking?
- Onde existem riscos de redundância, falta de contexto e desigualdade de representação?
- Quais decisões precisam ser tomadas antes da construção do RAG?

## 2. Configuração e reprodutibilidade

### 2.1 Por que registrar importações, parâmetros e versões

Uma análise científica deve poder ser repetida por outra pessoa. Por isso, o notebook centraliza bibliotecas, parâmetros globais e a semente aleatória `RANDOM_STATE = 42`.

A semente não torna todo algoritmo universalmente determinístico, mas garante que operações como a amostragem de documentos selecionem os mesmos registros em execuções equivalentes. Isso é necessário para comparar resultados e investigar casos concretos.

As configurações do Pandas melhoram a inspeção de tabelas. As configurações do Matplotlib e Seaborn padronizam tamanho, resolução e estilo dos gráficos. Essa padronização reduz diferenças meramente visuais entre execuções.

### 2.2 Stopwords

Stopwords são palavras muito frequentes que, em determinada tarefa, oferecem baixo poder discriminativo, como artigos, preposições, pronomes e verbos auxiliares. Sua remoção pode tornar gráficos de frequência mais interpretáveis.

O notebook combina duas fontes:

- NLTK: 200 termos normalizados;
- Stopwords ISO: 537 termos normalizados;
- união: 538 termos únicos.

A união é feita com conjuntos, portanto palavras repetidas nas duas fontes aparecem uma única vez.

Antes da união, as palavras são convertidas para minúsculas e têm seus acentos removidos. Isso reproduz o tratamento `lowercase=True` e `strip_accents='unicode'` aplicado pelo `CountVectorizer`. Sem essa equivalência, a stopword `não`, por exemplo, poderia não coincidir com o token normalizado `nao`.

O spaCy não é carregado. A biblioteca e o modelo `pt_core_news_sm` teriam custo adicional de instalação e memória para um ganho marginal de cobertura. A lista ISO já é abrangente e adequada ao objetivo exploratório.

### Limitação que deve ser reconhecida

Stopwords não são universalmente irrelevantes. Uma palavra pode ser pouco informativa para um gráfico geral e ainda ser importante para uma consulta específica. Por isso, a lista é aplicada apenas às análises de frequência e bigramas. Ela não remove palavras dos discursos originais e não será aplicada automaticamente aos documentos indexados no RAG.

### Pergunta provável

**Por que não remover stopwords antes de gerar embeddings?**

Modelos modernos de embeddings foram treinados com texto natural e utilizam o contexto completo. A remoção pode alterar sintaxe, negação e significado. Em especial, retirar palavras como “não” pode inverter o sentido. A necessidade de remoção deve ser avaliada por experimento, não presumida.

## 3. Aquisição e validação do arquivo

### 3.1 Por que procurar primeiro o arquivo local

O notebook procura o Parquet local para evitar download repetido, reduzir tempo e permitir trabalho desconectado. Se ele não existir, baixa a versão `v1.1.1` do Hugging Face. No Colab, o Google Drive é usado como armazenamento persistente.

Fixar a revisão `v1.1.1` evita que uma alteração futura no branch `main` modifique silenciosamente os dados analisados. Em pesquisa, a versão do dado deve ser tão explícita quanto a versão do código.

### 3.2 Por que validar o SHA-256

SHA-256 é uma função criptográfica de resumo. Ela produz uma assinatura de tamanho fixo para o conteúdo do arquivo. Uma alteração mínima nos bytes gera, com probabilidade extremamente alta, outro hash.

O hash esperado é:

`e09cfc4793e5394be440906320c7d3008cda5a52b90bbc85bf47446362406af1`

A validação demonstra que o arquivo local e o arquivo publicado correspondem à versão documentada. O hash verifica identidade binária, não qualidade semântica. Um arquivo pode ter o hash correto e ainda conter limitações originárias da coleta.

### 3.3 Por que usar Parquet

Parquet é um formato colunar. Ele preserva tipos, oferece compressão eficiente e permite selecionar colunas sem necessariamente ler todo o conteúdo. Para um corpus com textos longos, tende a ser mais eficiente e confiável que CSV.

O CSV permanece útil para interoperabilidade, mas é mais sujeito a problemas com delimitadores, quebras de linha, codificação e inferência de tipos.

## 4. Inspeção inicial do DataFrame

O corpus possui:

- 15.729 registros;
- 30 colunas;
- 15.729 códigos de pronunciamento únicos;
- período observado entre 1º de fevereiro de 2019 e 10 de janeiro de 2023.

Mostrar as primeiras linhas não é apenas uma formalidade. Essa inspeção confirma se o carregamento produziu colunas e valores plausíveis, permite reconhecer o nível de granularidade e ajuda a detectar erros evidentes, como cabeçalho interpretado como dado ou texto concentrado em uma única coluna.

Uma linha representa um pronunciamento, e `CodigoPronunciamento` funciona como chave de negócio. Essa unidade de análise precisa ser definida porque todas as contagens posteriores dependem dela.

## 5. Auditoria de estrutura, integridade e completude

### 5.1 Tipos, preenchimento, ausências e cardinalidade

Para cada coluna, o notebook calcula:

- tipo de dado;
- quantidade preenchida;
- quantidade ausente;
- percentual ausente;
- número de valores únicos.

Essas medidas têm funções diferentes:

- o tipo indica quais operações são válidas;
- a ausência indica cobertura;
- a cardinalidade indica diversidade e ajuda a reconhecer possíveis identificadores, categorias ou campos quase constantes.

Algumas colunas contêm listas ou arrays aninhados. Como listas não são diretamente hashable em Python, o notebook usa uma representação textual para contar valores únicos nessas colunas. Essa transformação serve apenas à contagem exploratória; não modifica o DataFrame original.

### 5.2 Validação das datas

A conversão usa `errors='coerce'`. Valores que não podem ser interpretados tornam-se `NaT`, o equivalente temporal de valor ausente. Em seguida, o notebook conta datas inválidas.

O resultado foi zero datas inválidas. Isso sustenta as agregações mensais e anuais, mas não prova que todas as datas representam corretamente o evento real; prova apenas que são sintaticamente válidas e coerentes com o intervalo observado.

### 5.3 Unicidade dos códigos

Foram encontrados 15.729 códigos únicos em 15.729 registros e nenhuma duplicidade de chave.

Duplicidade de chave e duplicidade textual são conceitos diferentes:

- duplicidade de chave significa repetição do mesmo identificador;
- duplicidade textual significa que identificadores distintos possuem conteúdo igual ou semelhante.

A ausência de códigos repetidos evita colisões na identificação de documentos, mas não elimina redundância textual.

### 5.4 Por que visualizar as colunas mais ausentes

O gráfico ordena os campos com maior ausência. Isso ajuda a distinguir campos essenciais de campos opcionais ou aplicáveis apenas a alguns tipos de autor.

Ausência não significa automaticamente erro. Por exemplo, cargo, órgão ou país podem não se aplicar a senadores. A interpretação deve considerar a semântica do campo e a origem oficial.

Para RAG, a pergunta relevante é: a ausência impede recuperar, filtrar, apresentar ou citar o documento? Uma coluna opcional pode ter alta ausência sem prejudicar o núcleo da solução.

## 6. Cobertura do conteúdo textual

### 6.1 Por que distinguir texto integral, resumo e indisponibilidade

O conteúdo usado pelo futuro RAG é classificado em três grupos:

- `texto_integral`: pronunciamento completo;
- `resumo_fallback`: ausência do texto integral, mas existência de resumo;
- `indisponível`: ausência dos dois.

Resultados:

- 15.039 textos integrais, ou 95,61%;
- 687 resumos de fallback, ou 4,37%;
- 3 registros indisponíveis, ou 0,02%;
- 15.726 documentos indexáveis, ou 99,98%.

Essa distinção é essencial porque texto integral e resumo não têm a mesma granularidade informacional. Um resumo pode permitir recuperação temática, mas não sustenta com o mesmo nível de detalhe uma resposta ou citação.

A coluna `fonte_documento` deve acompanhar o documento e seus chunks. Isso permite filtrar, ponderar resultados e informar ao usuário quando a evidência provém apenas de resumo.

### 6.2 Relação com os códigos HTTP

Os 15.039 textos integrais correspondem a respostas HTTP 200. Os 690 casos sem texto integral correspondem a HTTP 404. Entre esses, 687 possuem resumo e 3 não possuem conteúdo utilizável.

HTTP 404 significa que o recurso de texto integral não estava disponível no endpoint consultado. Não significa necessariamente que o pronunciamento nunca existiu ou que a coleta falhou por instabilidade de rede.

### 6.3 Implicação para o RAG

Os resumos devem ser indexados com marcação explícita e, preferencialmente, estratégia própria. Misturá-los aos textos integrais sem identificação criaria assimetria: um resumo curto poderia ter alta similaridade com uma pergunta, mas fornecer evidência insuficiente para a resposta.

## 7. Distribuição temporal

### 7.1 Por que preencher meses sem discursos com zero

Agrupar apenas os meses observados excluiria meses sem registros. Isso elevaria artificialmente a média e esconderia lacunas.

O notebook cria um calendário completo com 48 meses e preenche ausência de discursos com zero. Foram identificados:

- janeiro de 2020;
- janeiro de 2021;
- janeiro de 2022.

Janeiro é tradicionalmente associado ao recesso parlamentar, portanto os zeros são plausíveis. Ainda assim, plausibilidade institucional não substitui validação da coleta.

As estatísticas mensais são:

- média: 327,69;
- desvio-padrão: 228,91;
- mediana: 289,50;
- máximo: 949;
- mínimo: zero.

### 7.2 Média, mediana e desvio-padrão

A média é a soma dividida pelo número de meses e pode ser influenciada por picos. A mediana é o ponto central e é mais robusta a valores extremos. O desvio-padrão mede dispersão em torno da média.

A diferença entre média e mediana, combinada ao desvio-padrão elevado, indica variação temporal relevante. Essa variação pode refletir calendário legislativo, conjuntura política, pandemia, eleições, sessões especiais e disponibilidade de registros.

### 7.3 Por que isso importa para recuperação

Períodos com mais documentos têm mais oportunidades de aparecer entre os resultados. Sem avaliação estratificada, o sistema pode parecer eficaz porque funciona bem nos períodos mais densos e falhar nos menos representados.

O notebook 02 deverá distribuir perguntas por período e medir desempenho por estrato temporal.

## 8. Distribuição por autor, partido e UF

### 8.1 Objetivo dos rankings

Os rankings revelam quem e quais grupos estão mais representados. Eles não medem influência, qualidade, produtividade ou importância política; medem apenas frequência de pronunciamentos no corpus.

Essa ressalva evita uma inferência inadequada: mais discursos não implicam maior relevância substantiva.

### 8.2 Heatmap partido por ano

O heatmap cruza os partidos mais frequentes com os anos. A cor facilita identificar concentração e mudança temporal.

Mudanças podem ocorrer por atividade política, tamanho de bancada, troca de partido, substituição parlamentar ou ausência de metadados. Portanto, a visualização é descritiva, não causal.

### 8.3 Implicação para RAG

Um corpus desbalanceado tende a oferecer mais candidatos dos grupos majoritários. O recuperador não “cria” esse desbalanceamento, mas pode amplificá-lo. A avaliação deve medir se consultas equivalentes encontram evidências de grupos e períodos menos frequentes.

## 9. Comprimento e qualidade textual

### 9.1 Medidas calculadas

Para cada documento são calculados:

- caracteres;
- palavras;
- linhas;
- tokens estimados;
- razão entre caracteres e palavras.

O número de palavras aproxima a extensão linguística. Caracteres ajudam a estimar armazenamento e tokens. Linhas ajudam a reconhecer estrutura e possíveis problemas de formatação. A razão caracteres/palavra pode indicar texto incomum, ruído ou idioma diferente.

### 9.2 Quantis

Quantis descrevem a distribuição sem pressupor normalidade. Alguns resultados:

- mediana: 464 palavras e 711 tokens estimados;
- percentil 75: aproximadamente 913 palavras;
- percentil 95: aproximadamente 2.399 palavras;
- percentil 99: aproximadamente 4.103 palavras;
- máximo: 17.602 palavras e 26.653 tokens estimados.

A diferença entre mediana e máximo demonstra cauda longa. Uma única estratégia de armazenamento por documento seria inadequada: textos extensos ultrapassam janelas de contexto e dificultam recuperação precisa.

### 9.3 Histograma em escala logarítmica

Uma escala linear concentraria visualmente a maioria dos documentos na região inicial por causa dos valores extremos. A escala logarítmica comprime ordens de grandeza e permite observar simultaneamente documentos curtos e longos.

Usar log no eixo não transforma o dado armazenado; transforma apenas a representação visual.

### 9.4 ECDF

ECDF é a função de distribuição acumulada empírica. Para cada valor no eixo horizontal, ela mostra a proporção de documentos com tamanho menor ou igual àquele valor.

Ela permite responder perguntas como: “qual proporção caberia em um único limite de tokens?”. Também facilita comparar texto integral e resumo sem depender da escolha arbitrária de classes de um histograma.

## 10. Padrões de qualidade textual

Resultados:

- 1.291 documentos com menos de 50 palavras, 8,21%;
- 7 documentos com mais de 10 mil palavras, 0,04%;
- 44 documentos com URL, 0,28%;
- 1 documento com marcação HTML, 0,01%;
- 3 documentos vazios, 0,02%;
- nenhum caractere de substituição `�` detectado;
- nenhum caso de três ou mais espaços consecutivos detectado.

### 10.1 Por que detectar documentos curtos

Documentos curtos podem ser resumos legítimos, orientações de bancada, registros regimentais ou conteúdo insuficiente. Eles não devem ser removidos apenas pelo tamanho.

No RAG, um trecho curto pode ser altamente preciso, mas também pode não conter contexto suficiente para sustentar uma resposta. A inspeção qualitativa é indispensável.

### 10.2 Por que detectar documentos longos

Documentos longos geram muitos chunks e podem dominar o índice. Também aumentam o risco de separar pergunta e evidência em trechos distantes.

A resposta não é truncar arbitrariamente, mas aplicar segmentação coerente, preservando metadados e posição no documento.

### 10.3 HTML, URLs e codificação

HTML residual pode ser tratado como conteúdo e prejudicar embeddings. URLs podem ser úteis como referência ou ser ruído, dependendo do contexto. O caractere `�` é indício comum de falha de decodificação.

A baixa ocorrência indica boa qualidade técnica, mas os casos encontrados devem ser inspecionados antes de qualquer limpeza.

## 11. Duplicidade exata

### 11.1 Normalização usada

Antes do hash textual, o notebook:

- aplica Unicode NFKC;
- converte para minúsculas com `casefold`;
- reduz sequências de espaços a um espaço;
- remove espaços nas extremidades.

NFKC harmoniza representações Unicode compatíveis. `casefold` é mais adequado que simples `lower` para comparação independente de caixa em diferentes alfabetos.

Após a normalização, é calculado SHA-256 de cada texto. Hashes iguais indicam textos normalizados iguais.

### 11.2 Resultados

- 49 registros pertencem a grupos duplicados;
- 21 grupos de duplicidade;
- 28 cópias excedentes;
- 0,18% do corpus corresponde a cópias excedentes.

“Cópias excedentes” é a soma do tamanho de cada grupo menos uma ocorrência representativa. Isso não significa que 28 registros devam ser automaticamente removidos.

### 11.3 Por que duplicidade prejudica RAG

Textos repetidos podem:

- ocupar armazenamento desnecessário;
- retornar múltiplos chunks equivalentes;
- reduzir diversidade do top-k;
- dar impressão artificial de múltiplas evidências independentes.

Entretanto, identificadores distintos podem representar atos legislativos legítimos. A decisão de deduplicar precisa preservar proveniência e contexto.

## 12. Duplicidade aproximada

Duplicidade aproximada procura textos semelhantes, mas não idênticos. O notebook usa amostra reprodutível de 800 documentos com pelo menos 50 palavras para controlar tempo e memória.

### 12.1 Shingles

Um shingle é uma sequência contígua de tokens. Foram usados shingles de cinco palavras. Cada documento torna-se um conjunto dessas sequências.

Shingles capturam sobreposição local. Cinco palavras reduzem coincidências acidentais, mas podem deixar de reconhecer paráfrases ou textos semelhantes com muitas pequenas alterações.

### 12.2 Jaccard

A similaridade de Jaccard entre conjuntos A e B é:

`J(A,B) = |A ∩ B| / |A ∪ B|`

O valor varia de zero a um:

- zero: nenhuma unidade compartilhada;
- um: conjuntos idênticos.

Jaccard ignora frequência e considera apenas presença ou ausência dos shingles.

### 12.3 MinHash

Calcular Jaccard entre todos os pares teria complexidade quadrática. Com 800 documentos seriam 319.600 pares; com o corpus completo seriam mais de 123 milhões.

MinHash cria assinaturas probabilísticas que aproximam Jaccard. Documentos com conjuntos semelhantes tendem a produzir assinaturas semelhantes.

O notebook usa 128 permutações. Mais permutações tendem a melhorar a aproximação, mas aumentam custo de memória e processamento.

### 12.4 LSH

Locality-Sensitive Hashing agrupa assinaturas de forma que itens semelhantes tenham maior probabilidade de cair nos mesmos buckets. É usado para gerar candidatos, evitando comparar todos contra todos.

No limiar adotado, a amostra não produziu candidatos MinHash nem pares com Jaccard acima de 0,80. Isso não prova que o corpus inteiro não possui quase duplicatas. Significa apenas que a amostra e os parâmetros não detectaram pares com alta sobreposição de shingles.

### 12.5 TF-IDF

TF-IDF pondera termos de acordo com frequência no documento e raridade no corpus:

- TF aumenta com a frequência no documento;
- IDF reduz o peso de unidades presentes em muitos documentos.

Na análise aproximada são usados n-gramas de caracteres de três a cinco caracteres. Esse recurso tolera pequenas variações ortográficas e morfológicas melhor que palavras inteiras.

A matriz é limitada a 15 mil atributos e armazenada em `float32` para reduzir memória.

### 12.6 Similaridade do cosseno

Cada documento é representado por um vetor TF-IDF. A similaridade do cosseno mede o ângulo entre vetores:

`cos(A,B) = (A · B) / (||A|| ||B||)`

Valores próximos de um indicam direção semelhante, independentemente do tamanho absoluto dos vetores.

Foram encontrados dois documentos cujo vizinho mais próximo atingiu similaridade igual ou superior a 0,90. Os pares aparecem de forma direcional: A pode escolher B como vizinho e B escolher A. Portanto, duas linhas podem representar um único par não ordenado.

### 12.7 Por que usar métodos complementares

MinHash/Jaccard medem sobreposição de conjuntos de sequências. TF-IDF/cosseno medem semelhança na distribuição ponderada de unidades. Um par pode ter TF-IDF alto e Jaccard baixo. Isso não é contradição; os métodos capturam aspectos diferentes.

## 13. Inspeção qualitativa

Contagens não explicam a natureza dos casos. Por isso, o notebook mostra trechos e metadados de:

- dez menores documentos;
- dez maiores;
- grupos duplicados;
- resumos de fallback;
- registros com URL ou HTML;
- três registros indisponíveis.

A inspeção revelou, por exemplo, documentos curtos associados a sessões solenes, orientações de bancada e discurso em língua estrangeira. Isso demonstra por que um limiar de tamanho não deve ser usado como regra automática de exclusão.

Os documentos indisponíveis são:

- 486753;
- 486686;
- 486869.

Mostrar somente trechos de até 240 caracteres evita poluir o notebook, mas a investigação definitiva pode consultar o texto completo e a fonte oficial.

## 14. Frequência lexical

### 14.1 CountVectorizer

O `CountVectorizer` transforma documentos em uma matriz documento-termo. Cada célula registra quantas vezes um termo aparece em um documento.

Parâmetros importantes:

- `lowercase=True`: ignora diferenças de caixa;
- `strip_accents='unicode'`: remove marcas de acento;
- `stop_words=STOPWORDS_PT`: remove termos funcionais da visualização;
- `min_df=10`: exige presença em pelo menos dez documentos;
- `max_df=.98`: remove termos presentes em mais de 98% dos documentos;
- token com pelo menos três letras.

`min_df` reduz erros raros e termos muito específicos. `max_df` reduz expressões quase universais e pouco discriminativas.

### 14.2 O que a frequência permite concluir

Ela mostra vocabulário dominante e possíveis fórmulas recorrentes. Não identifica automaticamente temas, intenção, sentimento ou posição política.

Uma palavra frequente pode resultar de linguagem regimental, e não de prioridade substantiva. A interpretação exige contexto.

### 14.3 Bigramas

Bigramas são sequências de duas palavras. Eles preservam mais contexto que unigramas e permitem reconhecer expressões como nomes institucionais ou termos compostos.

Ainda assim, bigramas não equivalem a conceitos. Expressões frequentes podem ser fórmulas de tratamento ou trechos padronizados.

## 15. Mudança lexical com Jensen–Shannon

O notebook agrega as frequências de termos por ano e compara as distribuições usando a distância de Jensen–Shannon.

Ela é baseada na divergência de Kullback–Leibler, mas é simétrica e limitada. Com logaritmo de base 2, varia entre zero e um:

- zero: distribuições idênticas;
- valores maiores: distribuições mais diferentes.

É adicionada uma constante muito pequena às frequências para evitar problemas matemáticos com probabilidade zero.

### Por que aplicar

O vocabulário político pode mudar com pandemia, eleições, alterações econômicas e agenda legislativa. Se períodos tiverem distribuições diferentes, a avaliação do RAG precisa abranger todos eles.

### O que não concluir

A distância não informa quais eventos causaram a mudança, nem se ela é estatisticamente significativa. Também não identifica os termos responsáveis sem análise complementar.

## 16. Simulação de chunking

### 16.1 Por que dividir documentos

Embeddings e modelos possuem limites de contexto. Indexar discursos inteiros dificultaria recuperar apenas o trecho relevante e impediria processar documentos muito longos.

Chunking divide cada documento em unidades menores. Há uma troca:

- chunks pequenos aumentam precisão local, mas podem perder contexto;
- chunks grandes preservam contexto, mas podem misturar assuntos e reduzir precisão.

### 16.2 Estimativa de tokens

O notebook estima tokens como caracteres divididos por quatro. Essa é uma aproximação para planejamento, não uma contagem definitiva.

A tokenização depende do modelo. A implementação deve usar o tokenizador do modelo de embeddings escolhido, especialmente porque português, nomes próprios e sinais regimentais podem produzir proporções diferentes.

### 16.3 Sobreposição

Na configuração principal:

- tamanho: 512 tokens;
- sobreposição: 64 tokens;
- passo efetivo: 448 tokens.

A sobreposição reduz o risco de separar uma informação exatamente na fronteira. Em contrapartida, cria redundância e aumenta o índice.

Uma aproximação do número de chunks é calculada a partir do tamanho, sobreposição e passo, assegurando pelo menos um chunk para documentos não vazios.

### 16.4 Resultados

Com 512 tokens:

- aproximadamente 45.971 chunks no total;
- cerca de 2,92 chunks por registro;
- mediana de dois chunks para textos integrais;
- percentil 95 de nove chunks para textos integrais;
- máximo de 60 chunks;
- resumos de fallback cabem em um chunk.

Comparação:

- 256 tokens: 84.567 chunks;
- 512 tokens: 45.971 chunks;
- 768 tokens: 33.297 chunks;
- 1.024 tokens: 27.130 chunks.

Quanto menor o chunk, maior o número de vetores, o armazenamento, o tempo de embedding e o custo de busca.

### Limitação

A simulação corta por tamanho matemático. A implementação deverá preferir fronteiras semânticas, como parágrafos e sentenças, preservando posição e identificador do documento.

## 17. Cobertura dos metadados

Metadados permitem filtros e melhoram rastreabilidade. Entre os 15.726 documentos indexáveis:

- código, data, autor e tipo de uso têm cobertura de 100%;
- indexação temática tem 99,62%;
- partido e UF têm 86,81%.

### Por que isso importa

Uma consulta pode pedir discursos de determinado período, partido ou UF. Aplicar filtro antes ou durante a recuperação reduz candidatos irrelevantes.

Metadados também permitem construir citações e avaliações estratificadas.

### Cuidado

Ausência de partido e UF não deve causar exclusão automática. Cerca de 13,19% não possuem esses campos, possivelmente porque incluem autores externos ou tipos de participação aos quais o atributo não se aplica.

## 18. Concentração e HHI

O índice Herfindahl–Hirschman é a soma dos quadrados das participações:

`HHI = Σ pᵢ²`

Quanto maior, mais concentrada a distribuição. O valor depende do número e do tamanho relativo das categorias.

Entre valores conhecidos:

- autor: HHI 0,015;
- partido: HHI 0,085;
- UF: HHI 0,046.

A participação dos dez maiores é:

- autores: 30,09%;
- partidos: 83,53%;
- UFs: 54,78%.

O notebook apresenta uma análise principal excluindo ausências e uma análise auxiliar tratando `Não informado` como categoria. Isso evita que a ausência de partido e UF, de 13,19%, seja interpretada como um grupo político ou geográfico real.

HHI descreve concentração documental, não poder político ou viés algorítmico. Ele sinaliza uma condição que pode influenciar a recuperação e precisa ser considerada na avaliação.

## 19. Scorecard de prontidão dos dados

O scorecard reúne indicadores com limiares heurísticos:

- documentos indexáveis: adequado;
- cobertura de texto integral: adequada;
- registros sem conteúdo: adequado;
- cópias exatas excedentes: adequado;
- documentos com menos de 50 palavras: adequado;
- cobertura mínima dos filtros: requer tratamento, por causa dos 86,81% de partido e UF.

### Por que chamar de prontidão e não avaliação do RAG

O quadro avalia propriedades do corpus. Ele não mede se uma pergunta recupera o documento correto nem se uma resposta é fiel.

Os limiares não são padrões universais nem testes estatísticos. São critérios operacionais explícitos, úteis para identificar riscos e decisões pendentes.

### Como defender os limiares

Eles funcionam como regras de triagem, não como certificação. Na dissertação, devem ser descritos como heurísticos definidos para orientar o pipeline e revistos à luz dos experimentos do notebook 02.

## 20. Recomendações derivadas

As análises justificam:

- preservar código, data, autor, partido, UF, fonte e posição em cada chunk;
- distinguir texto integral e resumo;
- não indexar os três registros sem conteúdo;
- segmentar em fronteiras semânticas;
- inspecionar duplicatas antes de removê-las;
- combinar recuperação lexical, vetorial e filtros;
- avaliar por ano, partido, UF, tamanho e fonte do documento;
- medir recuperação e geração separadamente.

Essas recomendações não foram escolhidas arbitrariamente; cada uma responde a um achado da auditoria.

## 21. O que ficará para o notebook 02

O notebook `02-avaliar-recuperacao-rag.ipynb` deverá incluir:

1. conjunto de perguntas estratificado;
2. pronunciamentos relevantes para cada pergunta;
3. chunks efetivamente construídos;
4. comparação de tamanho e sobreposição;
5. BM25, recuperação vetorial e híbrida;
6. Recall@1, Recall@5, Recall@10, MRR e nDCG@k;
7. resultados por estrato;
8. diversidade dos resultados;
9. análise manual de erros;
10. avaliação da geração separada da recuperação.

### Conceitos de avaliação que precisam ser dominados

**Recall@k:** proporção dos documentos relevantes que aparece entre os k primeiros resultados. É importante quando não recuperar uma evidência constitui falha grave.

**Precision@k:** proporção dos k resultados que é relevante. Mede quanto ruído aparece para o usuário ou para o gerador.

**MRR:** média do inverso da posição do primeiro resultado relevante. Premia sistemas que colocam cedo a primeira evidência correta.

**nDCG@k:** considera posição e, quando disponível, graus de relevância. Resultados relevantes nas primeiras posições recebem maior peso.

**Groundedness:** grau em que a resposta é sustentada pelo contexto recuperado.

**Fidelidade:** ausência de afirmações que contradigam ou extrapolem as evidências fornecidas.

**Correção da citação:** correspondência entre a afirmação e o pronunciamento citado.

## 22. Questões difíceis que podem surgir na orientação

### “O corpus está pronto para RAG?”

Está pronto para experimentação, não para afirmar desempenho. A cobertura é alta, há pouca duplicidade exata e os metadados centrais são bons. Entretanto, é necessário definir chunking, embeddings, índice e conjunto de avaliação.

### “Por que usar resumo quando o texto integral não existe?”

Porque o resumo preserva cobertura temática de 687 registros. Ele será marcado como fallback para não ser confundido com evidência integral e poderá receber tratamento ou avaliação específica.

### “Por que não excluir todos os textos curtos?”

Tamanho pequeno não implica erro. A inspeção encontrou conteúdos legítimos, como orientações de bancada e registros de sessões. A exclusão deve depender da utilidade para recuperação e do tipo documental.

### “Por que não deduplicar automaticamente?”

Identificadores diferentes podem representar eventos legislativos distintos, ainda que o texto seja igual. A deduplicação pode eliminar proveniência. Uma alternativa é indexar uma representação canônica mantendo a lista de ocorrências.

### “Por que a análise aproximada usa amostra?”

Comparações par a par crescem quadraticamente. A amostra controla custo e serve como diagnóstico inicial. MinHash e LSH também reduzem o espaço de candidatos. Uma análise exaustiva pode ser executada posteriormente em infraestrutura própria, se os resultados justificarem.

### “Por que usar TF-IDF se o RAG será baseado em embeddings?”

TF-IDF é uma linha de base interpretável e detecta similaridade lexical. Embeddings medem proximidade semântica, mas podem falhar em nomes, números e termos legais. Comparar métodos ajuda a verificar se a complexidade adicional produz ganho.

### “Por que busca híbrida?”

Busca lexical é forte em termos exatos, códigos, nomes e expressões legislativas. Busca vetorial é forte em paráfrases e similaridade semântica. A combinação pode aproveitar as duas propriedades.

### “As diferenças anuais são causadas por eventos políticos?”

O notebook mostra distância lexical, não causalidade. Eventos são hipóteses interpretativas que exigem análise temporal e documental complementar.

### “O scorecard prova que os dados têm qualidade?”

Não. Ele resume indicadores e limiares operacionais. Qualidade é multidimensional e dependente do uso. A prova de adequação ao RAG virá do desempenho de recuperação e da análise de erros.

### “Por que não aplicar stopwords ao índice?”

Porque modelos de embeddings usam contexto natural, e a remoção pode alterar significado e negação. Stopwords foram adotadas apenas para tornar a frequência lexical interpretável.

### “Como evitar vazamento temporal ou de conteúdo?”

A avaliação deve separar perguntas e documentos com cuidado, impedir que a própria pergunta contenha identificadores triviais quando isso não representa o uso real e registrar se a divisão é temporal. Duplicatas ou quase duplicatas precisam permanecer no mesmo lado de uma divisão de treino/teste quando houver aprendizado supervisionado.

## 23. Afirmações que devem ser evitadas

Não afirmar que:

- frequência de discurso mede importância política;
- HHI comprova viés do RAG;
- distância lexical comprova efeito causal de eventos;
- 99,98% de documentos indexáveis implica 99,98% de cobertura das respostas;
- similaridade TF-IDF alta significa equivalência semântica;
- ausência de candidatos MinHash prova ausência de quase duplicatas;
- 512 tokens é a configuração ótima;
- quatro caracteres correspondem exatamente a um token;
- os limiares do scorecard são padrões científicos universais;
- o resumo possui a mesma evidência do discurso integral;
- o notebook já avaliou o RAG.

## 24. Glossário resumido

**Corpus:** conjunto organizado de documentos usados na pesquisa.

**RAG:** arquitetura que recupera documentos antes da geração para fornecer evidência ao modelo.

**Documento indexável:** registro com conteúdo textual suficiente para ingressar no índice.

**Chunk:** segmento de um documento usado como unidade de indexação e recuperação.

**Embedding:** vetor denso que representa características semânticas do texto.

**Busca vetorial:** recuperação baseada em proximidade entre embeddings.

**Busca lexical:** recuperação baseada na ocorrência e ponderação de termos, como BM25.

**Busca híbrida:** combinação de sinais lexicais e vetoriais.

**Top-k:** os k primeiros resultados retornados.

**Metadado:** atributo descritivo usado para identificar, filtrar ou citar um documento.

**Fallback:** alternativa usada quando a fonte preferencial não está disponível.

**Cardinalidade:** quantidade de valores distintos em uma variável.

**Quantil:** ponto que divide uma distribuição segundo determinada proporção.

**Cauda longa:** presença de poucos valores muito maiores que a maioria.

**ECDF:** proporção observada de valores menores ou iguais a um limite.

**N-grama:** sequência contígua de n unidades, como palavras ou caracteres.

**Shingle:** n-grama usado como elemento de conjunto em comparação documental.

**Hash:** resumo determinístico usado para identificar conteúdo binário ou textual.

**MinHash:** assinatura probabilística para aproximar similaridade de Jaccard.

**LSH:** técnica que encontra candidatos semelhantes sem comparar todos os pares.

**TF-IDF:** ponderação que combina frequência local e raridade global.

**Similaridade do cosseno:** medida angular entre vetores.

**Jensen–Shannon:** distância simétrica entre distribuições de probabilidade.

**HHI:** medida de concentração baseada na soma das participações ao quadrado.

## 25. Roteiro curto para apresentação oral

1. **Problema:** um RAG só pode recuperar evidências que estejam disponíveis, bem formadas e identificadas no corpus.
2. **Proveniência:** a base foi fixada na versão v1.1.1 e validada por SHA-256.
3. **Integridade:** são 15.729 registros, 15.729 códigos únicos e nenhuma data inválida.
4. **Cobertura:** 95,61% possuem texto integral; 687 usam resumo e apenas 3 não têm conteúdo.
5. **Distribuição:** o volume varia no tempo e entre autores, partidos e UFs, exigindo avaliação estratificada.
6. **Qualidade textual:** existe cauda longa, 8,21% de documentos curtos e apenas 0,18% de cópias exatas excedentes.
7. **Redundância:** hashes diagnosticam igualdade; MinHash/Jaccard e TF-IDF investigam semelhança aproximada.
8. **Chunking:** 512 tokens produziriam cerca de 45.971 chunks, mas a escolha ótima depende da avaliação do recuperador.
9. **Metadados:** filtros centrais têm boa cobertura, embora partido e UF estejam ausentes em 13,19%.
10. **Conclusão:** o corpus está pronto para experimentação; o notebook 02 medirá recuperação e geração separadamente.

## 26. Síntese final

A principal contribuição do notebook é converter uma coleção de arquivos em um corpus auditado, com limitações explícitas e decisões rastreáveis. A análise não tenta antecipar artificialmente o desempenho do RAG. Ela reduz incertezas sobre os dados e define hipóteses testáveis para o próximo estágio.

Essa separação entre qualidade do corpus, qualidade da recuperação e qualidade da geração demonstra domínio metodológico: cada componente será avaliado com indicadores adequados, evitando conclusões baseadas apenas em exemplos favoráveis ou em métricas desconectadas do problema de pesquisa.
