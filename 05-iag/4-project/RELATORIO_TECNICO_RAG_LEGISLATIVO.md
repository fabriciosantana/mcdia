# Chatbot legislativo com RAG para respostas auditáveis sobre discursos da 56ª Legislatura do Senado Federal

## 1 Introdução

### 1.1 Contextualização

O avanço recente dos grandes modelos de linguagem (*large language models* — LLMs) ampliou significativamente o interesse por soluções capazes de responder perguntas em linguagem natural a partir de grandes volumes documentais. No setor público, esse potencial mostra-se particularmente relevante em contextos caracterizados por acervos extensos, dinâmicos e heterogêneos, tais como legislação, pareceres, notas técnicas, discursos parlamentares e documentos administrativos. Nesses ambientes, o desafio não se restringe ao armazenamento da informação, mas abrange, sobretudo, sua recuperação qualificada, contextualizada e verificável.

Apesar de seu potencial, o uso direto de LLMs apresenta limitações amplamente discutidas na literatura, entre as quais se destacam a geração de respostas alucinatórias, a desatualização do conhecimento paramétrico e a baixa rastreabilidade das evidências mobilizadas na produção das respostas (Gao et al., 2023). Tais limitações assumem maior gravidade em contextos institucionais nos quais se exige transparência, verificabilidade, controle das fontes e responsabilização sobre os conteúdos produzidos.

Nesse cenário, a abordagem *retrieval-augmented generation* (RAG) apresenta-se como alternativa tecnicamente promissora. Em vez de depender exclusivamente do conhecimento internalizado no modelo, sistemas RAG recuperam trechos relevantes de uma base documental externa e os incorporam ao contexto da geração. Com isso, tende-se a elevar a precisão factual, a atualidade e a auditabilidade das respostas, ao mesmo tempo em que se favorece a explicitação das fontes que as sustentam (Gao et al., 2023).

No contexto do Parlamento brasileiro, a organização do conhecimento legislativo e a ampliação do acesso qualificado à informação constituem desafios relevantes de pesquisa aplicada. Cavalcanti (2024) observa que o emprego de inteligência artificial nesse domínio deve ser acompanhado de atenção à estrutura informacional, à mediação documental e à explicabilidade dos resultados. É nesse horizonte que se insere o presente trabalho, ao propor o desenvolvimento de um chatbot legislativo baseado em RAG, voltado à consulta de discursos da 56ª Legislatura do Senado Federal.

### 1.2 Motivação

A administração pública contemporânea opera sob crescente pressão por transparência, rastreabilidade, eficiência e capacidade de resposta. No ambiente parlamentar, a consulta a discursos e pronunciamentos mostra-se relevante para diversas finalidades, tais como análise temática, comparação de posicionamentos, apoio técnico a gabinetes, elaboração de relatórios, produção de subsídios e atendimento ao cidadão. Entretanto, a simples disponibilização pública desses documentos não garante, por si só, acesso eficiente ao conteúdo neles contido.

Em grandes acervos discursivos, mecanismos tradicionais de busca, predominantemente baseados em correspondência lexical, tendem a ser insuficientes quando o usuário formula perguntas complexas, comparativas, interpretativas ou orientadas à síntese. Além disso, a recuperação da informação frequentemente depende de conhecimento prévio sobre vocabulário, datas, autores ou a estrutura da base documental. Como consequência, a informação permanece formalmente acessível, mas substantivamente difícil de explorar.

Paralelamente, soluções baseadas exclusivamente em LLMs generalistas podem produzir respostas plausíveis e linguisticamente bem estruturadas, porém desprovidas de fundamentação verificável. Em domínios institucionais, tal comportamento é particularmente problemático, pois compromete a confiança, a governança da informação e a responsabilização sobre o uso da tecnologia. Deene (s.d.) argumenta que sistemas RAG podem mitigar parte desses riscos ao deslocar a base do conhecimento para documentos controlados, atualizáveis e auditáveis. Na mesma direção, Said (2025) enfatiza que, em cenários de produção, sistemas RAG requerem práticas adicionais de versionamento, observabilidade e avaliação contínua, de modo a assegurar qualidade e consistência ao longo do tempo.

