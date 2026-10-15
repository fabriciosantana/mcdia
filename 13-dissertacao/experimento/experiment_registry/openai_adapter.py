"""Adaptador OpenAI para gerar respostas a partir de uma execução de recuperação."""
from __future__ import annotations
import os, re, json, time, hashlib
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

def generate_responses(paths: ExperimentPaths, run_id, documents_path=None, model=None, client=None, parameters=None, max_items=None, attempt:int=1,max_total_prompt_tokens:int|None=None,max_duration_seconds:int|None=None,retry_uncertain:bool=False):
    """Gera com contextos congelados no SQLite e checkpoints persistentes por resposta."""
    if client is None:
        from dotenv import load_dotenv
        from openai import OpenAI
        load_dotenv()
        client=OpenAI()
    model=model or os.environ.get('OPENAI_MODEL')
    if not model: raise ValueError('OPENAI_MODEL é obrigatório')
    generated=[]; parameters=parameters or {"temperature":0.0}
    with connect(paths.database) as con:
        questions={r['question_id']:dict(r) for r in con.execute('SELECT question_id,query FROM questions WHERE run_id=?',(run_id,))}
        if not questions: raise ValueError(f'execução sem perguntas: {run_id}')
        if attempt<1: raise ValueError("repetição deve ser um inteiro positivo")
        existing={r[0] for r in con.execute("SELECT question_id FROM responses WHERE run_id=? AND generation_attempt=?",(run_id,attempt))}
        pending=[r for r in con.execute('SELECT question_id FROM retrieval_results WHERE run_id=? ORDER BY question_id',(run_id,)) if r['question_id'] not in existing]
        if max_items is not None: pending=pending[:max_items]
        uncertain=[r['question_id'] for r in con.execute("SELECT DISTINCT gi.question_id FROM generation_items gi JOIN experiment_jobs j USING(job_id) WHERE gi.run_id=? AND gi.generation_attempt=? AND gi.state IN ('running','uncertain')",(run_id,attempt))]
        blocked=[qid for qid in uncertain if any(row['question_id']==qid for row in pending)]
        if blocked and not retry_uncertain:raise ValueError("há itens com resultado incerto nesta repetição: "+", ".join(blocked)+". Marque a retentativa explícita para reenviar.")
        contexts_by_question={}; estimated_tokens=0
        for row in pending:
            contexts=[dict(r) for r in con.execute("SELECT rank,chunk_id,document_id,text,source_url,score FROM run_contexts WHERE run_id=? AND question_id=? ORDER BY rank",(run_id,row['question_id']))]
            if not contexts: raise ValueError(f"snapshot de contexto ausente para {row['question_id']}; geração bloqueada")
            for context in contexts: context['id']=context['chunk_id']
            prompt=build_prompt(questions[row['question_id']]['query'],contexts)
            estimated_tokens+=(len(prompt)+3)//4
            contexts_by_question[row['question_id']]=(contexts,prompt)
        if max_total_prompt_tokens is not None and estimated_tokens>max_total_prompt_tokens: raise ValueError(f"preflight excede limite: cerca de {estimated_tokens} tokens de entrada estimados para um teto de {max_total_prompt_tokens}; nenhuma chamada enviada")
    job_id=__import__('uuid').uuid4().hex
    with connect(paths.database) as con:
        con.execute("INSERT INTO experiment_jobs(job_id,run_id,kind,state,progress_total,progress_done,attempts) VALUES (?,?, 'generation','running',?,0,1)",(job_id,run_id,len(pending)))
        for row in pending:
            prompt_hash=sha256_text(contexts_by_question[row['question_id']][1])
            con.execute("INSERT INTO generation_items(job_id,run_id,question_id,generation_attempt,state,request_hash) VALUES (?,?,?,?, 'queued',?)",(job_id,run_id,row['question_id'],attempt,prompt_hash))
    job_started=time.monotonic()
    try:
      for row in pending:
        with connect(paths.database) as con:
            state=con.execute("SELECT state FROM experiment_jobs WHERE job_id=?",(job_id,)).fetchone()
            if not state or state['state']!='running': break
            con.execute("UPDATE generation_items SET state='running',started_at=CURRENT_TIMESTAMP WHERE job_id=? AND question_id=?",(job_id,row['question_id']))
        contexts,prompt=contexts_by_question[row['question_id']]
        if max_duration_seconds is not None and time.monotonic()-job_started>=max_duration_seconds:
            with connect(paths.database) as con: con.execute("UPDATE experiment_jobs SET state='cancelled',error='limite de duração atingido',finished_at=CURRENT_TIMESTAMP WHERE job_id=?",(job_id,))
            break
        started=time.monotonic()
        response=client.responses.create(model=model,input=prompt,**parameters)
        duration=int((time.monotonic()-started)*1000); answer=response.output_text
        valid_ids={c['chunk_id'] for c in contexts}; cited_ids=set(re.findall(r"\[([^\]]+)\]",answer))
        citations=[]
        for cited in cited_ids:
            if cited in valid_ids:
                context=next(c for c in contexts if c['chunk_id']==cited)
                citations.append({'document_id':context['document_id'],'chunk_id':cited,'cited_text':cited,'source_url':context['source_url'],'validity':'valid'})
            else: citations.append({'document_id':cited,'chunk_id':None,'cited_text':cited,'source_url':None,'validity':'unknown'})
        with connect(paths.database) as con:
            response_id=record_response(con,run_id,row['question_id'],answer,model,sha256_text(prompt),citations)
            context_hash=hashlib.sha256(json.dumps(contexts,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
            usage={"provider_usage":getattr(response,'usage',None),"estimated_input_tokens":(len(prompt)+3)//4,"cost_estimate":None}
            con.execute("UPDATE responses SET prompt_text=?,context_hash=?,provider='openai',parameters_json=?,duration_ms=?,usage_json=?,generation_attempt=? WHERE response_id=?",(prompt,context_hash,json.dumps(parameters),duration,json.dumps(usage,default=lambda x:getattr(x,'__dict__',str(x))),attempt,response_id))
            con.execute("UPDATE generation_items SET state='completed',response_id=?,finished_at=CURRENT_TIMESTAMP WHERE job_id=? AND question_id=?",(response_id,job_id,row['question_id']))
            generated.append({'response_id':response_id,'question_id':row['question_id'],'model':model})
            con.execute("UPDATE experiment_jobs SET progress_done=progress_done+1,heartbeat_at=CURRENT_TIMESTAMP WHERE job_id=?",(job_id,))
      with connect(paths.database) as con:
        state=con.execute("SELECT state FROM experiment_jobs WHERE job_id=?",(job_id,)).fetchone()
        if state and state['state']=='running': con.execute("UPDATE experiment_jobs SET state='completed',finished_at=CURRENT_TIMESTAMP WHERE job_id=?",(job_id,))
    except Exception as exc:
      with connect(paths.database) as con:
        con.execute("UPDATE generation_items SET state='uncertain',error=?,finished_at=CURRENT_TIMESTAMP WHERE job_id=? AND state='running'",(str(exc),job_id))
        con.execute("UPDATE experiment_jobs SET state='failed',error=?,finished_at=CURRENT_TIMESTAMP WHERE job_id=?",(str(exc),job_id))
      raise
    return {"generated":generated,"job_id":job_id,"attempt":attempt,"estimated_prompt_tokens":estimated_tokens,"cost_estimate":None}
