# Chatbot Legislativo com RAG para Respostas Auditáveis sobre Discursos da 56ª Legislatura do Senado Federal

## 1. Introdução

### 1.1 Contextualização

O avanço recente dos grandes modelos de linguagem (Large Language Models, LLMs) ampliou o interesse por soluções capazes de responder perguntas em linguagem natural sobre grandes volumes documentais. No setor público, esse potencial é especialmente relevante em contextos nos quais há acervos extensos, dinâmicos e heterogêneos, como legislação, pareceres, notas técnicas, discursos parlamentares e documentos administrativos. Entretanto, o uso direto de LLMs apresenta limitações conhecidas, como alucinações, desatualização do conhecimento e baixa rastreabilidade das evidências utilizadas para compor uma resposta (Gao et al., 2023).

Nesse cenário, a abordagem Retrieval-Augmented Generation (RAG) surge como uma arquitetura adequada para combinar recuperação semântica de documentos com geração textual fundamentada em fontes externas. Em vez de depender apenas do conhecimento paramétrico do modelo, o sistema recupera trechos relevantes de uma base documental e os incorpora ao contexto da resposta, elevando a precisão factual, a atualidade e a auditabilidade do resultado (Gao et al., 2023). No contexto do Parlamento brasileiro, a organização do conhecimento e a ampliação de mecanismos de acesso à informação já constituem tema relevante de pesquisa aplicada. Cavalcanti (2024) destaca que a inteligência artificial pode apoiar a organização do conhecimento legislativo, desde que utilizada com atenção à estrutura informacional, à mediação documental e à explicabilidade dos resultados. O presente projeto insere-se nesse problema aplicado ao desenvolver um chatbot legislativo baseado em RAG, orientado ao acervo de discursos da 56ª Legislatura do Senado Federal (Cavalcanti, 2024).

### 1.2 Motivação

A administração pública lida com forte pressão por transparência, rastreabilidade e eficiência na gestão da informação. Em ambientes parlamentares, a consulta a discursos e pronunciamentos é importante para análise temática, comparação de posicionamentos, apoio a gabinetes, produção de relatórios e atendimento ao cidadão. Todavia, a busca puramente lexical em grandes bases tende a ser insuficiente quando o usuário formula perguntas complexas, comparativas ou orientadas a síntese.

Além disso, soluções baseadas apenas em LLMs generalistas podem gerar respostas convincentes, porém não verificáveis, o que é particularmente problemático em domínios institucionais que exigem responsabilização e controle sobre as fontes. Deene (s.d.) argumenta que sistemas RAG podem reduzir riscos de governança informacional e conformidade ao deslocar a fonte primária do conhecimento para documentos controlados, atualizáveis e auditáveis (Deene, s.d.). Said (2025), por sua vez, ressalta que, em produção, sistemas RAG exigem não apenas recuperação e geração, mas também versionamento, observabilidade e avaliação contínua para mitigar riscos e garantir qualidade (Said, 2025).

### 1.3 Objetivo

O objetivo deste trabalho é desenvolver e demonstrar uma solução de chatbot legislativo com RAG voltada à consulta de discursos parlamentares da 56ª Legislatura do Senado Federal. Especificamente, busca-se estruturar uma base de conhecimento consultável a partir desses discursos, permitir perguntas em linguagem natural com respostas fundamentadas em trechos recuperados, avaliar empiricamente a qualidade inicial da recuperação e da geração, bem como documentar uma arquitetura reproduzível, com baixo acoplamento e possibilidade de evolução para cenários institucionais (Gao et al., 2023; Said, 2025).

## 2. Fundamentação teórica

### 2.1 Arquiteturas de LLM relacionadas ao problema

As arquiteturas mais relevantes para este projeto são as de LLMs generativos baseados em transformadores e os modelos de embeddings usados para busca vetorial. No primeiro caso, o LLM atua como componente de síntese, recebendo uma pergunta e um conjunto de trechos recuperados para compor uma resposta textual. No segundo, modelos de embedding convertem trechos documentais e consultas em vetores de alta dimensão, permitindo cálculo de similaridade semântica em banco vetorial (Gao et al., 2023).