Dessa forma, a motivação deste trabalho decorre da necessidade de investigar uma solução tecnicamente viável e institucionalmente adequada para ampliar o acesso qualificado a discursos parlamentares, combinando busca semântica, geração textual e mecanismos de auditabilidade.

### 1.3 Problema de pesquisa

Diante desse contexto, formula-se o seguinte problema de pesquisa: **como estruturar uma solução baseada em RAG capaz de permitir a consulta, em linguagem natural, a discursos da 56ª Legislatura do Senado Federal, produzindo respostas úteis, fundamentadas em evidências recuperadas e compatíveis com exigências de auditabilidade em contexto institucional?**

A formulação desse problema decorre da percepção de que o acesso documental, embora formalmente assegurado, ainda enfrenta limitações relevantes quando se exige recuperação semântica, síntese orientada ao usuário e rastreabilidade das fontes utilizadas na resposta.

### 1.4 Objetivos

O objetivo geral deste trabalho consiste em desenvolver e demonstrar uma solução de chatbot legislativo baseada em RAG para consulta a discursos parlamentares da 56ª Legislatura do Senado Federal.

Como objetivos específicos, pretende-se:

- estruturar uma base de conhecimento consultável a partir dos discursos parlamentares;
- possibilitar a formulação de perguntas em linguagem natural com respostas fundamentadas em trechos recuperados;
- avaliar empiricamente a qualidade inicial dos processos de recuperação e geração;
- documentar uma arquitetura reprodutível, modular e passível de evolução para cenários institucionais.

### 1.5 Justificativa

A relevância deste estudo decorre de sua contribuição em dois planos complementares. No plano prático, a pesquisa investiga uma forma de ampliar o acesso qualificado a informações parlamentares públicas, contribuindo para transparência, memória institucional e apoio a atividades de gabinete, pesquisa e controle social. No plano teórico-aplicado, o trabalho examina a aplicação de técnicas contemporâneas de recuperação e geração em um domínio documental complexo, marcado por exigências elevadas de explicabilidade, governança e rastreabilidade.

Além disso, o estudo se justifica pela aderência do problema a desafios concretos da administração pública digital. Em vez de tratar a inteligência artificial como mecanismo autônomo de produção de respostas, propõe-se abordagem em que a geração textual é condicionada por fontes documentais públicas, controláveis e auditáveis. Essa orientação é coerente com demandas institucionais por uso responsável de IA em contextos sensíveis.

### 1.6 Estrutura do capítulo

Este capítulo encontra-se organizado da seguinte forma. Inicialmente, apresenta-se a fundamentação teórica, com ênfase nas arquiteturas de LLM e nas técnicas relacionadas a sistemas RAG. Em seguida, procede-se à caracterização do problema, à identificação das partes interessadas e à definição dos critérios de sucesso. Na sequência, descreve-se a proposta de solução, incluindo arquitetura, pipeline, contribuições e limitações. Posteriormente, são apresentados os experimentos conduzidos e os resultados alcançados. Por fim, expõem-se as conclusões do trabalho, suas limitações e os desdobramentos futuros.

---

## 2 Fundamentação teórica

### 2.1 Arquiteturas de LLM relacionadas ao problema

As arquiteturas mais diretamente relacionadas a este projeto são, de um lado, os LLMs generativos baseados em transformadores e, de outro, os modelos de *embeddings* utilizados para recuperação semântica. No primeiro caso, o LLM atua como componente de síntese textual, recebendo uma pergunta e um conjunto de trechos recuperados para compor uma resposta. No segundo, modelos de *embedding* convertem documentos e consultas em vetores em espaço de alta dimensionalidade, tornando possível o cálculo de similaridade semântica em bancos vetoriais (Gao et al., 2023).

Em sistemas RAG, tais componentes operam de maneira complementar. O modelo de *embedding* sustenta a etapa de recuperação, enquanto o modelo generativo realiza a etapa de composição da resposta a partir do contexto recuperado. Essa separação funcional é relevante porque favorece modularidade arquitetural e especialização de componentes, o que, por sua vez, amplia a capacidade de evolução incremental da solução.

