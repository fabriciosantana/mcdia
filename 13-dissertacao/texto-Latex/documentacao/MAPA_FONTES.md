# Mapa de proveniência e reaproveitamento

| Material de origem | Papel na dissertação | Destino inicial | Cuidado editorial |
|---|---|---|---|
| `../revisao-pre-projeto/fabricio-santana-tecnicas-avaliacao-rag_REV-PITA.pdf` | Anotações da revisão do pré-projeto pelo orientador | Capítulos portados do pré-projeto e elementos pré-textuais correspondentes | Aplicar as intervenções identificáveis de modo rastreável, preservando o desenho da dissertação e distinguindo sugestões editoriais de mudanças metodológicas |
| `chatbot-rag-pre/sections/01-introducao.tex` | Problema, pergunta, justificativa e objetivos | Capítulo 1 | Atualizar linguagem prospectiva somente quando houver evidência final |
| `chatbot-rag-pre/sections/02-referencial-teorico.tex` | Fundamentos e lacuna | Capítulos 2 e 3 | Separar referencial conceitual de comparação crítica dos trabalhos |
| `chatbot-rag-pre/sections/03-hipoteses.tex` | Hipóteses do estudo | Seção autônoma, com conteúdo integral do pré-projeto e revisão ortográfica indicada pelo orientador; discussão posterior no capítulo de discussão | Não tratar como teste causal clássico; qualquer reorganização ou reescrita exige decisão editorial explícita |
| `chatbot-rag-pre/sections/04-metodologia.tex` | Desenho planejado, protocolo e matriz metodológica | Seção autônoma de metodologia, preservada após as hipóteses e atualizada conforme as anotações do orientador | Converter futuro em procedimento realizado apenas após execução; qualquer reorganização exige decisão editorial explícita |
| `chatbot-rag/` | Prova de conceito e evidência preliminar | Capítulos 3, 5 e 7 | Não apresentar como resultado final da dissertação |
| `4-project/README.md` e scripts | Implementação e reprodutibilidade | Capítulo 5 e apêndices | Conferir configuração efetivamente usada na rodada final |
| `4-project/eval/` | Baterias, rubricas, prompts e resultados | Capítulos 4 e 6; apêndices | Congelar a versão escolhida e registrar hashes |
| `4-project/knowledge_openwebui/build_metadata.json` | Manifesto da base preparada | Capítulo 5 | Verificar se corresponde ao corpus final |
| `chatbot-rag/literatura/` | Triagem e comparação bibliográfica | Capítulo 3 | Verificar cada referência e atualizar a busca |

## Linha de demarcação da evidência

1. O artigo demonstra viabilidade preliminar com bateria pequena e avaliação automatizada acompanhada de inspeção humana amostral.
2. A dissertação amplia o desenho com bateria balanceada, conjunto de referência, avaliação formal da recuperação, baselines, avaliação humana independente e comparação controlada com juiz automatizado.
3. Números do artigo só podem aparecer identificados como resultados preliminares ou antecedentes do estudo.
4. Números dos capítulos de resultados e discussão devem vir de uma execução final congelada e documentada.