No contexto de RAG, esses componentes operam de forma complementar: o modelo de embedding suporta a etapa de recuperação, enquanto o modelo generativo suporta a etapa de composição da resposta (Gao et al., 2023). Gao et al. (2023) classificam as arquiteturas RAG em formas ingênuas, avançadas e modulares. Para o problema legislativo abordado neste trabalho, a arquitetura modular revela-se particularmente adequada, pois facilita a substituição independente de extratores, modelos de embedding, banco vetorial, reranqueadores e modelos gerativos, permitindo a evolução incremental do sistema sem reengenharia completa da solução (Gao et al., 2023).

### 2.2 Técnicas relacionadas

As principais técnicas empregadas no projeto incluem extração documental, chunking, embeddings semânticos, recuperação vetorial, reranqueamento e seleção contextual, bem como prompting orientado a evidências (Said, 2025). A extração documental compreende a conversão e preparação do texto para ingestão na base de conhecimento. O chunking corresponde à segmentação dos documentos em unidades menores destinadas à indexação vetorial. Os embeddings semânticos fornecem a representação vetorial de chunks e consultas, enquanto a recuperação vetorial permite a identificação dos trechos mais relevantes. O reranqueamento e a seleção contextual delimitam o subconjunto de contexto enviado ao modelo gerativo. Por fim, o prompting orientado a evidências contempla instruções explícitas para privilegiar o contexto recuperado, limitar inferências especulativas e distribuir citações ao longo da resposta (Said, 2025).

Entre essas técnicas, o chunking assume papel central. Singh (2025) discute que estratégias de segmentação inadequadas podem prejudicar sensivelmente a recuperação ao quebrar o contexto semântico ou, no extremo oposto, ao gerar blocos excessivamente grandes, reduzindo a precisão da busca (Singh, 2025). No presente projeto, o desenvolvimento exigiu ajustes iterativos de chunking para equilibrar qualidade de recuperação e restrições operacionais do banco vetorial em nuvem. A experiência prática corroborou a literatura: o chunking não é uma etapa acessória, mas um dos principais fatores de desempenho de um sistema RAG (Singh, 2025).

Said (2025) acrescenta que, em ambientes reais, técnicas de avaliação, observabilidade e versionamento são tão importantes quanto o pipeline básico de recuperação, sobretudo para detectar regressões, acompanhar mudanças em modelos e dados, e assegurar consistência entre versões do sistema. Essa perspectiva foi incorporada ao projeto por meio de scripts próprios de importação, avaliação e documentação de parâmetros (Said, 2025).

### 2.3 Trabalhos e soluções relacionadas

Gao et al. (2023) oferecem a base conceitual mais abrangente para compreender o RAG como solução para problemas de desatualização, baixa explicabilidade e geração não rastreável em LLMs, orientando a decomposição do problema em etapas de recuperação, aumento de contexto e geração (Gao et al., 2023). No campo jurídico e regulatório, Deene (s.d.) discute o potencial do RAG para reduzir riscos associados ao uso corporativo de IA, especialmente por aumentar o controle sobre fontes, facilitar a atualização e favorecer mecanismos de responsabilização (Deene, s.d.). Embora o texto esteja voltado ao contexto empresarial e de proteção de dados, seus argumentos são aplicáveis ao setor público por analogia institucional.

No domínio político, Khaliq et al. (2024) demonstram que arquiteturas RAG podem apoiar tarefas de fact-checking político com raciocínio apoiado em evidências externas, articulando recuperação rigorosa e geração explicável (Khaliq et al., 2024). Ainda que o foco do presente projeto não seja verificação factual multimodal, o trabalho de Khaliq et al. (2024) mostra que o domínio político-parlamentar é compatível com abordagens RAG e se beneficia de estruturas de recuperação rigorosa. Por fim, Cavalcanti (2024) aproxima a discussão da realidade do Parlamento brasileiro ao tratar da inteligência artificial na organização do conhecimento legislativo, reforçando a pertinência da aplicação de IA explicável e documentalmente ancorada em contextos institucionais (Cavalcanti, 2024).

## 3. Caracterização do problema

### 3.1 Problema da administração pública