Segundo Gao et al. (2023), sistemas RAG podem ser classificados em abordagens ingênuas, avançadas e modulares. Para o problema investigado neste trabalho, a arquitetura modular mostra-se especialmente adequada, pois permite substituir, de forma relativamente independente, extratores documentais, estratégias de segmentação, modelos de *embedding*, bancos vetoriais, reranqueadores e modelos gerativos. Em contextos institucionais, essa característica é particularmente desejável, uma vez que restrições de infraestrutura, custos operacionais, requisitos de segurança e políticas de governança podem demandar alterações graduais da pilha tecnológica.

### 2.2 Técnicas relacionadas

As principais técnicas mobilizadas neste projeto incluem extração documental, *chunking*, geração de *embeddings* semânticos, recuperação vetorial, reranqueamento, seleção contextual e *prompting* orientado a evidências (Said, 2025). A extração documental corresponde à conversão e preparação do texto para ingestão na base de conhecimento. O *chunking* refere-se à segmentação dos documentos em unidades menores, adequadas à indexação vetorial e ao uso posterior como contexto de geração. Os *embeddings* semânticos representam vetorialmente documentos e consultas, enquanto a recuperação vetorial identifica os trechos semanticamente mais relevantes. O reranqueamento e a seleção contextual, por sua vez, delimitam o subconjunto de trechos efetivamente enviado ao modelo generativo. Por fim, o *prompting* orientado a evidências consiste na formulação de instruções explícitas para que o modelo privilegie o contexto recuperado, evite inferências especulativas e apresente referências de modo transparente.

Dentre essas técnicas, o *chunking* ocupa posição central. Singh (2025) argumenta que estratégias inadequadas de segmentação podem comprometer significativamente a recuperação semântica, seja por fragmentarem indevidamente o contexto, seja por gerarem blocos excessivamente extensos, com perda de precisão na busca. No presente projeto, a segmentação documental exigiu sucessivos ajustes empíricos para equilibrar granularidade semântica, preservação de contexto e restrições operacionais do banco vetorial e da camada de ingestão. Assim, a experiência prática corrobora a literatura ao indicar que o *chunking* não constitui etapa meramente operacional, mas um dos principais determinantes do desempenho de um sistema RAG.

Além disso, Said (2025) destaca que, em ambientes reais, a qualidade de um sistema RAG depende não apenas do pipeline básico de recuperação e geração, mas também de mecanismos de observabilidade, versionamento e avaliação. Tais mecanismos mostram-se essenciais para detectar regressões, acompanhar mudanças em modelos e parâmetros e manter consistência entre diferentes versões do sistema. Essa perspectiva foi incorporada ao projeto por meio da criação de scripts próprios de preparação, importação, avaliação e documentação dos principais parâmetros experimentais.

### 2.3 Trabalhos e soluções relacionadas

Gao et al. (2023) oferecem a base conceitual mais abrangente para compreender o RAG como resposta aos problemas de desatualização, baixa explicabilidade e geração não rastreável em LLMs. Seu trabalho orienta a decomposição do problema em etapas de recuperação, aumento de contexto e geração, fornecendo referencial teórico para o desenho da solução adotada neste estudo.

No campo jurídico e regulatório, Deene (s.d.) discute o potencial de sistemas RAG para reduzir riscos associados ao uso corporativo de inteligência artificial, sobretudo por ampliar o controle sobre as fontes, facilitar atualizações documentais e favorecer mecanismos de responsabilização. Embora o enfoque do autor esteja voltado ao contexto empresarial e à proteção de dados, seus argumentos são aplicáveis, por analogia, ao setor público, no qual a governança da informação também ocupa posição central.

No domínio político, Khaliq et al. (2024) demonstram que arquiteturas RAG podem apoiar tarefas de *fact-checking* político com raciocínio fundamentado em evidências externas, articulando recuperação rigorosa e geração explicável. Ainda que o objetivo deste trabalho não seja a verificação factual multimodal, a pesquisa desses autores é relevante por demonstrar a aderência do domínio político-parlamentar a abordagens baseadas em recuperação e geração com evidências.

