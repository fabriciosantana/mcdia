# Técnicas de avaliação de sistemas RAG Resources

## Knowledge

- [TREC — Relevance Judgements](https://trec.nist.gov/data/reljudge_eng.html)  
  Fonte primária sobre definição de relevância, pooling, qrels e compatibilidade entre corpus e julgamentos.

- [NIST — Common Evaluation Measures](https://trec.nist.gov/pubs/trec10/appendices/measures.pdf)  
  Referência primária para medidas clássicas de listas ranqueadas, incluindo recall e reciprocal rank.

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks — Lewis et al.](https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html)  
  Artigo fundador sobre a arquitetura RAG e a relação entre recuperação e geração. Use para entender o pipeline que será avaliado.
- [ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems](https://aclanthology.org/2024.naacl-long.20/)  
  Framework que separa relevância do contexto, fidelidade e relevância da resposta, com calibração humana. Use para estudar avaliação multidimensional.
- [Ragas: Automated Evaluation of Retrieval Augmented Generation](https://arxiv.org/abs/2309.15217)  
  Apresenta métricas automatizadas para componentes de RAG. Use para distinguir métricas de recuperação e de geração.
- [BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://openreview.net/forum?id=wCu6T5xFjeJ)  
  Benchmark heterogêneo de recuperação. Use para compreender avaliação ranqueada e limites de transferência entre conjuntos.
- [Measuring the Groundedness of Legal Question-Answering Systems](https://aclanthology.org/2024.nllp-1.14/)  
  Benchmark jurídico de groundedness com comparação entre similaridade, NLI e LLMs. Use para estudar fidelidade ao contexto.
- [RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models](https://aclanthology.org/2024.acl-long.585/)  
  Corpus com anotações em nível de caso e palavra. Use para análise fina de alucinações e erros.
- [Towards Fine-Grained Citation Evaluation in Generated Text](https://aclanthology.org/2024.inlg-main.35/)  
  Distingue suporte completo, parcial e ausente de citações. Use para estudar verificabilidade.
- [GaRAGe: A Benchmark with Grounding Annotations for RAG Evaluation](https://aclanthology.org/2025.findings-acl.875/)  
  Avalia grounding relevante e deflexão quando a evidência não basta. Use para perguntas não respondíveis.
- [GroUSE: A Benchmark to Evaluate Evaluators in Grounded Question Answering](https://aclanthology.org/2025.coling-main.304/)  
  Testa calibração e discriminação de juízes automáticos por meio de modos de falha em respostas fundamentadas.

## Wisdom

- Nenhuma comunidade foi definida ainda. A formação começará com fontes acadêmicas e exercícios; uma comunidade poderá ser escolhida quando surgir uma necessidade prática específica.

## Gaps

- Ainda falta selecionar um curso ou capítulo introdutório que trate, em conjunto, métricas de recuperação, avaliação humana e análise de erros em linguagem acessível. As primeiras lições compensarão essa lacuna com sínteses próprias apoiadas nas fontes acima.
