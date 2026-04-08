# Chatbot Legislativo com RAG para Respostas Auditáveis sobre Discursos da 56ª Legislatura do Senado Federal

## 1. Introdução

### 1.1 Contextualização

O avanço recente dos grandes modelos de linguagem (*Large Language Models* — LLMs) ampliou significativamente o interesse por soluções capazes de responder perguntas em linguagem natural a partir de grandes volumes documentais. No setor público, esse potencial é particularmente relevante em contextos marcados por acervos extensos, dinâmicos e heterogêneos, como legislação, pareceres, notas técnicas, discursos parlamentares e documentos administrativos. Nesses ambientes, o desafio não consiste apenas em armazenar informação, mas em viabilizar sua recuperação qualificada, contextualizada e verificável.

Apesar de seu potencial, o uso direto de LLMs apresenta limitações amplamente discutidas na literatura, entre as quais se destacam a geração de respostas alucinatórias, a desatualização do conhecimento paramétrico e a baixa rastreabilidade das evidências mobilizadas pelo modelo (GAO et al., 2023). Tais limitações se tornam especialmente críticas em ambientes institucionais que exigem transparência, verificabilidade, controle das fontes e responsabilização sobre os conteúdos produzidos.

Nesse contexto, a abordagem *Retrieval-Augmented Generation* (RAG) se apresenta como alternativa tecnicamente promissora. Em vez de depender exclusivamente do conhecimento internalizado no modelo, sistemas RAG recuperam trechos relevantes de uma base documental externa e os inserem no contexto da geração da resposta. Essa arquitetura tende a elevar a precisão factual, a atualidade e a auditabilidade dos resultados, ao mesmo tempo em que favorece a explicitação das fontes que sustentam a resposta gerada (GAO et al., 2023).

No Parlamento brasileiro, a organização do conhecimento legislativo e a ampliação do acesso qualificado à informação constituem desafios relevantes de pesquisa aplicada. Cavalcanti (2024) observa que a inteligência artificial pode apoiar a organização do conhecimento no contexto parlamentar, desde que sua adoção seja acompanhada de atenção à estrutura informacional, à mediação documental e à explicabilidade dos resultados. É nesse horizonte que se insere o presente trabalho, ao propor o desenvolvimento de um chatbot legislativo baseado em RAG, voltado à consulta de discursos da 56ª Legislatura do Senado Federal.

### 1.2 Motivação

A administração pública contemporânea opera sob crescente pressão por transparência, rastreabilidade, eficiência e capacidade de resposta. No ambiente parlamentar, a consulta a discursos e pronunciamentos é relevante para diferentes finalidades, como análise temática, comparação de posicionamentos, apoio técnico a gabinetes, elaboração de relatórios, produção de subsídios e atendimento ao cidadão. Entretanto, a simples disponibilização pública dos documentos não garante, por si só, acesso eficiente ao conteúdo neles contido.

Em grandes acervos discursivos, mecanismos tradicionais de busca, predominantemente baseados em correspondência lexical, tendem a ser insuficientes quando o usuário formula perguntas complexas, comparativas, interpretativas ou orientadas à síntese. Esse problema se agrava quando a recuperação da informação depende de conhecimento prévio sobre vocabulário, datas, autores ou a estrutura da base documental. Em consequência, a informação pública permanece formalmente acessível, mas substantivamente difícil de explorar.

Além disso, soluções baseadas exclusivamente em LLMs generalistas podem produzir respostas plausíveis e linguisticamente bem estruturadas, porém desprovidas de fundamentação verificável. Em domínios institucionais, esse tipo de comportamento é especialmente problemático, pois compromete a confiança, a governança da informação e a responsabilização sobre o uso da tecnologia. Deene (s.d.) argumenta que sistemas RAG podem mitigar parte desses riscos ao deslocar a base do conhecimento de documentos controlados, atualizáveis e auditáveis. Said (2025), por sua vez, enfatiza que, em cenários de produção, sistemas RAG exigem práticas adicionais de versionamento, observabilidade e avaliação contínua para assegurar qualidade e consistência ao longo do tempo.

Dessa forma, a motivação deste trabalho decorre da necessidade de investigar uma solução tecnicamente viável e institucionalmente adequada para ampliar o acesso qualificado a discursos parlamentares, combinando busca semântica, geração textual e mecanismos de auditabilidade.

