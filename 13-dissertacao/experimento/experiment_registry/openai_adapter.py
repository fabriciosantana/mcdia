"""Adaptador OpenAI para gerar respostas a partir de uma execução de recuperação."""
from __future__ import annotations
import os
import re
from pathlib import Path
from .config import ExperimentPaths
from .db import connect
from .registry import sha256_text
from .response_evaluation import record_response

def load_documents(path):
    import json
    return {str(item['id']): item for item in (json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip())}

def build_prompt(query, contexts):
    context='\n\n'.join(f"[Documento {c['id']}]\n{c['text']}" for c in contexts)
    return ("Responda à pergunta usando somente os documentos fornecidos. "
            "Se não houver evidência suficiente, declare a insuficiência. "
            "Ao usar uma evidência, indique o identificador entre colchetes.\n\n"
            f"Pergunta: {query}\n\nContexto:\n{context}")

def generate_responses(paths: ExperimentPaths, run_id, documents_path, model=None, client=None):
    """Gera e persiste respostas; client pode ser falso nos testes."""
    if client is None:
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv()
        client=OpenAI()
    model=model or os.environ.get('OPENAI_MODEL')
    if not model: raise ValueError('OPENAI_MODEL é obrigatório')
    docs=load_documents(documents_path); generated=[]
    with connect(paths.database) as con:
        questions={r['question_id']:dict(r) for r in con.execute('SELECT question_id,query FROM questions WHERE run_id=?',(run_id,))}
        if not questions: raise ValueError(f'execução sem perguntas: {run_id}')
        for row in con.execute('SELECT question_id,ranked_doc_ids_json FROM retrieval_results WHERE run_id=? ORDER BY question_id',(run_id,)):
            import json
            ids=json.loads(row['ranked_doc_ids_json']); contexts=[docs[i] for i in ids if i in docs]
            prompt=build_prompt(questions[row['question_id']]['query'],contexts)
            response=client.responses.create(model=model,input=prompt)
            answer=response.output_text
            cited_ids = set(re.findall(r"\[([^\]]+)\]", answer))
            citations=[{'document_id':c['id'],'cited_text':None} for c in contexts if c['id'] in cited_ids]
            response_id=record_response(con,run_id,row['question_id'],answer,model,sha256_text(prompt),citations)
            generated.append({'response_id':response_id,'question_id':row['question_id'],'model':model})
    return generated