O problema central abordado neste trabalho é a dificuldade de transformar grandes acervos parlamentares em bases efetivamente consultáveis por meio de perguntas em linguagem natural, com respostas úteis, verificáveis e contextualizadas. Embora os discursos legislativos sejam públicos, seu volume e diversidade dificultam a recuperação eficiente de argumentos, temas, posicionamentos e referências temporais apenas por mecanismos tradicionais de busca. Na prática, esse quadro impacta gabinetes parlamentares que precisam recuperar rapidamente posicionamentos anteriores, equipes técnicas responsáveis por notas, pareceres e subsídios, pesquisadores e jornalistas que investigam temas legislativos e cidadãos interessados em transparência e controle social.

Na ausência de uma camada semântica de recuperação, a consulta ao acervo tende a ser fragmentada, lenta e dependente de conhecimento prévio sobre a estrutura e o conteúdo da base (Gao et al., 2023; Cavalcanti, 2024). O chatbot legislativo com RAG proposto busca atuar precisamente sobre essa lacuna, adicionando uma camada de mediação que combina busca semântica e geração com evidências.

### 3.2 Partes interessadas

As partes interessadas no projeto abrangem, em primeiro lugar, os gabinetes parlamentares, consultorias legislativas e assessorias técnicas que demandam acesso rápido e qualificado a discursos anteriores. Abrangem também equipes de transparência e gestão da informação, pesquisadores em ciência política, direito e administração pública, bem como cidadãos e organizações da sociedade civil que utilizam o acervo como insumo para controle social. Por fim, incluem-se as equipes de tecnologia responsáveis pela operação e manutenção da solução, que precisam de mecanismos claros de governança, observabilidade e evolução arquitetural (Cavalcanti, 2024; Said, 2025).

### 3.3 Critérios de sucesso

Os critérios de sucesso definidos para o laboratório dizem respeito à capacidade de indexar uma base representativa de discursos parlamentares, à recuperação de trechos relevantes para perguntas factuais e analíticas e à geração de respostas em português baseadas prioritariamente no contexto recuperado. Incluem, adicionalmente, a inclusão de referências e metadados dos discursos utilizados, a possibilidade de importação e avaliação automatizadas e a reprodutibilidade da solução em ambiente local ou containerizado (Said, 2025). Esses critérios dialogam com recomendações da literatura para sistemas RAG em produção, que enfatizam reprodutibilidade, avaliação contínua e rastreabilidade (Gao et al., 2023; Said, 2025).

## 4. Proposta de solução

### 4.1 Arquitetura do chatbot legislativo

A solução proposta materializa-se em um chatbot legislativo que utiliza RAG para responder consultas sobre discursos da 56ª Legislatura do Senado Federal. A arquitetura compreende três serviços principais: uma instância do Open WebUI como interface de interação e orquestração do fluxo de RAG; o Docling para extração e preparação de conteúdo documental; e o ChromaDB como banco vetorial acessado por HTTP. Essa separação de responsabilidades é coerente com a adoção de uma arquitetura modular discutida por Gao et al. (2023).

O ambiente foi definido em arquivo `docker-compose.yaml`, com serviços configurados em `network_mode: host`, de modo a reduzir a complexidade de conectividade local. O sistema foi configurado para operar tanto com embeddings locais, via Ollama, quanto com embeddings providos por serviços externos, como a API da OpenAI, sendo esta segunda opção a utilizada na configuração experimental validada (Gao et al., 2023; Said, 2025). Essa flexibilidade facilita a adaptação da solução a diferentes ambientes institucionais e restrições de infraestrutura.

### 4.2 Pipeline desenvolvido

O pipeline do projeto inicia-se com a aquisição dos dados, baseada no dataset `fabriciosantana/discursos-senado-legislatura-56`, que reúne discursos da 56ª Legislatura do Senado Federal. Na etapa de pré-processamento e seleção textual, prioriza-se o campo `TextoDiscursoIntegral`, com recurso ao `Resumo` e à `Indexacao` quando necessário, garantindo que o conteúdo mais completo e informativo seja privilegiado na construção da base. Em seguida, realiza-se o chunking em nível de palavras, com geração de segmentos que preservam metadados relevantes por chunk, em consonância com a importância da segmentação para o desempenho de sistemas RAG enfatizada por Singh (2025).

A partir desses segmentos, são gerados arquivos de ingestão para o Open WebUI, em lotes markdown estruturados, bem como um arquivo `jsonl` de referência. A importação dos lotes é automatizada por script que realiza o upload, monitora o processamento e assegura a inclusão na knowledge base do Open WebUI. Concluída a ingestão, procede-se à indexação vetorial, em que os embeddings são gerados e persistidos no ChromaDB. A etapa de consulta RAG integra recuperação vetorial, montagem de contexto, aplicação do prompt e geração da resposta pelo modelo, compondo o fluxo de atendimento do chatbot legislativo.