Por fim, Cavalcanti (2024) aproxima a discussão do contexto brasileiro ao tratar da inteligência artificial na organização do conhecimento legislativo. Sua contribuição reforça a pertinência de soluções explicáveis, documentalmente ancoradas e informacionalmente estruturadas em ambientes parlamentares, oferecendo base teórica específica para a aplicação proposta neste trabalho.

### 2.4 Síntese da revisão e lacuna de pesquisa

A revisão realizada permite identificar convergência entre diferentes autores quanto ao potencial do RAG para elevar a precisão factual, a auditabilidade e a governança de sistemas baseados em LLM. Verifica-se, entretanto, que parte significativa da literatura permanece concentrada em discussões conceituais amplas, cenários corporativos ou aplicações em domínios distintos do acervo legislativo brasileiro. Nesse sentido, observa-se lacuna aplicada relacionada à construção, documentação e avaliação de soluções RAG voltadas especificamente à consulta de discursos parlamentares no contexto do Senado Federal.

Assim, este trabalho busca contribuir para o preenchimento dessa lacuna ao propor, implementar e avaliar uma solução reprodutível de chatbot legislativo baseada em RAG, com foco em discursos da 56ª Legislatura e atenção explícita a exigências de rastreabilidade, explicabilidade e utilidade institucional.

---

## 3 Caracterização do problema

### 3.1 Problema da administração pública

O problema central abordado neste trabalho consiste na dificuldade de transformar grandes acervos parlamentares em bases efetivamente consultáveis por meio de perguntas em linguagem natural, com respostas úteis, contextualizadas e verificáveis. Embora os discursos legislativos sejam públicos, seu volume, diversidade temática e dispersão temporal tornam a recuperação de argumentos, posicionamentos, temas recorrentes e referências históricas uma tarefa complexa quando realizada por mecanismos tradicionais de busca.

Na prática, esse quadro impacta diferentes atores institucionais. Gabinetes parlamentares podem necessitar recuperar rapidamente posicionamentos anteriores sobre determinado tema; equipes técnicas precisam localizar subsídios para notas, relatórios e pareceres; pesquisadores e jornalistas demandam acesso qualificado a discursos para fins analíticos; e cidadãos interessados em transparência e controle social podem se beneficiar de instrumentos que tornem o acervo mais acessível e inteligível. Na ausência de uma camada semântica de recuperação, o acesso ao conteúdo tende a ser fragmentado, lento e altamente dependente de conhecimento prévio sobre a estrutura documental e os termos empregados nos discursos (Gao et al., 2023; Cavalcanti, 2024).

Desse modo, o chatbot legislativo com RAG proposto neste trabalho procura atuar precisamente sobre essa lacuna, acrescentando uma camada de mediação informacional que combina recuperação semântica, contextualização documental e geração textual baseada em evidências.

### 3.2 Partes interessadas

As partes interessadas no projeto abrangem, em primeiro lugar, gabinetes parlamentares, consultorias legislativas e assessorias técnicas, que demandam acesso rápido e qualificado a discursos e posicionamentos anteriores. Incluem-se, também, equipes de transparência, gestão da informação e tecnologia, para as quais são particularmente relevantes aspectos de governança, manutenção, rastreabilidade e evolução da solução.

Além disso, pesquisadores das áreas de ciência política, direito, administração pública e ciência da informação constituem público potencial do sistema, assim como cidadãos e organizações da sociedade civil interessados em controle social e acompanhamento da atividade parlamentar (Cavalcanti, 2024; Said, 2025).

### 3.3 Critérios de sucesso

Os critérios de sucesso definidos para este laboratório incluem: a capacidade de indexar uma base representativa de discursos parlamentares; a recuperação de trechos relevantes para perguntas factuais e analíticas; a geração de respostas em português fundamentadas prioritariamente no contexto recuperado; a apresentação de referências e metadados associados aos discursos utilizados; a automatização das etapas de importação e avaliação; e a reprodutibilidade da solução em ambiente local ou containerizado (Said, 2025).