### 1.3 Objetivo

O objetivo geral deste trabalho é desenvolver e demonstrar uma solução de chatbot legislativo baseada em RAG para consulta a discursos parlamentares da 56ª Legislatura do Senado Federal.

Como objetivos específicos, busca-se:

- estruturar uma base de conhecimento consultável a partir dos discursos parlamentares;
- permitir a formulação de perguntas em linguagem natural com respostas fundamentadas em trechos recuperados;
- avaliar empiricamente a qualidade inicial dos processos de recuperação e geração;
- documentar uma arquitetura reprodutível, modular e passível de evolução para cenários institucionais.

Ao perseguir esses objetivos, o trabalho procura contribuir para a aplicação prática de técnicas de RAG em contextos públicos, com ênfase em transparência, rastreabilidade, governança da informação e reprodutibilidade técnica.

---

## 2. Fundamentação teórica

### 2.1 Arquiteturas de LLM relacionadas ao problema

As arquiteturas mais diretamente relacionadas a este projeto são, de um lado, os LLMs generativos baseados em transformadores e, de outro, os modelos de *embeddings* utilizados para recuperação semântica. No primeiro caso, o LLM atua como componente de síntese textual, recebendo uma pergunta e um conjunto de trechos recuperados para compor uma resposta. No segundo, modelos de *embedding* convertem documentos e consultas em vetores em espaço de alta dimensionalidade, possibilitando o cálculo de similaridade semântica em bancos vetoriais (GAO et al., 2023).

Em sistemas RAG, esses componentes operam de modo complementar. O modelo de *embedding* sustenta a etapa de recuperação, enquanto o modelo generativo executa a etapa de composição da resposta a partir do contexto recuperado. Essa separação funcional é relevante porque permite modularidade arquitetural e especialização de componentes, favorecendo tanto a escalabilidade quanto a evolução incremental da solução.

Gao et al. (2023) classificam os sistemas RAG em abordagens ingênuas, avançadas e modulares. Para o problema investigado neste trabalho, a arquitetura modular mostra-se especialmente adequada, pois permite substituir, de forma relativamente independente, extratores documentais, estratégias de segmentação, modelos de *embedding*, bancos vetoriais, reranqueadores e modelos gerativos. Essa característica é particularmente desejável em contextos institucionais, nos quais restrições de infraestrutura, requisitos de segurança, custos operacionais e políticas de governança podem demandar alterações graduais na pilha tecnológica sem reengenharia completa do sistema.

### 2.2 Técnicas relacionadas

As principais técnicas mobilizadas no projeto incluem extração documental, *chunking*, geração de *embeddings* semânticos, recuperação vetorial, reranqueamento, seleção contextual e *prompting* orientado a evidências (SAID, 2025). A extração documental corresponde à conversão e preparação do texto para ingestão na base de conhecimento. O *chunking* refere-se à segmentação dos documentos em unidades menores, adequadas à indexação vetorial e ao posterior uso como contexto na geração. Os *embeddings* semânticos representam vetorialmente documentos e consultas, enquanto a recuperação vetorial identifica os trechos mais semanticamente relevantes. O reranqueamento e a seleção contextual delimitam o subconjunto de trechos a ser efetivamente enviado ao modelo generativo. Por fim, o *prompting* orientado a evidências consiste na formulação de instruções explícitas para que o modelo privilegie o contexto recuperado, evite inferências especulativas e apresente referências de modo transparente.

Dentre essas técnicas, o *chunking* ocupa posição central. Singh (2025) argumenta que estratégias inadequadas de segmentação podem comprometer significativamente a recuperação semântica, seja por fragmentar indevidamente o contexto, seja por gerar blocos excessivamente extensos, reduzindo a precisão da busca. No presente projeto, a segmentação documental exigiu sucessivos ajustes empíricos para equilibrar granularidade semântica, preservação de contexto e restrições operacionais do banco vetorial e da camada de ingestão. Essa experiência prática confirma a literatura ao indicar que o *chunking* não constitui etapa meramente operacional, mas um dos principais determinantes do desempenho de um sistema RAG.

