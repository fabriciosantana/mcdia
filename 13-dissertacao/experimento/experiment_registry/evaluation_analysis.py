"""Julgamento automatizado e comparação transparente com avaliações humanas."""
from __future__ import annotations

import json
import uuid
from typing import Any

FIELDS = ("factual_correctness", "context_adherence", "citation_support", "proportional_completeness", "insufficiency_recognition")


def record_automated_evaluation(connection, response_id: str, model: str, scores: dict[str, int], prompt_hash: str | None = None, notes: str = "",round_id:str|None=None,judge_prompt:str|None=None,parameters:dict|None=None,attempt:int=1) -> str:
    if connection.execute("SELECT 1 FROM responses WHERE response_id=?", (response_id,)).fetchone() is None:
        raise ValueError(f"resposta inexistente: {response_id}")
    values = []
    for field in FIELDS:
        value = scores.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value not in (0, 1, 2):
            raise ValueError(f"nota inválida: {field}")
        values.append(value)
    evaluation_id = str(uuid.uuid4())
    with connection:
        connection.execute(
            "INSERT INTO automated_evaluations(evaluation_id,response_id,evaluator_model,prompt_hash,factual_correctness,context_adherence,citation_support,proportional_completeness,insufficiency_recognition,notes,round_id,judge_prompt,provider,parameters_json,attempt) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (evaluation_id, response_id, model, prompt_hash, *values, notes,round_id,judge_prompt,'openai',json.dumps(parameters or {},ensure_ascii=False),attempt),
        )
    return evaluation_id


def _weighted_kappa(human: list[int], automated: list[int]) -> float | None:
    if not human or len(human) != len(automated):
        return None
    categories = (0, 1, 2)
    observed = sum(1 - abs(a - b) / 2 for a, b in zip(human, automated)) / len(human)
    human_mean = {c: human.count(c) / len(human) for c in categories}
    auto_mean = {c: automated.count(c) / len(automated) for c in categories}
    expected = sum(human_mean[a] * auto_mean[b] * (1 - abs(a - b) / 2) for a in categories for b in categories)
    return (observed - expected) / (1 - expected) if expected < 1 else None


def agreement_report(connection, run_id: str, human_round_id: str|None=None, judge_round_id: str|None=None) -> dict[str, Any]:
    # Uma linha por resposta: nunca combina todas as avaliações humanas com todos os juízes.
    human_filter=" AND h.round_id=?" if human_round_id else ""
    judge_filter=" AND a.round_id=?" if judge_round_id else ""
    eval_params=[]
    if human_round_id: eval_params.append(human_round_id)
    if judge_round_id: eval_params.append(judge_round_id)
    rows=connection.execute(
      "WITH h AS (SELECT h.*,ROW_NUMBER() OVER(PARTITION BY response_id ORDER BY submitted_at DESC,rowid DESC) rn FROM human_evaluations h WHERE 1=1"+human_filter+") ,"
      "a AS (SELECT a.*,ROW_NUMBER() OVER(PARTITION BY response_id ORDER BY rowid DESC) rn FROM automated_evaluations a WHERE 1=1"+judge_filter+") "
      "SELECT * FROM (SELECT h.response_id,r.question_id,h.factual_correctness,h.context_adherence,h.citation_support,h.proportional_completeness,h.insufficiency_recognition,a.factual_correctness af,a.context_adherence ac,a.citation_support asup,a.proportional_completeness ap,a.insufficiency_recognition ai,ROW_NUMBER() OVER(PARTITION BY r.question_id ORDER BY r.generation_attempt,r.response_id) qn FROM h JOIN a ON a.response_id=h.response_id JOIN responses r ON r.response_id=h.response_id WHERE r.run_id=? AND r.generation_attempt=(SELECT MIN(r2.generation_attempt) FROM responses r2 WHERE r2.run_id=r.run_id AND r2.question_id=r.question_id) AND h.rn=1 AND a.rn=1) WHERE qn=1",
      [*eval_params,run_id]).fetchall()
    dimensions = {}
    aliases = dict(zip(FIELDS, ("factual_correctness", "context_adherence", "citation_support", "proportional_completeness", "insufficiency_recognition")))
    auto_aliases = dict(zip(FIELDS, ("af", "ac", "asup", "ap", "ai")))
    for field in FIELDS:
        pairs = [(row[field], row[auto_aliases[field]]) for row in rows if row[field] is not None and row[auto_aliases[field]] is not None]
        dimensions[field] = {"n": len(pairs), "exact_agreement": (sum(a == b for a, b in pairs) / len(pairs) if pairs else None), "weighted_kappa": _weighted_kappa([a for a, _ in pairs], [b for _, b in pairs])}
    return {"run_id": run_id, "paired_responses": len(rows),"unique_questions":len({row['question_id'] for row in rows}),"unit":"pergunta; primeira repetição de geração por pergunta","human_round_id":human_round_id,"judge_round_id":judge_round_id,"pairing":"uma avaliação humana e uma avaliação automatizada mais recente por resposta","dimensions": dimensions}


