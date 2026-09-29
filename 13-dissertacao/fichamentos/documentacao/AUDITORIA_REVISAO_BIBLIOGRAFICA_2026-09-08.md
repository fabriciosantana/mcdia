# Auditoria da revisão bibliográfica

Data: 08/09/2026. Escopo: revisão dos fichamentos, fontes centrais, citações dos capítulos 2 e 3 e consolidação do inventário bibliográfico.

## 1. Fichamentos

A verificação estrutural inicial encontrou 53 fichas compiláveis, todas com contribuição principal, excertos localizados e proposta de aproveitamento. Após a atualização de 29/09/2026, o conjunto passou a 58 fichas. Cinquenta e sete usam explicitamente o campo de limitações; a ficha institucional da IPU usa uma formulação equivalente de riscos/ressalvas. Não foram identificadas fichas sem os quatro conteúdos mínimos.

A revisão de conteúdo foi focal e não substitui a leitura integral pelo pesquisador. As fichas centrais foram conferidas contra os PDFs/extrações locais; as interpretações foram mantidas com ressalvas de transferência e sem converter resultados dos artigos em resultados da dissertação.

## 2. Fontes centrais aprofundadas

| Fonte | Verificação | Ajuste interpretativo
|---|---| --- 
| ARES | método, dimensões, PPI, comparação com RAGAS e limitações | manter como referência para separar relevância de contexto, fidelidade e relevância da resposta; não transferir ganhos diretamente
| RAGAS | versão publicada e ressalvas da ficha | citar como conjunto de métricas, registrando a divergência entre a publicação de 2024 e a chave baseada no preprint
| ConsJudge | introdução, método, tabela de resultados e limitações | usar para justificar calibração do juiz, não como substituto de avaliação humana
| LegalBench-RAG | preprint v1, tabelas e divergência interna de contagens | manter a ressalva sobre a versão e não tratar o benchmark como equivalente ao corpus parlamentar
| Trautmann et al. | corpus de groundedness jurídico, comparação de similaridade/NLI/LLM e macro-F1 | usar como apoio à dimensão de fidelidade contextual; o macro-F1 é resultado das condições do benchmark
| Niu et al. / RAGTruth | anotações de caso e palavra, intensidade e detecção de alucinação | usar como taxonomia operacional de erro, sem presumir equivalência de domínio ou idioma
| Zhang et al. | suporte completo, parcial e ausente; comparação de métricas | usar para exigir verificabilidade graduada, além da mera presença de citação
| Sorodoc et al. / GaRAGe | relevância das passagens, atribuição e deflexão | usar para perguntas não respondíveis e insuficiência documental; resultados são específicos do benchmark
| Reuter et al. | DRM, documentos semelhantes e Summary-Augmented Chunking | medir erro de documento separado de erro de trecho; tratar SAC como hipótese, não como ganho garantido

A rubrica de cinco dimensões foi mantida como síntese operacional da literatura, e não como padrão único já consagrado. A dimensão de insuficiência documental é uma adaptação explícita ao contexto parlamentar, apoiada nas noções de deflexão, abstinência, recusa e prevenção de alucinação presentes nos benchmarks consultados.

## 3. Auditoria de citações dos capítulos 2 e 3

As chaves citadas foram conferidas contra `referencias.bib`; não há chave ausente. As afirmações técnicas principais estão apoiadas por fontes primárias ou sínteses explicitamente qualificadas. As citações dos capítulos foram conferidas após a incorporação das fontes que passaram a ter texto local verificável; não há chaves ausentes. As passagens permanecem sustentadas por fontes acessíveis próximas ou foram redigidas como delimitação da dissertação.

Pontos que devem permanecer sob controle editorial: (a) números de versões de RAGAS, HELM, Ji e WFD; (b) contagens divergentes em LegalBench-RAG; (c) resultados de ARES, Trautmann e GaRAGe sempre acompanhados da expressão “nas condições do estudo”; (d) inferências de transferência para o Senado apresentadas como hipóteses de teste.

## 4. Estado final do corpus bibliográfico

O corpus ativo foi encerrado com 58 referências fichadas. As duas referências sem acesso foram retiradas dos inventários, da bibliografia ativa e do arquivo de obtenção. Não há citações ativas dependentes delas. A versão congelada e seus hashes estão registrados em `fichamentos/documentacao/BIBLIOGRAFIA_CONGELADA_2026-09-29.md`.


## 5. Atualização de 15/09/2026

Em execução do fluxo `ars-lit-review`, foram aprofundadas as nove fontes centrais (ARES, RAGAS, ConsJudge, LegalBench-RAG, Trautmann, RAGTruth, Zhang, GaRAGe e Reuter). Cada ficha recebeu um campo de controle de uso na redação, delimitando a contribuição sustentada e os resultados que não podem ser transferidos diretamente para o corpus parlamentar.

Os capítulos 2 e 3 foram revisados para: (a) apresentar as cinco dimensões avaliativas como síntese operacional da literatura, e não como rubrica canônica; (b) explicitar a adaptação da insuficiência documental ao contexto parlamentar; e (c) separar erro de documento, erro de trecho e erro de afirmação. A dissertação foi recompilada sem erros de LaTeX ou citações indefinidas; permanecem apenas avisos tipográficos preexistentes.

Em 29/09/2026, cinco PDFs foram recebidos, validados por preflight e fichados. Duas entradas sem acesso foram removidas do corpus ativo. A ficha 57 registra que o PDF de Geunis é de 2025, e as fichas 55 e 56 registram as edições efetivamente consultadas de Gil e Lakatos/Marconi.
