# Evidências preliminares do sistema RAG

Nota de apoio à redação dos capítulos de caso empírico, resultados e discussão. Esta síntese separa evidências do protótipo e do experimento de viabilidade dos procedimentos e resultados ainda previstos para o experimento principal. As fontes abaixo são artefatos locais do projeto de implementação; não constituem, por si, validação independente dos dados anotados.

## Corpus e preparação documentados

O manifesto da preparação registra 15.729 linhas de entrada, 15.726 registros com texto utilizável, três registros ignorados e 23.806 trechos. Desses trechos, 23.119 vieram de texto integral e 687 de resumos. A configuração registrada usa até 850 palavras por trecho, sobreposição de 150 palavras e até 200 trechos por arquivo; foram produzidos 120 lotes Markdown. Esses números caracterizam a preparação do artefato de viabilidade, não uma segmentação otimizada ou comparação experimental de alternativas. Fonte: [`build_metadata.json`](../../../06-inteligencia-artificial-generativa/4-project/knowledge_openwebui/build_metadata.json).

O README do projeto descreve Open WebUI como interface e orquestrador, ChromaDB como armazenamento vetorial, preparação em Python e opções de provedores OpenAI e Ollama. A configuração registrada nas rodadas de maio usa `gpt-5-nano` como gerador e como juiz; essa reutilização deve ser declarada ao apresentar as notas automatizadas. Fontes: [`README.md`](../../../06-inteligencia-artificial-generativa/4-project/README.md) e arquivos de configuração indicados abaixo.

## Experimento de viabilidade: execuções automatizadas

Os resumos de execução de 5 de maio registram quatro rodadas completas, todas sem erros de processamento:

| Artefato | Perguntas | Média do juiz (0–10) | Bateria indicada na configuração |
|---|---:|---:|---|
| [`rag_eval_20260505T142659Z`](../../../06-inteligencia-artificial-generativa/4-project/eval/results/rag_eval_20260505T142659Z.run_summary.json) | 20 | 9,350 | `discursos_questions.json` |
| [`rag_eval_20260505T153315Z`](../../../06-inteligencia-artificial-generativa/4-project/eval/results/rag_eval_20260505T153315Z.run_summary.json) | 20 | 9,250 | `discursos_questions_v4_200.json` |
| [`rag_eval_20260505T162724Z`](../../../06-inteligencia-artificial-generativa/4-project/eval/results/rag_eval_20260505T162724Z.run_summary.json) | 32 | 9,031 | `discursos_questions_v4_pilot_stratified.json` |
| [`rag_eval_20260505T171157Z`](../../../06-inteligencia-artificial-generativa/4-project/eval/results/rag_eval_20260505T171157Z.run_summary.json) | 32 | 9,094 | `discursos_questions_v4_pilot_stratified.json` |

As configurações das quatro rodadas identificam o mesmo hash de `build_metadata.json` e o mesmo par de modelos (`gpt-5-nano` para geração e julgamento). As duas rodadas de 32 itens usam a mesma bateria-piloto. As rodadas de 20 itens usam conjuntos diferentes, logo suas médias não devem ser tratadas como repetição do mesmo teste. Configurações: arquivos `.run_config.json` com os mesmos prefixos temporais na pasta `eval/results/`.

Essas médias são notas produzidas pelo juiz automatizado sob a rubrica exploratória do projeto; não são métricas de recuperação, notas humanas independentes ou estimativas da qualidade geral do sistema. Os próprios resumos registram riscos altos de mistura de autores em 29/32 itens na rodada das 16:27 e 28/32 na rodada das 17:11. Assim, a conclusão defensável é que o fluxo foi executado com sucesso e gerou material para diagnóstico, não que o sistema atingiu desempenho validado.

Uma execução posterior, de duas perguntas selecionadas (`q089` e `q191`), também foi concluída; o resumo relata risco alto de mistura de autores nos dois casos. É uma checagem exploratória de escopo muito pequeno. Fonte: [`rag_eval_20260505T190155Z.run_summary.json`](../../../06-inteligencia-artificial-generativa/4-project/eval/results/rag_eval_20260505T190155Z.run_summary.json) e [`rag_eval_20260505T190155Z.md`](../../../06-inteligencia-artificial-generativa/4-project/eval/results/rag_eval_20260505T190155Z.md).

## Estabilidade e inspeção humana amostral

O resumo de estabilidade de abril compara três rodadas de 20 perguntas com o mesmo identificador e fingerprints da base. As médias das notas do juiz foram 9,15, 9,55 e 9,35; 12 perguntas variaram entre rodadas, com maior amplitude em uma pergunta numérica. Isso documenta variação de respostas/notas sob aquela configuração e conjunto; não prova estabilidade geral do sistema. Fonte: [`stability_summary_20260417T012001Z.md`](../../../06-inteligencia-artificial-generativa/4-project/eval/results/stability_summary_20260417T012001Z.md) e os três arquivos `.run_config.json` nele listados.

O pacote de sete respostas para revisão manual declara expressamente que foi preparado por assistente como proposta argumentada e não substitui avaliação independente por outra pessoa. Nele, a leitura proposta considera inadequada a resposta `q20`, apesar da nota automática 10/10, por erro de escopo. Isso ilustra uma divergência que merece inspeção, mas não deve ser relatado como anotação humana independente nem como medida de concordância. Fonte: [`rag_eval_20260416T172816Z.manual_validation_sample.md`](../../../06-inteligencia-artificial-generativa/4-project/eval/results/rag_eval_20260416T172816Z.manual_validation_sample.md).

## Estado do experimento principal

Os materiais examinados não documentam execução do experimento principal com conjunto-ouro validado, comparação controlada entre BM25, busca vetorial e híbrida, ou avaliação humana independente dimensionada. A bateria de 200 perguntas e o piloto de 32 são artefatos disponíveis, mas seus próprios registros os apresentam como material para curadoria. A rubrica exploratória de cinco critérios e escala de 0 a 2 está em [`RUBRIC.md`](../../../06-inteligencia-artificial-generativa/4-project/eval/RUBRIC.md); ela não deve ser confundida com a rubrica de cinco dimensões e escala previstas no protocolo principal da dissertação.

Portanto, os capítulos podem apresentar como concluídos a preparação registrada do acervo de viabilidade e as execuções automatizadas acima; como preliminares, as notas do juiz e a inspeção amostral; como pendentes/em curso, a confirmação das versões e da configuração reexecutadas, a validação da respondibilidade e das evidências de referência, a comparação formal dos recuperadores e a avaliação humana independente. Nenhum desses resultados preliminares deve ser usado para corroborar ou rejeitar H1–H3.
