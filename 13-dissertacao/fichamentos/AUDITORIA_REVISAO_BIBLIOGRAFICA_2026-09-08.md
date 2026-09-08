# Auditoria da revisão bibliográfica

Data: 08/09/2026. Escopo: 53 fichamentos, fontes centrais, citações dos capítulos 2 e 3 e sete referências pendentes do inventário original.

## 1. Fichamentos

A verificação estrutural encontrou 53 fichas compiláveis, todas com contribuição principal, excertos localizados e proposta de aproveitamento. Cinquenta e duas usam explicitamente o campo de limitações; a ficha institucional da IPU usa uma formulação equivalente de riscos/ressalvas. Não foram identificadas fichas sem os quatro conteúdos mínimos.

A revisão de conteúdo foi focal e não substitui a leitura integral pelo pesquisador. As fichas centrais foram conferidas contra os PDFs/extrações locais; as interpretações foram mantidas com ressalvas de transferência e sem converter resultados dos artigos em resultados da dissertação.

## 2. Fontes centrais aprofundadas

| Fonte | Verificação | Ajuste interpretativo
|---|---|
| ARES | método, dimensões, PPI, comparação com RAGAS e limitações | manter como referência para separar relevância de contexto, fidelidade e relevância da resposta; não transferir ganhos diretamente
| RAGAS | versão publicada e ressalvas da ficha | citar como conjunto de métricas, registrando a divergência entre a publicação de 2024 e a chave baseada no preprint
| ConsJudge | introdução, método, tabela de resultados e limitações | usar para justificar calibração do juiz, não como substituto de avaliação humana
| LegalBench-RAG | preprint v1, tabelas e divergência interna de contagens | manter a ressalva sobre a versão e não tratar o benchmark como equivalente ao corpus parlamentar
| Trautmann et al. | corpus de groundedness jurídico, comparação de similaridade/NLI/LLM e macro-F1 | usar como apoio à dimensão de fidelidade contextual; o macro-F1 é resultado das condições do benchmark
| Niu et al. / RAGTruth | anotações de caso e palavra, intensidade e detecção de alucinação | usar como taxonomia operacional de erro, sem presumir equivalência de domínio ou idioma
| Zhang et al. | suporte completo, parcial e ausente; comparação de métricas | usar para exigir verificabilidade graduada, além da mera presença de citação
| Sorodoc et al. / GaRAGe | relevância das passagens, atribuição e deflexão | usar para perguntas não respondíveis e insuficiência documental; resultados são específicos do benchmark
| Reuter et al. | DRM, documentos semelhantes e Summary-Augmented Chunking | medir erro de documento separado de erro de trecho; tratar SAC como hipótese, não como ganho garantido

## 3. Auditoria de citações dos capítulos 2 e 3

As chaves citadas foram conferidas contra `referencias.bib`; não há chave ausente. As afirmações técnicas principais estão apoiadas por fontes primárias ou sínteses explicitamente qualificadas. Foram removidas três citações pendentes que não tinham texto integral verificável: `geunis2023parliamentaryMonitoring`, `deAlmeidaSantos2025aiGovernance` e `matoshiEtAl2025parliamentRag`. As passagens permanecem sustentadas por fontes acessíveis próximas ou foram redigidas como delimitação da dissertação.

Pontos que devem permanecer sob controle editorial: (a) números de versões de RAGAS, HELM, Ji e WFD; (b) contagens divergentes em LegalBench-RAG; (c) resultados de ARES, Trautmann e GaRAGe sempre acompanhados da expressão “nas condições do estudo”; (d) inferências de transferência para o Senado apresentadas como hipóteses de teste.

## 4. Destino das sete referências pendentes

| Chave | Decisão | Justificativa
|---|---|
| `peffersEtAl2007dsrm` | manter como referência metodológica; recuperar PDF antes da versão final | fundamenta DSR, mas a ficha e a conferência textual continuam pendentes
| `geunis2023parliamentaryMonitoring` | não incorporar por ora; retirar citação do capítulo 2 | identidade/versão da página não coincide com a entrada de 2023
| `deAlmeidaSantos2025aiGovernance` | não incorporar por ora; retirar citação do capítulo 2 | metadados disponíveis, texto integral não verificado e argumento já coberto por IPU/WFD
| `matoshiEtAl2025parliamentRag` | manter como candidata contextual; retirar citação do capítulo 2 | acesso restrito e ausência de ficha verificável
| `gil2022projetosPesquisa` | manter apenas como apoio metodológico, pendente de confirmação da 7ª edição | não é fonte da revisão de RAG; recuperar ou substituir antes da redação metodológica final
| `lakatosMarconi2021metodologia` | manter apenas como apoio metodológico, pendente de confirmação da 9ª edição | mesma condição; não afeta a revisão bibliográfica substantiva
| `creswellPlanoClark2018mixedMethods` | manter apenas como apoio metodológico, pendente de confirmação da 3ª edição | mesma condição; substituir se a edição não puder ser conferida

A revisão bibliográfica substantiva pode ser considerada encerrada para o piloto. As quatro referências metodológicas pendentes exigem apenas decisão editorial e confirmação de edição, não nova busca temática.
