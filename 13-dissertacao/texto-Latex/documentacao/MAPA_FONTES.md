# Mapa de proveniência e reaproveitamento

| Material de origem | Papel na dissertação | Destino inicial | Cuidado editorial |
|---|---|---|---|
| `../revisao-pre-projeto/fabricio-santana-tecnicas-avaliacao-rag_REV-PITA.pdf` | Anotações da revisão do pré-projeto pelo orientador | Capítulos portados do pré-projeto e elementos pré-textuais correspondentes | Aplicar as intervenções identificáveis de modo rastreável, preservando o desenho da dissertação e distinguindo sugestões editoriais de mudanças metodológicas |
| `chatbot-rag-pre/sections/01-introducao.tex` | Problema, pergunta, justificativa e objetivos | Capítulo 1 | Atualizar linguagem prospectiva somente quando houver evidência final |
| `chatbot-rag-pre/sections/02-referencial-teorico.tex` | Fundamentos e lacuna | Capítulos 2 e 3 | Separar referencial conceitual de comparação crítica dos trabalhos |
| `chatbot-rag-pre/sections/03-hipoteses.tex` | Hipóteses do estudo | Seção autônoma, com conteúdo integral do pré-projeto e revisão ortográfica indicada pelo orientador; discussão posterior no capítulo de discussão | Não tratar como teste causal clássico; qualquer reorganização ou reescrita exige decisão editorial explícita |
| `chatbot-rag-pre/sections/04-metodologia.tex` | Desenho planejado, protocolo e matriz metodológica | Seção autônoma de metodologia, preservada após as hipóteses e atualizada conforme as anotações do orientador | Converter futuro em procedimento realizado apenas após execução; qualquer reorganização exige decisão editorial explícita |
| `../notebooks/01-analisar-base-discursos-rag.ipynb` | Evidência executada sobre caracterização, qualidade e prontidão do corpus | Capítulos 4 e 5 | Distinguir resultados da análise do corpus de resultados de recuperação ou geração; estimativas de chunks não representam chunks efetivamente construídos |
| `../notebooks/ANOTACOES.md` | Fundamentação explicativa e registro das decisões analíticas do notebook 01 | Apoio à redação dos capítulos 4 e 5 | Confirmar toda afirmação numérica nas saídas executadas do notebook antes de incorporá-la ao texto final |
| `4-project/README.md` e scripts | Implementação do protótipo e reprodutibilidade do experimento de viabilidade em reexecução | Capítulos 4 a 6 e apêndices | Confirmar configurações e artefatos da reexecução; congelar separadamente o protocolo do experimento principal |
| `4-project/eval/` | Baterias, rubricas, prompts e resultados da análise de viabilidade | Capítulos 4 e 6; apêndices | Revisar respondibilidade e evidências, identificar versões e hashes e separar resultados registrados dos que ainda serão reexecutados |
| `4-project/knowledge_openwebui/build_metadata.json` | Manifesto da base preparada | Capítulo 5 | Verificar se corresponde ao corpus final |
| `chatbot-rag/literatura/` | Triagem e comparação bibliográfica | Capítulo 3 | Verificar cada referência e atualizar a busca |

## Linha de demarcação da evidência

1. O protótipo técnico e suas primeiras rodadas de avaliação integram o percurso da pesquisa e compõem a etapa de viabilidade, com avaliação automatizada e inspeção humana amostral.
2. O experimento de viabilidade inclui preparação de trechos, bateria ampliada e rodadas automatizadas; essa etapa está sendo reexecutada e seus artefatos precisam ser conferidos e versionados.
3. O experimento principal deverá usar conjunto de referência validado, comparação controlada de recuperadores, avaliação humana independente e comparação com juiz automatizado.
4. Resultados da viabilidade devem ser apresentados como evidência preliminar do percurso da pesquisa, sem serem tratados como teste das hipóteses ou substitutos dos resultados do experimento principal.