Além disso, Said (2025) destaca que, em ambientes reais, a qualidade de um sistema RAG depende não apenas do pipeline básico de recuperação e geração, mas também de mecanismos de observabilidade, versionamento e avaliação. Tais mecanismos são fundamentais para detectar regressões, acompanhar os efeitos de mudanças em modelos e parâmetros e manter consistência entre diferentes versões do sistema. Essa perspectiva foi incorporada ao projeto por meio da criação de scripts próprios de preparação, importação, avaliação e documentação dos principais parâmetros experimentais.

### 2.3 Trabalhos e soluções relacionadas

Gao et al. (2023) oferecem a base conceitual mais abrangente para compreender o RAG como resposta aos problemas de desatualização, baixa explicabilidade e geração não rastreável em LLMs. Seu trabalho orienta a decomposição do problema em etapas de recuperação, aumento de contexto e geração, fornecendo referencial teórico para o desenho da solução adotada neste estudo.

No campo jurídico e regulatório, Deene (s.d.) discute o potencial de sistemas RAG para reduzir riscos associados ao uso corporativo de inteligência artificial, sobretudo por ampliar o controle sobre as fontes, facilitar atualizações documentais e favorecer mecanismos de responsabilização. Embora o enfoque do autor esteja voltado ao contexto empresarial e à proteção de dados, seus argumentos são aplicáveis, por analogia, ao setor público, em que a governança da informação é igualmente central.

No domínio político, Khaliq et al. (2024) demonstram que arquiteturas RAG podem apoiar tarefas de *fact-checking* político com raciocínio fundamentado em evidências externas, articulando recuperação rigorosa e geração explicável. Ainda que o objetivo deste trabalho não seja a verificação factual multimodal, a pesquisa desses autores é relevante por demonstrar a aderência do domínio político-parlamentar a abordagens baseadas em recuperação e geração com evidências.

Por fim, Cavalcanti (2024) aproxima a discussão do contexto brasileiro ao tratar da inteligência artificial na organização do conhecimento legislativo. Sua contribuição reforça a pertinência de soluções explicáveis, documentalmente ancoradas e informacionalmente estruturadas em ambientes parlamentares, oferecendo base teórica específica para a aplicação proposta neste trabalho.

---

## 3. Caracterização do problema

### 3.1 Problema da administração pública

O problema central abordado neste trabalho consiste na dificuldade de transformar grandes acervos parlamentares em bases efetivamente consultáveis por meio de perguntas em linguagem natural, com respostas úteis, contextualizadas e verificáveis. Embora os discursos legislativos sejam públicos, seu volume, diversidade temática e dispersão temporal tornam a recuperação de argumentos, posicionamentos, temas recorrentes e referências históricas uma tarefa complexa quando realizada por meio de mecanismos tradicionais de busca.

Na prática, esse quadro impacta diferentes atores institucionais. Gabinetes parlamentares podem necessitar recuperar rapidamente posicionamentos anteriores sobre determinado tema; equipes técnicas precisam localizar subsídios para notas, relatórios e pareceres; pesquisadores e jornalistas demandam acesso qualificado a discursos para fins analíticos; e cidadãos interessados em transparência e controle social podem se beneficiar de instrumentos que tornem o acervo mais acessível e inteligível. Sem uma camada semântica de recuperação, o acesso ao conteúdo tende a ser fragmentado, lento e altamente dependente de conhecimento prévio sobre a estrutura documental e os termos exatos empregados nos discursos (GAO et al., 2023; CAVALCANTI, 2024).

O chatbot legislativo com RAG proposto neste trabalho procura atuar justamente sobre essa lacuna, acrescentando uma camada de mediação informacional que combina recuperação semântica, contextualização documental e geração textual baseada em evidências.

### 3.2 Partes interessadas

As partes interessadas no projeto abrangem, em primeiro lugar, gabinetes parlamentares, consultorias legislativas e assessorias técnicas, que demandam acesso rápido e qualificado a discursos e posicionamentos anteriores. Incluem-se também equipes de transparência, gestão da informação e tecnologia, para as quais são relevantes aspectos de governança, manutenção, rastreabilidade e evolução da solução. Além disso, pesquisadores das áreas de ciência política, direito, administração pública e ciência da informação constituem público potencial do sistema, bem como cidadãos e organizações da sociedade civil interessados em controle social e acompanhamento da atividade parlamentar (CAVALCANTI, 2024; SAID, 2025).