Por fim, a avaliação inicial é realizada por meio de um script (`run_rag_eval.py`) que consulta a knowledge base via API e gera saídas em formatos `.jsonl`, `.md` e `.csv`, permitindo análise estruturada, revisão qualitativa e scoring manual para comparação entre execuções (Said, 2025). O script `build_openwebui_knowledge_from_hf.py` sintetiza a fase de preparação ao gerar chunks com metadados como data, autor, partido, unidade da federação, tipo de uso da palavra, resumo, indexação e URL do texto integral. Essa modelagem favorece tanto a recuperação semântica quanto a geração posterior de respostas auditáveis, com referências documentais claras (Gao et al., 2023; Said, 2025).

### 4.3 Principais contribuições

O projeto contribui para a literatura e para a prática institucional ao construir um ambiente reprodutível de chatbot legislativo com RAG, adaptado a um acervo real do Senado Federal. Demonstra, empiricamente, a importância de uma modelagem de chunk com metadados ricos para fins de auditoria e referência, automatiza a importação em lote e a avaliação básica e valida, em ambiente experimental, a sensibilidade do desempenho às escolhas de chunking e de conectividade com um banco vetorial remoto (Gao et al., 2023; Singh, 2025; Said, 2025). Ao fazê-lo, aproxima as recomendações gerais de RAG em produção da realidade de um acervo legislativo brasileiro.

### 4.4 Riscos e limitações

Os principais riscos e limitações identificados dizem respeito à sensibilidade do desempenho à estratégia de chunking, à possibilidade de mistura excessiva de fontes em perguntas muito abertas e à dependência da qualidade dos documentos e metadados de origem. Há também risco de respostas expansivas ou excessivamente inferenciais quando o prompt não é suficientemente restritivo, bem como dependência de quotas e limites operacionais de serviços externos, tanto para embeddings quanto para o banco vetorial (Singh, 2025; Said, 2025). Deene (s.d.) e Said (2025) contribuem para interpretar esses riscos de forma mais ampla: um sistema RAG melhora o controle e a auditabilidade, mas não elimina automaticamente problemas de qualidade documental, governança, avaliação e conformidade, exigindo processos institucionais de monitoramento e revisão (Deene, s.d.; Said, 2025).

## 5. Experimentos e demonstração

### 5.1 Setup experimental

O experimento utilizou uma base derivada do dataset `fabriciosantana/discursos-senado-legislatura-56`, contendo 15.729 registros de entrada, dos quais 15.726 correspondem a discursos efetivamente escritos e 3 foram descartados por ausência de texto útil. A partir desses registros, foram gerados 23.806 chunks e organizados 120 arquivos markdown de ingestão. Esses números foram registrados em `knowledge_openwebui/build_metadata.json`, de modo a permitir rastreabilidade quantitativa da base construída (Said, 2025).

Na etapa de construção da base, adotaram-se, como parâmetros principais, `max_words = 850`, `overlap_words = 150` e `chunks_per_file = 200`, escolhas que refletem a preocupação em equilibrar granularidade e contexto, em consonância com as recomendações de Singh (2025) sobre estratégias de chunking. Na configuração operacional validada no Open WebUI, definiram-se `Chunk Size = 6000`, `Chunk Overlap = 500` e `Chunk Min Size Target = 2000`, com o `Markdown Header Text Splitter` habilitado, uso do modelo de embedding `text-embedding-3-small` e batch de embeddings de tamanho 32 (Gao et al., 2023).

O prompt de RAG foi evoluído iterativamente para privilegiar o uso prioritário do contexto recuperado, proibir explicitamente a invenção de fatos, exigir declaração quando a informação solicitada não estivesse presente no contexto e incentivar a distribuição de citações ao longo da resposta, incluindo, quando pertinente, uma seção final de referências. Essa configuração busca alinhar a operação do chatbot legislativo com a ênfase em explicabilidade, auditabilidade e governança presente na literatura (Deene, s.d.; Said, 2025).

