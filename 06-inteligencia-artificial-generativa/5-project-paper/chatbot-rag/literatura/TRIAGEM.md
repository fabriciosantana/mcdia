# Triagem de referencias para a issue #3

Esta triagem registra a avaliacao de pertinencia das referencias novas ou ainda nao citadas no texto, com foco na tabela comparativa de trabalhos relacionados.

## Incluidas no manuscrito e na tabela comparativa

| Chave BibTeX | Decisao | Justificativa |
|---|---|---|
| `chouhanGertz2024lexdrafter` | Incluir | RAG aplicado a documentos legislativos da Uniao Europeia; tarefa diferente, mas diretamente relacionada a RAG legislativo. |
| `colombo2024legisAi` | Incluir no texto, fora da tabela | Apoia a contextualizacao de grafos de conhecimento e LLMs para suporte e monitoramento de sistemas legislativos; a tabela preserva `colomboEtAl2025legisSearch` como comparacao mais completa. |
| `colomboEtAl2025legisSearch` | Incluir | Busca em legislacao italiana com grafo, LLM, baseline BM25/TF-IDF e ablacao; referencia forte para comparacao metodologica. |
| `dahlEtAl2024largeLegalFictions` | Incluir no texto, fora da tabela | Forte para calibrar riscos de alucinacao e inferencias nao verificaveis em dominios juridicos; pertinente a limites e governanca, nao a comparacao de sistemas parlamentares. |
| `garrisonEtAl2024talkNdaa` | Incluir | Avalia RAG em legislacao congressional dos EUA; util para comparar avaliacao em corpus legislativo longo. |
| `hevnerEtAl2004designScience` | Incluir no texto, fora da tabela | Base para enquadramento em Design Science Research; pertinente a metodologia, nao a comparacao de sistemas RAG parlamentares. |
| `matoshiEtAl2025parliamentRag` | Incluir | Projetos-piloto com topic modeling e RAG em contexto parlamentar suico; uma das referencias mais proximas ao objetivo do artigo. |
| `mosbachEtAl2025worldAvatarParliament` | Incluir | Sistema RAG hibrido com grafo de conhecimento para debates parlamentares alemaes; muito pertinente para diferenciar corpus e arquitetura. |
| `peffersEtAl2007dsrm` | Incluir no texto, fora da tabela | Base para metodologia DSRM; pertinente ao desenho metodologico do estudo, nao a comparacao de trabalhos relacionados. |
| `pipitoneAlami2024legalbenchRag` | Incluir no texto, fora da tabela | Relevante para reforcar que avaliacao de RAG juridico envolve recuperacao, fidelidade ao contexto e adequacao da evidencia, nao apenas qualidade textual. |
| `rogiersEtAl2024kamerraad` | Incluir | Interface conversacional e recuperacao de informacao em politica parlamentar belga; pertinente para comparacao de acesso parlamentar. |
| `sarnikar2025legislativeTexts` | Incluir | Consulta e compreensao de textos legislativos longos com LLMs; pertinente como trabalho adjacente sobre legislacao extensa. |
| `lewisEtAl2020rag` | Incluir no texto, fora da tabela | Referencia seminal de RAG; deve fundamentar arquitetura, nao a comparacao de dominio parlamentar. |

## Baixa pertinencia direta para o manuscrito atual

| Chave BibTeX | Decisao | Justificativa |
|---|---|---|
| `akbarEtAl2025transportationCybersecurityRag` | Nao citar agora | Usa RAG em lacunas legais de ciberseguranca em transportes. E util como exemplo de RAG em politica/regulacao, mas distante de parlamentos, discursos e legislacao parlamentar. A entrada foi atualizada porque o trabalho passou a artigo publicado. |

## Referencias ja citadas e mantidas na tabela

| Chave BibTeX | Decisao | Justificativa |
|---|---|---|
| `blanco2025plenarioPalanqueEstudio` | Manter | Compartilha o corpus empirico de discursos do Senado; essencial para diferenciar analise descritiva de sistema RAG. |
| `blanco2026letrasGraudas` | Manter | Complementa a caracterizacao computacional dos discursos do Senado. |
| `khaliq2024ragar` | Manter | RAG em dominio politico e fact-checking; pertinente como trabalho adjacente. |
| `martelloteViola2025organizacaoConhecimento` | Manter | Contexto brasileiro de organizacao do conhecimento legislativo; pertinente para aproximar IA e informacao parlamentar. |