### 3.3 Critérios de sucesso

Os critérios de sucesso definidos para o laboratório incluem: a capacidade de indexar uma base representativa de discursos parlamentares; a recuperação de trechos relevantes para perguntas factuais e analíticas; a geração de respostas em português fundamentadas prioritariamente no contexto recuperado; a apresentação de referências e metadados associados aos discursos utilizados; a automatização das etapas de importação e avaliação; e a reprodutibilidade da solução em ambiente local ou containerizado (SAID, 2025).

Tais critérios dialogam com recomendações da literatura para sistemas RAG em produção, que enfatizam avaliação contínua, reprodutibilidade e rastreabilidade como propriedades desejáveis em soluções que lidam com informação sensível ou institucionalmente relevante (GAO et al., 2023; SAID, 2025).

---

## 4. Proposta de solução

### 4.1 Arquitetura do chatbot legislativo

A solução proposta materializa-se em um chatbot legislativo que utiliza a abordagem RAG para responder a consultas sobre discursos da 56ª Legislatura do Senado Federal. A arquitetura compreende três serviços principais: uma instância do Open WebUI, utilizada como interface de interação e orquestração do fluxo de RAG; o Docling, empregado na extração e preparação de conteúdo documental; e o ChromaDB, utilizado como banco vetorial acessado por HTTP.

Essa separação de responsabilidades é coerente com a adoção de uma arquitetura modular, na medida em que favorece o isolamento de funções, a substituição de componentes e a evolução incremental do sistema. Em termos práticos, essa modularidade é importante porque permite testar combinações distintas de modelos, parâmetros e serviços sem exigir reconstrução integral da solução.

O ambiente foi definido em arquivo `docker-compose.yaml`, com serviços configurados em `network_mode: host`, buscando reduzir a complexidade de conectividade em ambiente local. O sistema foi preparado para operar tanto com *embeddings* locais, via Ollama, quanto com *embeddings* providos por serviços externos, como a API da OpenAI. Na configuração experimental validada, adotou-se esta segunda opção. Essa flexibilidade amplia a adaptabilidade da solução a diferentes restrições institucionais de infraestrutura, custo ou política tecnológica.

### 4.2 Pipeline desenvolvido

O pipeline do projeto inicia-se com a aquisição dos dados, baseada no *dataset* `fabriciosantana/discursos-senado-legislatura-56`, que reúne discursos da 56ª Legislatura do Senado Federal. Na etapa de pré-processamento e seleção textual, priorizou-se o campo `TextoDiscursoIntegral`, recorrendo-se aos campos `Resumo` e `Indexacao` quando necessário, de forma a privilegiar o conteúdo mais completo e informativo na construção da base.

Em seguida, realizou-se o *chunking* em nível de palavras, com geração de segmentos que preservam metadados relevantes por *chunk*. Esses metadados incluem data, autor, partido, unidade da federação, tipo de uso da palavra, resumo, indexação e URL do texto integral. Essa modelagem favorece não apenas a recuperação semântica, mas também a auditabilidade das respostas, uma vez que permite reconstituir a origem documental dos trechos utilizados.

A partir desses segmentos, foram gerados arquivos de ingestão para o Open WebUI em lotes estruturados em formato Markdown, além de um arquivo `jsonl` de referência. A importação dos lotes foi automatizada por script responsável por realizar o *upload*, monitorar o processamento e garantir a inclusão dos conteúdos na *knowledge base* do Open WebUI. Concluída a ingestão, procedeu-se à indexação vetorial, com geração e persistência dos *embeddings* no ChromaDB.

Na etapa de consulta, o fluxo RAG integra recuperação vetorial, montagem de contexto, aplicação de *prompt* e geração da resposta pelo modelo. Por fim, a avaliação inicial foi realizada por meio do script `run_rag_eval.py`, que consulta a *knowledge base* via API e produz saídas nos formatos `.jsonl`, `.md` e `.csv`, viabilizando análise estruturada, revisão qualitativa e pontuação manual para comparação entre execuções. Esse arranjo aproxima o ambiente experimental de práticas de observabilidade e avaliação recomendadas para sistemas RAG em cenários reais de uso (SAID, 2025).

