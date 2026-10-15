# Recuperação e métricas corretas

## ADDED Requirements

### Requirement: Métricas por pergunta
O sistema SHALL distinguir Recall@k (evidências relevantes distintas recuperadas / evidências relevantes de referência), Hit@k, Precision@k, MRR e nDCG. Graus, ganho, denominador de precisão, tratamento de não julgados e política de duplicação SHALL ser versionados. Ausência de gold SHALL produzir não aplicável com motivo.

#### Scenario: Verificar resultado conhecido
- **WHEN** gold é a,b,c e ranking é a,b,x
- **THEN** Recall@1=1/3, Recall@5=2/3 e Hit@5=1; nDCG fica entre 0 e 1 quando aplicável; perguntas sem evidência não recebem zero artificial

### Requirement: Estratégias explícitas
O sistema SHALL disponibilizar BM25, busca vetorial Chroma e fusão lexical-vetorial configurável, mantendo TF-IDF e o híbrido lexical legado identificados separadamente. Parâmetros efetivos, k e filtros SHALL constar na execução.

#### Scenario: Comparar recuperadores
- **WHEN** a mesma bateria congelada é executada com três estratégias
- **THEN** o híbrido usa listas BM25 e vetorial, o método BM25 não calcula TF-IDF e as estratégias compartilham corpus e referência

### Requirement: Índices Chroma administráveis
O sistema SHALL manter registro SQLite de índice, coleção, versão do corpus/chunks, provedor, modelo, dimensões, distância, parâmetros e estado. Construção em lotes SHALL registrar progresso, falhas e retomada explícita; falha de leitura SHALL NOT apagar coleção automaticamente.

#### Scenario: Retomar indexação incompleta
- **WHEN** uma tarefa falha após persistir um lote
- **THEN** o operador vê o erro e pode retomar apenas itens faltantes; índice incompleto não é selecionável para execução final

### Requirement: Identidade dos vetores
O sistema SHALL associar vetores e resultados por ID, validar contagem/dimensão/valores e consultar a coleção via busca vetorial parametrizada. Alteração do provedor ou dimensão SHALL gerar índice incompatível distinto.

#### Scenario: Retorno fora de ordem
- **WHEN** o armazenamento devolve IDs em ordem diferente da entrada
- **THEN** cada score continua vinculado ao chunk correto; consultas repetidas não regeneram embeddings compatíveis