Para a avaliação, o script `run_rag_eval.py` realiza consultas automatizadas à knowledge base do Open WebUI via API, gerando saídas em `.jsonl` para persistência estruturada, em `.md` para revisão qualitativa e em `.csv` para atribuição de notas e comparação entre execuções (Said, 2025). Esse arranjo aproxima o ambiente do laboratório de práticas de observabilidade e versionamento recomendadas para sistemas RAG em produção.

### 5.2 Resultados alcançados

Os resultados do laboratório foram satisfatórios para uma prova de conceito funcional do chatbot legislativo com RAG. A importação de todos os 120 lotes foi concluída com sucesso e o sistema passou a responder perguntas factuais e temáticas sobre discursos da 56ª Legislatura com qualidade inicial considerada adequada. Observou-se que perguntas específicas e “atômicas” apresentaram desempenho superior em relação a perguntas excessivamente abertas ou multifocais e constatou-se que a inclusão de referências ao final da resposta é viável por meio de instruções apropriadas no prompt (Gao et al., 2023; Said, 2025).

Na avaliação empírica, verificou-se que perguntas sobre dados objetivos e argumentos centrais de um senador tendem a produzir respostas mais precisas, enquanto questões transversais, comparativas e muito abertas elevam o risco de sínteses excessivamente amplas. Ficou evidente que a qualidade percebida depende não apenas do modelo subjacente, mas da combinação entre estratégia de chunking, desenho do prompt e formulação da consulta (Singh, 2025; Said, 2025). Esses achados são coerentes com a literatura. Gao et al. (2023) observam que RAG não é uma técnica única, mas um pipeline cujo desempenho emerge da interação entre recuperação, aumento de contexto e geração (Gao et al., 2023). Said (2025) reforça que avaliação contínua é necessária para detectar regressões e orientar ajustes em ambiente de produção (Said, 2025).

### 5.3 Impacto na administração pública

O impacto potencial do chatbot legislativo com RAG para a administração pública manifesta-se em pelo menos quatro dimensões. Em termos de transparência, as respostas passam a ser ancoradas em discursos públicos e citáveis, facilitando a verificação por terceiros. Em termos de eficiência, há redução do tempo de busca em grandes acervos legislativos, com ganho operacional para gabinetes e equipes técnicas. No que se refere à memória institucional, a recuperação de posicionamentos anteriores, temas recorrentes e evidências documentais torna-se mais rápida e sistemática. Finalmente, quanto ao apoio à decisão, gabinetes e equipes técnicas podem explorar o acervo de forma mais estruturada, usando o chatbot como camada de mediação informacional (Cavalcanti, 2024; Deene, s.d.).

Por operar sobre fontes controladas e com possibilidade de referência explícita aos discursos da 56ª Legislatura, a solução é mais compatível com exigências de accountability do que o uso isolado de um chatbot genérico. Esse ponto dialoga com Deene (s.d.) e Cavalcanti (2024), que destacam a importância da governança das fontes e da mediação documental em contextos institucionais (Cavalcanti, 2024; Deene, s.d.).

## 6. Conclusão e trabalhos futuros

### 6.1 Revisão das contribuições

O trabalho desenvolveu uma solução funcional de chatbot legislativo com RAG voltada ao acervo de discursos da 56ª Legislatura do Senado Federal, composta por um pipeline de preparação documental, um banco vetorial, uma interface de consulta e scripts auxiliares de ingestão e avaliação. O projeto demonstrou que é possível estruturar uma base semântica consultável e responder perguntas em linguagem natural com apoio em evidências recuperadas, alinhando-se à visão de RAG como técnica para aumentar atualidade, explicabilidade e rastreabilidade dos LLMs (Gao et al., 2023).

### 6.2 Discussão e interpretação crítica dos resultados frente aos objetivos

Considerando o objetivo proposto, os resultados podem ser considerados positivos. A solução atendeu aos requisitos mínimos de indexação da base de discursos da 56ª Legislatura, recuperação de trechos relevantes, geração de respostas e automação de testes, em consonância com os critérios de sucesso definidos (Said, 2025). A experiência também evidenciou que a qualidade de um RAG institucional depende de disciplina metodológica: a escolha da estratégia de chunking, o desenho do prompt, a governança de metadados e a avaliação iterativa influenciam diretamente o comportamento final do chatbot (Gao et al., 2023; Singh, 2025).