### 4.3 Principais contribuições

O projeto apresenta contribuições em dois níveis complementares: técnico e institucional. No plano técnico, constrói um ambiente reprodutível de chatbot legislativo com RAG adaptado a um acervo real do Senado Federal; demonstra a importância de uma modelagem de *chunks* enriquecida por metadados; automatiza etapas de importação, ingestão e avaliação; e evidencia empiricamente a sensibilidade do desempenho às escolhas de segmentação e conectividade com banco vetorial remoto.

No plano institucional, a solução demonstra a viabilidade de aplicar técnicas contemporâneas de recuperação e geração ao contexto do Parlamento brasileiro, aproximando recomendações gerais da literatura de RAG em produção da realidade de um acervo legislativo público. Ao fazê-lo, contribui para a discussão sobre governança, auditabilidade e uso responsável de IA em contextos parlamentares.

### 4.4 Riscos e limitações

Os principais riscos e limitações identificados relacionam-se à sensibilidade do desempenho à estratégia de *chunking*, à possibilidade de combinação excessiva de fontes em perguntas muito abertas, à dependência da qualidade dos documentos e metadados de origem e ao risco de respostas excessivamente amplas ou inferenciais quando o *prompt* não é suficientemente restritivo. Há, ainda, dependência operacional de serviços externos, tanto para geração de *embeddings* quanto para parte da geração de respostas.

Esses riscos devem ser compreendidos em chave ampliada. Como observam Deene (s.d.) e Said (2025), sistemas RAG podem melhorar controle e auditabilidade, mas não eliminam automaticamente problemas de qualidade documental, governança de dados, conformidade, monitoramento ou avaliação. Em outras palavras, o RAG reduz determinadas fragilidades do uso puro de LLMs, mas não substitui a necessidade de processos institucionais de revisão e controle.

---

## 5. Experimentos e demonstração

### 5.1 Setup experimental

O experimento utilizou uma base derivada do *dataset* `fabriciosantana/discursos-senado-legislatura-56`, contendo 15.729 registros de entrada, dos quais 15.726 correspondiam a discursos efetivamente escritos e 3 foram descartados por ausência de texto útil. A partir desses registros, foram gerados 23.806 *chunks*, organizados em 120 arquivos Markdown de ingestão. Esses números foram registrados em `knowledge_openwebui/build_metadata.json`, permitindo rastreabilidade quantitativa da base construída.

Na etapa de preparação da base, adotaram-se como parâmetros principais `max_words = 850`, `overlap_words = 150` e `chunks_per_file = 200`, buscando equilibrar granularidade e preservação de contexto. Já na configuração operacional validada no Open WebUI, foram definidos `Chunk Size = 6000`, `Chunk Overlap = 500` e `Chunk Min Size Target = 2000`, com o `Markdown Header Text Splitter` habilitado, uso do modelo de *embedding* `text-embedding-3-small` e lote de *embeddings* de tamanho 32.

O *prompt* de RAG foi evoluído iterativamente para atender a requisitos centrais do problema institucional: privilegiar o uso prioritário do contexto recuperado, proibir explicitamente a invenção de fatos, exigir declaração de insuficiência quando a informação solicitada não estivesse presente no contexto e incentivar a distribuição de citações ao longo da resposta, complementada, quando pertinente, por uma seção final de referências. Essa configuração se alinha à literatura que enfatiza explicabilidade, auditabilidade e governança em sistemas RAG (DEENE, s.d.; SAID, 2025).

Para a avaliação, o script `run_rag_eval.py` realizou consultas automatizadas à *knowledge base* do Open WebUI via API, gerando saídas em `.jsonl`, `.md` e `.csv`. Tal arranjo permitiu persistência estruturada, revisão qualitativa e comparação manual entre execuções, aproximando o ambiente experimental de práticas de observabilidade e versionamento recomendadas para sistemas RAG em produção.

### 5.2 Resultados alcançados

Os resultados obtidos foram satisfatórios para uma prova de conceito funcional de chatbot legislativo com RAG. A importação dos 120 lotes foi concluída com sucesso, e o sistema passou a responder perguntas factuais e temáticas sobre discursos da 56ª Legislatura com qualidade inicial considerada adequada. Observou-se que perguntas específicas, delimitadas e mais “atômicas” apresentaram desempenho superior em comparação com perguntas muito abertas, multifocais ou excessivamente interpretativas.