Tais critérios dialogam com recomendações da literatura para sistemas RAG em produção, que enfatizam avaliação contínua, reprodutibilidade e rastreabilidade como propriedades desejáveis em soluções voltadas a informação institucionalmente relevante (Gao et al., 2023; Said, 2025).

---

## 4 Proposta de solução

### 4.1 Arquitetura do chatbot legislativo

A solução proposta materializa-se em um chatbot legislativo que utiliza a abordagem RAG para responder a consultas sobre discursos da 56ª Legislatura do Senado Federal. A arquitetura compreende três serviços principais: uma instância do Open WebUI, utilizada como interface de interação e orquestração do fluxo de RAG; o Docling, empregado na extração e preparação de conteúdo documental; e o ChromaDB, utilizado como banco vetorial acessado por HTTP.

Essa separação de responsabilidades mostra-se coerente com a adoção de arquitetura modular, na medida em que favorece o isolamento de funções, a substituição de componentes e a evolução incremental do sistema. Em termos práticos, tal modularidade é importante porque permite testar combinações distintas de modelos, parâmetros e serviços sem exigir reconstrução integral da solução.

O ambiente foi definido em arquivo `docker-compose.yaml`, com serviços configurados em `network_mode: host`, com o objetivo de reduzir a complexidade de conectividade em ambiente local. O sistema foi preparado para operar tanto com *embeddings* locais, via Ollama, quanto com *embeddings* providos por serviços externos, como a API da OpenAI. Na configuração experimental validada, adotou-se esta segunda opção. Essa flexibilidade amplia a adaptabilidade da solução a diferentes restrições institucionais de infraestrutura, custo ou política tecnológica.

### 4.2 Pipeline desenvolvido

O pipeline do projeto inicia-se com a aquisição dos dados, baseada no *dataset* `fabriciosantana/discursos-senado-legislatura-56`, que reúne discursos da 56ª Legislatura do Senado Federal. Na etapa de pré-processamento e seleção textual, priorizou-se o campo `TextoDiscursoIntegral`, recorrendo-se aos campos `Resumo` e `Indexacao` quando necessário, de modo a privilegiar o conteúdo mais completo e informativo na construção da base.

Em seguida, realizou-se o *chunking* em nível de palavras, com geração de segmentos que preservam metadados relevantes por *chunk*. Esses metadados incluem data, autor, partido, unidade da federação, tipo de uso da palavra, resumo, indexação e URL do texto integral. Tal modelagem favorece não apenas a recuperação semântica, mas também a auditabilidade das respostas, uma vez que permite reconstituir a origem documental dos trechos utilizados.

A partir desses segmentos, foram gerados arquivos de ingestão para o Open WebUI em lotes estruturados em formato Markdown, além de um arquivo `jsonl` de referência. A importação dos lotes foi automatizada por script responsável por realizar o *upload*, monitorar o processamento e garantir a inclusão dos conteúdos na *knowledge base* do Open WebUI. Concluída a ingestão, procedeu-se à indexação vetorial, com geração e persistência dos *embeddings* no ChromaDB.

Na etapa de consulta, o fluxo RAG integra recuperação vetorial, montagem de contexto, aplicação de *prompt* e geração da resposta pelo modelo. Por fim, a avaliação inicial foi realizada por meio do script `run_rag_eval.py`, que consulta a *knowledge base* via API e produz saídas nos formatos `.jsonl`, `.md` e `.csv`, viabilizando análise estruturada, revisão qualitativa e pontuação manual para comparação entre execuções (Said, 2025).

### 4.3 Principais contribuições

O projeto apresenta contribuições em dois níveis complementares: técnico e institucional. No plano técnico, constrói-se um ambiente reprodutível de chatbot legislativo com RAG adaptado a um acervo real do Senado Federal; demonstra-se a importância de uma modelagem de *chunks* enriquecida por metadados; automatizam-se etapas de importação, ingestão e avaliação; e evidencia-se empiricamente a sensibilidade do desempenho às escolhas de segmentação e conectividade com banco vetorial remoto.