def parse_judge_json(text: str) -> dict[str, Any]:
    """Valida a saída JSON do juiz sem aceitar texto parcial ou notas fora da escala."""
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("saída do juiz não é JSON válido") from exc
    if not isinstance(value, dict) or any(field not in value for field in FIELDS):
        raise ValueError("saída do juiz deve conter as cinco dimensões")
    scores = {field: value[field] for field in FIELDS}
    for field, score in scores.items():
        if not isinstance(score, int) or isinstance(score,bool) or score not in (0, 1, 2):
            raise ValueError(f"nota inválida no juiz: {field}")
    return {"scores": scores, "notes": str(value.get("notes", ""))}


def judge_response(connection, response_id: str, model: str, client=None,round_id:str|None=None,parameters:dict|None=None,attempt:int=1) -> str:
    """Executa um juiz estruturado; o cliente pode ser substituído em testes."""
    row = connection.execute("SELECT r.*,q.query FROM responses r JOIN questions q ON q.run_id=r.run_id AND q.question_id=r.question_id WHERE r.response_id=?", (response_id,)).fetchone()
    if row is None:
        raise ValueError(f"resposta inexistente: {response_id}")
    if round_id:
        judge_round=connection.execute("SELECT run_id,kind,model FROM evaluation_rounds WHERE round_id=?",(round_id,)).fetchone()
        if not judge_round or judge_round['kind']!='judge' or judge_round['run_id']!=row['run_id']: raise ValueError("rodada do juiz incompatível com a resposta")
        if judge_round['model'] and judge_round['model']!=model: raise ValueError("modelo difere daquele congelado na rodada")
    if client is None:
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv(); client = OpenAI()
    rubric=connection.execute("SELECT rv.rubric_json FROM rubric_versions rv JOIN evaluation_rounds er ON er.rubric_id=rv.rubric_id WHERE er.round_id=?",(round_id,)).fetchone() if round_id else connection.execute("SELECT rubric_json FROM rubric_versions WHERE state='frozen' ORDER BY version DESC LIMIT 1").fetchone()
    if not rubric: raise ValueError("rubrica versionada ausente; julgamento bloqueado")
    contexts=[dict(r) for r in connection.execute("SELECT rank,chunk_id,document_id,text,source_url FROM run_contexts WHERE run_id=? AND question_id=? ORDER BY rank",(row['run_id'],row['question_id']))]
    if not contexts: raise ValueError("contexto recuperado ausente; julgamento bloqueado")
    references=connection.execute("SELECT reference_chunks_json,judgments_json FROM run_question_snapshots WHERE run_id=? AND question_id=?",(row['run_id'],row['question_id'])).fetchone()
    reference_texts=[]
    if references:
        snapshot=connection.execute("SELECT chunk_set_id FROM run_question_snapshots WHERE run_id=? AND question_id=?",(row['run_id'],row['question_id'])).fetchone()
        ids=json.loads(references['reference_chunks_json'] or '[]')
        if ids:
            placeholders=','.join('?' for _ in ids)
            reference_texts=[dict(x) for x in connection.execute(f"SELECT chunk_id,document_id,text FROM document_chunks WHERE chunk_set_id=? AND chunk_id IN ({placeholders})",[snapshot['chunk_set_id'],*ids])]
    prompt = (
        "Avalie a resposta RAG exclusivamente segundo a rubrica. Julgue fidelidade ao contexto recuperado e verificabilidade pelas referências separadamente. Retorne somente JSON com "
        "factual_correctness, context_adherence, citation_support, proportional_completeness, "
        "insufficiency_recognition, cada um inteiro 0, 1 ou 2, e notes. Use as âncoras desta rubrica:\n"+rubric['rubric_json']+"\n\nPergunta:\n"+row['query']+"\n\nResposta:\n"+row["answer"]+
        "\n\nContexto recuperado (ordem apresentada):\n"+json.dumps(contexts,ensure_ascii=False)+
        "\n\nTexto das referências gold:\n"+json.dumps(reference_texts,ensure_ascii=False)+"\n\nJulgamentos gold:\n"+(references['judgments_json'] if references else "não registrados")
    )
    if attempt<1: raise ValueError("repetição do juiz deve ser positiva")
    result = client.responses.create(model=model, input=prompt,**(parameters or {}))
    parsed = parse_judge_json(result.output_text)
    import hashlib
    evaluation_id=record_automated_evaluation(connection, response_id, model, parsed["scores"], prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(), notes=parsed["notes"],round_id=round_id,judge_prompt=prompt,parameters=parameters,attempt=attempt)
    return evaluation_id