A avaliação empírica também indicou que perguntas voltadas a dados objetivos ou argumentos centrais de um senador tendem a produzir respostas mais precisas, enquanto questões transversais, comparativas ou amplas elevam o risco de sínteses genéricas ou de combinação excessiva de contextos distintos. Esses achados reforçam a compreensão de que o desempenho de um sistema RAG emerge da interação entre diferentes componentes do pipeline — em especial, segmentação, recuperação, seleção contextual, formulação da consulta e desenho do *prompt* (GAO et al., 2023; SINGH, 2025; SAID, 2025).

Ficou evidente, ainda, que a inclusão de referências documentais ao final da resposta é viável por meio de instruções adequadas no *prompt*, o que representa ganho relevante em termos de auditabilidade. Em síntese, os resultados indicam que a solução cumpre adequadamente a função de prova de conceito, ao demonstrar viabilidade técnica, coerência arquitetural e utilidade inicial para consultas sobre o acervo discursivo analisado.

### 5.3 Impacto na administração pública

O impacto potencial do chatbot legislativo com RAG na administração pública pode ser analisado em pelo menos quatro dimensões. Em primeiro lugar, há impacto sobre a transparência, na medida em que as respostas passam a ser ancoradas em discursos públicos e citáveis, facilitando a verificação por terceiros. Em segundo lugar, há ganho de eficiência, uma vez que o sistema reduz o tempo necessário para localizar informações relevantes em grandes acervos documentais. Em terceiro lugar, a solução fortalece a memória institucional, ao facilitar a recuperação de posicionamentos anteriores, temas recorrentes e evidências documentais. Por fim, há potencial de apoio à decisão, na medida em que gabinetes e equipes técnicas passam a dispor de camada adicional de mediação informacional para explorar o acervo legislativo de forma mais estruturada (CAVALCANTI, 2024; DEENE, s.d.).

Por operar sobre fontes controladas e permitir referência explícita aos discursos da 56ª Legislatura, a solução mostra-se mais compatível com exigências de *accountability* do que o uso isolado de um chatbot generalista. Essa característica é particularmente importante em contextos públicos, nos quais a confiabilidade da informação não pode ser dissociada da governança das fontes e da possibilidade de auditoria posterior.

---

## 6. Conclusão e trabalhos futuros

### 6.1 Revisão das contribuições

O trabalho desenvolveu uma solução funcional de chatbot legislativo com RAG voltada ao acervo de discursos da 56ª Legislatura do Senado Federal. A solução compreende um pipeline de preparação documental, uma base vetorial, uma interface de consulta e scripts auxiliares de ingestão e avaliação. O projeto demonstrou que é possível estruturar uma base semântica consultável e responder perguntas em linguagem natural com apoio em evidências recuperadas, aproximando o uso de LLMs das exigências de atualidade, explicabilidade e rastreabilidade apontadas pela literatura (GAO et al., 2023).

### 6.2 Discussão e interpretação crítica dos resultados frente aos objetivos

À luz dos objetivos propostos, os resultados podem ser considerados positivos. A solução atendeu aos requisitos mínimos de indexação da base de discursos da 56ª Legislatura, recuperação de trechos relevantes, geração de respostas fundamentadas e automação básica da avaliação. Mais do que isso, a experiência evidenciou que a qualidade de um sistema RAG institucional depende de disciplina metodológica e de decisões arquiteturais consistentes. Estratégias de *chunking*, desenho do *prompt*, governança de metadados e avaliação iterativa influenciam diretamente o comportamento do chatbot.

Essa constatação confirma a literatura recente, segundo a qual RAG não deve ser entendido apenas como a conexão entre um LLM e um banco vetorial, mas como um sistema sociotécnico que exige observabilidade, versionamento e critérios explícitos de sucesso, especialmente quando utilizado em funções públicas sensíveis (SAID, 2025). Nesse sentido, a principal contribuição do trabalho não reside apenas na implementação do protótipo, mas também na explicitação das escolhas técnicas, limitações práticas e requisitos de governança envolvidos em sua construção.

### 6.3 Limitações