No plano institucional, a solução demonstra a viabilidade de aplicar técnicas contemporâneas de recuperação e geração ao contexto do Parlamento brasileiro, aproximando recomendações gerais da literatura de RAG em produção da realidade de um acervo legislativo público. Desse modo, contribui-se para a discussão sobre governança, auditabilidade e uso responsável de inteligência artificial em contextos parlamentares.

### 4.4 Riscos e limitações

Os principais riscos e limitações identificados relacionam-se à sensibilidade do desempenho à estratégia de *chunking*, à possibilidade de combinação excessiva de fontes em perguntas muito abertas, à dependência da qualidade dos documentos e metadados de origem e ao risco de respostas excessivamente amplas ou inferenciais quando o *prompt* não é suficientemente restritivo. Há, ainda, dependência operacional de serviços externos, tanto para geração de *embeddings* quanto para parte da geração de respostas.

Esses riscos devem ser compreendidos em perspectiva ampliada. Como observam Deene (s.d.) e Said (2025), sistemas RAG podem melhorar controle e auditabilidade, mas não eliminam automaticamente problemas de qualidade documental, governança de dados, conformidade, monitoramento ou avaliação. Em outras palavras, o RAG reduz determinadas fragilidades do uso puro de LLMs, mas não substitui a necessidade de processos institucionais de revisão e controle.

---

## 5 Experimentos e demonstração

### 5.1 Setup experimental

O experimento utilizou uma base derivada do *dataset* `fabriciosantana/discursos-senado-legislatura-56`, contendo 15.729 registros de entrada, dos quais 15.726 correspondiam a discursos efetivamente escritos e 3 foram descartados por ausência de texto útil. A partir desses registros, foram gerados 23.806 *chunks*, organizados em 120 arquivos Markdown de ingestão. Esses números foram registrados em `knowledge_openwebui/build_metadata.json`, permitindo rastreabilidade quantitativa da base construída.

Na etapa de preparação da base, adotaram-se como parâmetros principais `max_words = 850`, `overlap_words = 150` e `chunks_per_file = 200`, buscando equilibrar granularidade e preservação de contexto. Já na configuração operacional validada no Open WebUI, foram definidos `Chunk Size = 6000`, `Chunk Overlap = 500` e `Chunk Min Size Target = 2000`, com o `Markdown Header Text Splitter` habilitado, uso do modelo de *embedding* `text-embedding-3-small` e lote de *embeddings* de tamanho 32.

O *prompt* de RAG foi evoluído iterativamente para atender a requisitos centrais do problema institucional: privilegiar o uso prioritário do contexto recuperado, proibir explicitamente a invenção de fatos, exigir declaração de insuficiência quando a informação solicitada não estivesse presente no contexto e incentivar a distribuição de citações ao longo da resposta, complementada, quando pertinente, por uma seção final de referências. Tal configuração alinha-se à literatura que enfatiza explicabilidade, auditabilidade e governança em sistemas RAG (Deene, s.d.; Said, 2025).

Para a avaliação, o script `run_rag_eval.py` realizou consultas automatizadas à *knowledge base* do Open WebUI via API, gerando saídas em `.jsonl`, `.md` e `.csv`. Esse arranjo permitiu persistência estruturada, revisão qualitativa e comparação manual entre execuções, aproximando o ambiente experimental de práticas de observabilidade e versionamento recomendadas para sistemas RAG em produção.

### 5.2 Resultados alcançados

Os resultados obtidos mostraram-se satisfatórios para uma prova de conceito funcional de chatbot legislativo com RAG. A importação dos 120 lotes foi concluída com sucesso, e o sistema passou a responder perguntas factuais e temáticas sobre discursos da 56ª Legislatura com qualidade inicial considerada adequada. Observou-se que perguntas específicas, delimitadas e mais atômicas apresentaram desempenho superior em comparação com perguntas muito abertas, multifocais ou excessivamente interpretativas.

