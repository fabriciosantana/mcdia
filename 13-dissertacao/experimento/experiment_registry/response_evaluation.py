"""Persistência de respostas, citações e avaliações humanas."""
from __future__ import annotations
import json, uuid
from pathlib import Path

def _require_question(con, run_id, question_id):
    if con.execute('SELECT 1 FROM questions WHERE run_id=? AND question_id=?',(run_id,question_id)).fetchone() is None:
        raise ValueError(f'pergunta inexistente na execução: {run_id}/{question_id}')

def record_response(con, run_id, question_id, answer, model=None, prompt_hash=None, citations=()):
    if not answer or not answer.strip(): raise ValueError('answer é obrigatório')
    _require_question(con,run_id,question_id); response_id=str(uuid.uuid4())
    with con:
        con.execute('INSERT INTO responses(response_id,run_id,question_id,answer,model,prompt_hash) VALUES (?,?,?,?,?,?)',(response_id,run_id,question_id,answer,model,prompt_hash))
        for citation in citations:
            if not citation.get('document_id'): raise ValueError('citação requer document_id')
            con.execute('INSERT INTO citations(citation_id,response_id,document_id,chunk_id,cited_text) VALUES (?,?,?,?,?)',(str(uuid.uuid4()),response_id,citation['document_id'],citation.get('chunk_id'),citation.get('cited_text')))
    return response_id

def record_human_evaluation(con, response_id, evaluator, scores, notes=''):
    fields=('factual_correctness','context_adherence','citation_support','proportional_completeness','insufficiency_recognition')
    if con.execute('SELECT 1 FROM responses WHERE response_id=?',(response_id,)).fetchone() is None: raise ValueError(f'resposta inexistente: {response_id}')
    values=[]
    for field in fields:
        value=scores.get(field)
        if not isinstance(value,int) or isinstance(value,bool) or value not in (0,1,2): raise ValueError(f'nota inválida: {field}')
        values.append(value)
    evaluation_id=str(uuid.uuid4())
    with con: con.execute('INSERT INTO human_evaluations(evaluation_id,response_id,evaluator,factual_correctness,context_adherence,citation_support,proportional_completeness,insufficiency_recognition,notes) VALUES (?,?,?,?,?,?,?,?,?)',(evaluation_id,response_id,evaluator,*values,notes))
    return evaluation_id

def list_responses(con, run_id):
    rows=[]
    for row in con.execute('SELECT * FROM responses WHERE run_id=? ORDER BY created_at,response_id',(run_id,)):
        item=dict(row); item['citations']=[dict(c) for c in con.execute('SELECT citation_id,document_id,chunk_id,cited_text FROM citations WHERE response_id=?',(row['response_id'],))]; item['evaluations']=[dict(e) for e in con.execute('SELECT * FROM human_evaluations WHERE response_id=?',(row['response_id'],))]; rows.append(item)
    return rows

def ingest_jsonl(con, path):
    count=0
    for line_no,line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(),1):
        if not line.strip(): continue
        try: item=json.loads(line)
        except json.JSONDecodeError as exc: raise ValueError(f'JSONL inválido na linha {line_no}') from exc
        record_response(con,item['run_id'],item['question_id'],item['answer'],item.get('model'),item.get('prompt_hash'),item.get('citations',()))
        count+=1
    return count