Entre as limitações atuais da solução, destacam-se a avaliação ainda predominantemente qualitativa e manual; a ausência, nesta etapa, de filtros mais sofisticados por autor, período ou tipo de discurso diretamente integrados ao fluxo de geração; a possibilidade de respostas excessivamente amplas em consultas abertas; e a dependência de serviços externos para *embeddings* e parte da geração. Tais limitações dialogam com alertas da literatura acerca de riscos operacionais, vieses de dados e necessidade de monitoramento contínuo em sistemas RAG (GAO et al., 2023; SAID, 2025).

### 6.4 Próximos passos

Como trabalhos futuros, recomenda-se ampliar a avaliação automática por meio de *frameworks* especializados, como RAGAS, ou abordagens baseadas em “juiz LLM”, de modo a complementar a avaliação humana com métricas sistemáticas. Sugere-se também incorporar filtros estruturados por metadado na etapa de recuperação, experimentar reranqueadores mais robustos, testar diferentes estratégias de *chunking* por tipo documental e implementar pós-processamento determinístico para a seção de referências.

Além disso, a solução pode ser expandida para outros tipos de documentos legislativos, como pareceres, projetos de lei, notas técnicas e documentos administrativos relacionados ao processo legislativo. Em perspectiva mais avançada, um desdobramento possível consiste na evolução do sistema para cenários de geração assistida de minutas, relatórios ou discursos, desde que preservados mecanismos de rastreabilidade, supervisão humana obrigatória e controles institucionais adequados. Dessa forma, o presente trabalho abre caminho para uma agenda mais ampla de pesquisa e desenvolvimento sobre IA generativa auditável no contexto do Parlamento brasileiro.

---

## Referências

CAVALCANTI, Helen Bento. Inteligência Artificial na Organização do Conhecimento do Parlamento Brasileiro. In: **ISKO Brasil 2024**, Campina Grande. *Anais...* Campina Grande: UFCG, 2024. Disponível em: <https://dspace.sti.ufcg.edu.br/bitstream/riufcg/38144/1/HELEN%20BENTO%20CAVALCANTI-ARTIGO-CI%C3%8ANCIA%20DA%20COMPUTA%C3%87%C3%83O-CEEI%20%282024%29.pdf>. Acesso em: 28 out. 2025.

DEENE, Joris. Can a RAG system reduce the GDPR risks of your enterprise AI? *ICT Lawyer*, s.d. Disponível em: <https://www.ictrechtswijzer.be/en/can-a-rag-system-reduce-the-gdpr-risks-of-your-enterprise-ai/>. Acesso em: 8 abr. 2026.

GAO, Yunfan; XIONG, Yun; GAO, Xinyu; JIA, Kangxiang; PAN, Jinliu; BI, Yuxi; DAI, Yi; SUN, Jiawei; WANG, Meng; WANG, Haofen. Retrieval-augmented generation for large language models: a survey. *arXiv preprint*, arXiv:2312.10997, 2023. Disponível em: <https://arxiv.org/abs/2312.10997>. Acesso em: 28 out. 2025.

KHALIQ, Mohammed Abdul et al. RAG-Augmented Reasoning for Political Fact-Checking using Multimodal Large Language Models. In: **PROCEEDINGS OF THE SEVENTH FACT EXTRACTION AND VERIFICATION WORKSHOP (FEVER)**, 2024, Miami, Florida, USA. *Proceedings...* Miami: Association for Computational Linguistics, 2024. p. 280-296. DOI: <https://doi.org/10.18653/v1/2024.fever-1.29>. Disponível em: <https://aclanthology.org/2024.fever-1.29/>. Acesso em: 19 nov. 2025.

SAID, Adil. RAG in Practice: Exploring Versioning, Observability, and Evaluation in Production Systems. *Towards AI*, 28 ago. 2025. Disponível em: <https://towardsai.net/p/artificial-intelligence/rag-in-practice-exploring-versioning-observability-and-evaluation-in-production-systems>. Acesso em: 8 abr. 2026.

SINGH, Pankaj. 8 Types of Chunking for RAG Systems. *Analytics Vidhya*, 4 abr. 2025. Disponível em: <https://www.analyticsvidhya.com/blog/2025/02/types-of-chunking-for-rag-systems/>. Acesso em: 8 abr. 2026.