A avaliação empírica também indicou que perguntas voltadas a dados objetivos ou argumentos centrais de um senador tendem a produzir respostas mais precisas, enquanto questões transversais, comparativas ou amplas elevam o risco de sínteses genéricas ou de combinação excessiva de contextos distintos. Esses achados reforçam a compreensão de que o desempenho de um sistema RAG emerge da interação entre diferentes componentes do pipeline, em especial segmentação, recuperação, seleção contextual, formulação da consulta e desenho do *prompt* (Gao et al., 2023; Singh, 2025; Said, 2025).

Verificou-se, ainda, que a inclusão de referências documentais ao final da resposta é viável por meio de instruções adequadas no *prompt*, o que representa ganho relevante em termos de auditabilidade. Em síntese, os resultados indicam que a solução cumpre adequadamente a função de prova de conceito, ao demonstrar viabilidade técnica, coerência arquitetural e utilidade inicial para consultas sobre o acervo discursivo analisado.

### 5.3 Impacto na administração pública

O impacto potencial do chatbot legislativo com RAG na administração pública pode ser analisado em pelo menos quatro dimensões. Em primeiro lugar, há impacto sobre a transparência, na medida em que as respostas passam a ser ancoradas em discursos públicos e citáveis, facilitando a verificação por terceiros. Em segundo lugar, há ganho de eficiência, uma vez que o sistema reduz o tempo necessário para localizar informações relevantes em grandes acervos documentais. Em terceiro lugar, a solução fortalece a memória institucional, ao facilitar a recuperação de posicionamentos anteriores, temas recorrentes e evidências documentais. Por fim, observa-se potencial de apoio à decisão, na medida em que gabinetes e equipes técnicas passam a dispor de camada adicional de mediação informacional para explorar o acervo legislativo de forma mais estruturada (Cavalcanti, 2024; Deene, s.d.).

Por operar sobre fontes controladas e permitir referência explícita aos discursos da 56ª Legislatura, a solução mostra-se mais compatível com exigências de *accountability* do que o uso isolado de um chatbot generalista. Essa característica assume especial relevância em contextos públicos, nos quais a confiabilidade da informação não pode ser dissociada da governança das fontes e da possibilidade de auditoria posterior.

---

## 6 Conclusão e trabalhos futuros

### 6.1 Síntese das contribuições

O trabalho desenvolveu uma solução funcional de chatbot legislativo com RAG voltada ao acervo de discursos da 56ª Legislatura do Senado Federal. A solução compreende um pipeline de preparação documental, uma base vetorial, uma interface de consulta e scripts auxiliares de ingestão e avaliação. Demonstrou-se, assim, que é possível estruturar uma base semântica consultável e responder perguntas em linguagem natural com apoio em evidências recuperadas, aproximando o uso de LLMs das exigências de atualidade, explicabilidade e rastreabilidade apontadas pela literatura (Gao et al., 2023).

### 6.2 Discussão dos resultados frente aos objetivos

À luz dos objetivos propostos, os resultados podem ser considerados positivos. A solução atendeu aos requisitos mínimos de indexação da base de discursos da 56ª Legislatura, recuperação de trechos relevantes, geração de respostas fundamentadas e automação básica da avaliação. Mais do que isso, a experiência evidenciou que a qualidade de um sistema RAG institucional depende de disciplina metodológica e de decisões arquiteturais consistentes. Estratégias de *chunking*, desenho do *prompt*, governança de metadados e avaliação iterativa influenciam diretamente o comportamento do chatbot.

Tal constatação confirma a literatura recente, segundo a qual RAG não deve ser entendido apenas como a conexão entre um LLM e um banco vetorial, mas como sistema sociotécnico que exige observabilidade, versionamento e critérios explícitos de sucesso, especialmente quando utilizado em funções públicas sensíveis (Said, 2025). Nesse sentido, a principal contribuição do trabalho não reside apenas na implementação do protótipo, mas também na explicitação das escolhas técnicas, limitações práticas e requisitos de governança envolvidos em sua construção.

