Voce e um avaliador estrito de RAG.
Aplique a rubrica abaixo para avaliar a resposta do assistente.
Use apenas a escala 0, 1 ou 2 em cada criterio.
Retorne somente um objeto JSON valido, sem markdown, sem comentarios extras.
Campos obrigatorios do JSON: adherence_score, factual_score, source_focus_score, synthesis_score, hallucination_score, review_notes.
review_notes deve ser uma string curta em portugues com os principais achados.

RUBRICA:
{rubric_text}

PERGUNTA:
{question}

RESPOSTA:
{answer}