Essa constatação confirma a literatura recente. RAG não deve ser entendido apenas como “conectar um LLM a um banco vetorial”, mas como um sistema sociotécnico que exige observabilidade, versionamento e critérios claros de sucesso, sobretudo quando utilizado para apoiar funções públicas sensíveis (Said, 2025).

### 6.3 Limitações

As limitações atuais incluem uma avaliação ainda predominantemente qualitativa e manual, a ausência, nesta etapa, de filtros mais sofisticados por autor, período ou tipo de discurso diretamente integrados ao fluxo de geração, a possibilidade de respostas excessivamente amplas em consultas abertas e a dependência de serviços externos para embeddings e parte da geração (Said, 2025). Essas limitações dialogam com alertas da literatura sobre riscos operacionais, viés de dados e necessidade de monitoramento contínuo em sistemas RAG (Gao et al., 2023; Said, 2025).

### 6.4 Próximos passos

Como trabalhos futuros, recomenda-se ampliar a avaliação automática com o uso de frameworks especializados, como RAGAS ou abordagens baseadas em “juiz LLM”, de modo a complementar o julgamento humano com métricas sistemáticas. Sugere-se, ainda, incorporar filtros estruturados por metadado na recuperação, experimentar reranqueadores mais robustos, testar diferentes estratégias de chunking por tipo documental, implementar pós-processamento determinístico para a seção de referências e expandir a solução para outros tipos de documentos legislativos, como pareceres, projetos de lei e notas técnicas. Um passo adicional consiste em evoluir o sistema para cenários de geração assistida de minutas e discursos, preservando rastreabilidade e revisões humanas obrigatórias (Gao et al., 2023; Singh, 2025; Said, 2025).

## Referências

CAVALCANTI, Helen Bento. Inteligência Artificial na Organização do Conhecimento do Parlamento Brasileiro. In: **ISKO Brasil 2024**, Campina Grande. *Anais...* Campina Grande: UFCG, 2024. Disponível em: <https://dspace.sti.ufcg.edu.br/bitstream/riufcg/38144/1/HELEN%20BENTO%20CAVALCANTI-ARTIGO-CI%C3%8ANCIA%20DA%20COMPUTA%C3%87%C3%83O-CEEI%20%282024%29.pdf>. Acesso em: 28 out. 2025.

DEENE, Joris. Can a RAG system reduce the GDPR risks of your enterprise AI? *ICT Lawyer*, s.d. Disponível em: <https://www.ictrechtswijzer.be/en/can-a-rag-system-reduce-the-gdpr-risks-of-your-enterprise-ai/>. Acesso em: 8 abr. 2026.

GAO, Yunfan; XIONG, Yun; GAO, Xinyu; JIA, Kangxiang; PAN, Jinliu; BI, Yuxi; DAI, Yi; SUN, Jiawei; WANG, Meng; WANG, Haofen. Retrieval-augmented generation for large language models: a survey. *arXiv preprint*, arXiv:2312.10997, 2023. Disponível em: <https://arxiv.org/abs/2312.10997>. Acesso em: 28 out. 2025.

KHALIQ, Mohammed Abdul; et al. RAG-Augmented Reasoning for Political Fact-Checking using Multimodal Large Language Models. In: **PROCEEDINGS OF THE SEVENTH FACT EXTRACTION AND VERIFICATION WORKSHOP (FEVER)**, 2024, Miami, Florida, USA. *Proceedings...* Miami: Association for Computational Linguistics, 2024. p. 280-296. DOI: <https://doi.org/10.18653/v1/2024.fever-1.29>. Disponível em: <https://aclanthology.org/2024.fever-1.29/>. Acesso em: 19 nov. 2025.

SAID, Adil. RAG in Practice: Exploring Versioning, Observability, and Evaluation in Production Systems. *Towards AI*, 28 ago. 2025. Disponível em: <https://towardsai.net/p/artificial-intelligence/rag-in-practice-exploring-versioning-observability-and-evaluation-in-production-systems>. Acesso em: 8 abr. 2026.

SINGH, Pankaj. 8 Types of Chunking for RAG Systems. *Analytics Vidhya*, 4 abr. 2025. Disponível em: <https://www.analyticsvidhya.com/blog/2025/02/types-of-chunking-for-rag-systems/>. Acesso em: 8 abr. 2026.