### 6.3 Limitações

Entre as limitações atuais da solução, destacam-se a avaliação ainda predominantemente qualitativa e manual; a ausência, nesta etapa, de filtros mais sofisticados por autor, período ou tipo de discurso diretamente integrados ao fluxo de geração; a possibilidade de respostas excessivamente amplas em consultas abertas; e a dependência de serviços externos para *embeddings* e parte da geração. Tais limitações dialogam com alertas da literatura acerca de riscos operacionais, vieses de dados e necessidade de monitoramento contínuo em sistemas RAG (Gao et al., 2023; Said, 2025).

### 6.4 Trabalhos futuros

Como trabalhos futuros, recomenda-se ampliar a avaliação automática por meio de *frameworks* especializados, como RAGAS, ou de abordagens baseadas em “juiz LLM”, de modo a complementar a avaliação humana com métricas sistemáticas. Sugere-se, também, incorporar filtros estruturados por metadado na etapa de recuperação, experimentar reranqueadores mais robustos, testar diferentes estratégias de *chunking* por tipo documental e implementar pós-processamento determinístico para a seção de referências.

Além disso, a solução pode ser expandida para outros tipos de documentos legislativos, como pareceres, projetos de lei, notas técnicas e documentos administrativos relacionados ao processo legislativo. Em perspectiva mais avançada, um desdobramento possível consiste na evolução do sistema para cenários de geração assistida de minutas, relatórios ou discursos, desde que preservados mecanismos de rastreabilidade, supervisão humana obrigatória e controles institucionais adequados. Dessa forma, o presente trabalho abre caminho para agenda mais ampla de pesquisa e desenvolvimento sobre inteligência artificial generativa auditável no contexto do Parlamento brasileiro.

---

## Referências

CAVALCANTI, Helen Bento. Inteligência artificial na organização do conhecimento do Parlamento brasileiro. In: ISKO BRASIL 2024, Campina Grande. Anais [...]. Campina Grande: UFCG, 2024. Disponível em: https://dspace.sti.ufcg.edu.br/bitstream/riufcg/38144/1/HELEN%20BENTO%20CAVALCANTI-ARTIGO-CI%C3%8ANCIA%20DA%20COMPUTA%C3%87%C3%83O-CEEI%20%282024%29.pdf. Acesso em: 28 out. 2025.

DEENE, Joris. Can a RAG system reduce the GDPR risks of your enterprise AI? ICT Lawyer, [s. l.], s.d. Disponível em: https://www.ictrechtswijzer.be/en/can-a-rag-system-reduce-the-gdpr-risks-of-your-enterprise-ai/. Acesso em: 8 abr. 2026.

GAO, Yunfan et al. Retrieval-augmented generation for large language models: a survey. arXiv preprint, arXiv:2312.10997, 2023. Disponível em: https://arxiv.org/abs/2312.10997. Acesso em: 28 out. 2025.

KHALIQ, Mohammed Abdul et al. RAG-augmented reasoning for political fact-checking using multimodal large language models. In: PROCEEDINGS OF THE SEVENTH FACT EXTRACTION AND VERIFICATION WORKSHOP (FEVER), 2024, Miami, Florida, USA. Proceedings [...]. Miami: Association for Computational Linguistics, 2024. p. 280-296. DOI: https://doi.org/10.18653/v1/2024.fever-1.29. Disponível em: https://aclanthology.org/2024.fever-1.29/. Acesso em: 19 nov. 2025.

SAID, Adil. RAG in practice: exploring versioning, observability, and evaluation in production systems. Towards AI, [s. l.], 28 ago. 2025. Disponível em: https://towardsai.net/p/artificial-intelligence/rag-in-practice-exploring-versioning-observability-and-evaluation-in-production-systems. Acesso em: 8 abr. 2026.

SINGH, Pankaj. 8 types of chunking for RAG systems. Analytics Vidhya, [s. l.], 4 abr. 2025. Disponível em: https://www.analyticsvidhya.com/blog/2025/02/types-of-chunking-for-rag-systems/. Acesso em: 8 abr. 2026.