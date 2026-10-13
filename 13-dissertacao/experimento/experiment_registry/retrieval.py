"""Baselines de recuperação e persistência dos resultados."""
from __future__ import annotations

import csv, hashlib, json, math, re
from pathlib import Path
from typing import Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .config import ExperimentPaths
from .db import connect, initialize_database
from .registry import create_run, register_artifact

TOKEN = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)

def file_sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def load_documents(path):
    docs=[]
    for line_no,line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(),1):
        if not line.strip(): continue
        try: item=json.loads(line)
        except json.JSONDecodeError as e: raise ValueError(f'documento JSONL inválido na linha {line_no}') from e
        if not isinstance(item,dict) or not item.get('id') or not isinstance(item.get('text'),str):
            raise ValueError(f'documento inválido na linha {line_no}: requer id e text')
        docs.append({'id':str(item['id']),'document_id':str(item.get('document_id', item['id']).split(':', 1)[0]),'text':item['text'],'metadata':item.get('metadata', {})})
    if not docs: raise ValueError('o arquivo de documentos está vazio')
    return docs

def load_questions(path):
    rows=[]
    with Path(path).open(encoding='utf-8',newline='') as f:
        for row in csv.DictReader(f):
            if not row.get('question_id') or not row.get('query'): raise ValueError('pergunta requer question_id e query')
            raw=row.get('reference_doc_ids','').strip()
            refs=[x.strip() for x in raw.split(';') if x.strip()]
            chunks=[x.strip() for x in row.get('reference_chunk_ids','').split(';') if x.strip()]
            status=(row.get('status') or row.get('validation_status') or 'validated').strip().lower()
            if status not in {'validated','validada','validated_for_run'}:
                continue
            judgments={}
            raw_judgments=(row.get('relevance_judgments') or '').strip()
            if raw_judgments:
                try: judgments=json.loads(raw_judgments)
                except json.JSONDecodeError: raise ValueError(f'julgamentos inválidos para {row["question_id"]}')
            rows.append({'question_id':row['question_id'],'query':row['query'],'references':refs,'reference_chunks':chunks,'judgments':judgments,'category':row.get('category') or row.get('categoria'),'respondible':(row.get('respondible') or row.get('respondibilidade') or ('sim' if refs else '')).lower() not in {'não','nao','false','0',''}})
    if not rows: raise ValueError('o arquivo de perguntas está vazio')
    return rows

def _tokens(text): return TOKEN.findall(text.lower())

def bm25_scores(docs, query, k1=1.5, b=.75):
    token_docs=[_tokens(d['text']) for d in docs]; lengths=np.array([len(x) for x in token_docs],dtype=float); avg=max(lengths.mean(),1)
    df={}
    for terms in token_docs:
        for term in set(terms): df[term]=df.get(term,0)+1
    qterms=set(_tokens(query)); scores=[]
    n=len(docs)
    for terms,dl in zip(token_docs,lengths):
        freq={t:terms.count(t) for t in qterms}; score=0.
        for t,tf in freq.items():
            if not tf: continue
            idf=math.log(1+(n-df.get(t,0)+.5)/(df.get(t,0)+.5))
            score += idf*tf*(k1+1)/(tf+k1*(1-b+b*dl/avg))
        scores.append(score)
    return np.array(scores)

def tfidf_scores(docs, query):
    vectorizer=TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True)
    matrix=vectorizer.fit_transform([d['text'] for d in docs])
    return (matrix @ vectorizer.transform([query]).T).toarray().ravel()

def _normalize(values):
    lo,hi=float(values.min()),float(values.max())
    return (values-lo)/(hi-lo) if hi>lo else np.zeros_like(values)

def rank_documents(docs, query, method, embedding_model=None, embedding_client=None):
    if method == 'dense':
        from .embedding_retrieval import rank_dense
        return rank_dense(docs, query, embedding_model, embedding_client)
    if method not in {'bm25','tfidf','hybrid'}: raise ValueError(f'estratégia não suportada: {method}')
    bm=bm25_scores(docs,query); tf=tfidf_scores(docs,query)
    scores=bm if method=='bm25' else tf if method=='tfidf' else (_normalize(bm)+_normalize(tf))/2
    order=np.argsort(-scores,kind='stable')
    return [{'id':docs[i]['id'],'document_id':str(docs[i].get('document_id', docs[i]['id']).split(':', 1)[0]),'score':float(scores[i])} for i in order]

def _metrics(results, questions):
    by={q['question_id']:q for q in questions}; ranks=[]; values={key:[] for key in ('precision_at_1','precision_at_5','precision_at_10','hit_at_1','hit_at_5','hit_at_10','ndcg_at_5','ndcg_at_10')}
    for result in results:
        q=by[result['question_id']]; refs=set(q['reference_chunks'] or q['references'])
        if not refs: continue
        ranking=result['ranking']; relevant=[item for item in ranking if item['id'] in refs or item.get('document_id') in refs]
        rank=next((i+1 for i,item in enumerate(ranking) if item['id'] in refs or item.get('document_id') in refs),None)
        ranks.append(rank)
        grades=q.get('judgments',{})
        for k in (1,5,10):
            top=ranking[:k]; hits=[item for item in top if item['id'] in refs or item.get('document_id') in refs]
            values[f'precision_at_{k}'].append(len(hits)/k); values[f'hit_at_{k}'].append(float(bool(hits)))
            if k in (5,10):
                dcg=sum((float(grades.get(item['id'], grades.get(item.get('document_id'), 1))))/math.log2(i+2) for i,item in enumerate(top) if item['id'] in refs or item.get('document_id') in refs)
                ideal=sorted([float(v) for v in grades.values()] or [1], reverse=True)[:k]
                idcg=sum(v/math.log2(i+2) for i,v in enumerate(ideal)); values[f'ndcg_at_{k}'].append(dcg/idcg if idcg else 0.0)
    n=len(ranks)
    result={'recall_at_1':sum(r is not None and r<=1 for r in ranks)/n if n else None,'recall_at_5':sum(r is not None and r<=5 for r in ranks)/n if n else None,'recall_at_10':sum(r is not None and r<=10 for r in ranks)/n if n else None,'mrr':sum(1/r if r else 0 for r in ranks)/n if n else None,'respondible_questions':n}
    result.update({key:(sum(vals)/len(vals) if vals else None) for key,vals in values.items()})
    return result

def run_retrieval(paths:ExperimentPaths, documents_path, questions_path, method, name, embedding_model=None, embedding_client=None):
    docs=load_documents(documents_path); questions=load_questions(questions_path)
    config={'retrieval':{'method':method,'k':10,'embedding_model':embedding_model},'inputs':{'documents_sha256':file_sha256(documents_path),'questions_sha256':file_sha256(questions_path)}}
    paths.ensure_directories(); initialize_database(paths)
    with connect(paths.database) as con:
        run_id=create_run(con,name,config)
        for q in questions:
            con.execute('INSERT INTO questions(run_id,question_id,query,reference_doc_ids_json,respondible) VALUES (?,?,?,?,?)',(run_id,q['question_id'],q['query'],json.dumps(q['references']),int(q['respondible'])))
            con.execute('INSERT INTO question_metadata(run_id,question_id,category,validation_status,reference_chunks_json,relevance_judgments_json) VALUES (?,?,?,?,?,?)',(run_id,q['question_id'],q.get('category'),'validated',json.dumps(q.get('reference_chunks',[])),json.dumps(q.get('judgments',{}))))
        detailed=[]
        for q in questions:
            ranking=rank_documents(docs,q['query'],method,embedding_model,embedding_client)
            top=ranking[:10]; detailed.append({'question_id':q['question_id'],'ranking':top})
            con.execute('INSERT INTO retrieval_results(run_id,question_id,ranked_doc_ids_json,scores_json) VALUES (?,?,?,?)',(run_id,q['question_id'],json.dumps([x['id'] for x in top]),json.dumps([x['score'] for x in top])))
        metrics=_metrics(detailed,questions)
        con.execute('INSERT INTO retrieval_metrics(run_id,method,recall_at_1,recall_at_5,recall_at_10,mrr,respondible_questions,precision_at_1,precision_at_5,precision_at_10,hit_at_1,hit_at_5,hit_at_10,ndcg_at_5,ndcg_at_10) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(run_id,method,metrics['recall_at_1'],metrics['recall_at_5'],metrics['recall_at_10'],metrics['mrr'],metrics['respondible_questions'],metrics['precision_at_1'],metrics['precision_at_5'],metrics['precision_at_10'],metrics['hit_at_1'],metrics['hit_at_5'],metrics['hit_at_10'],metrics['ndcg_at_5'],metrics['ndcg_at_10']))
        con.execute("UPDATE experiment_runs SET state='completed', finished_at=CURRENT_TIMESTAMP WHERE run_id=?", (run_id,))
        register_artifact(con,run_id,'documents-input',documents_path)
        register_artifact(con,run_id,'questions-input',questions_path)
        output=paths.outputs/f'{run_id}-retrieval.json'; output.write_text(json.dumps({'run_id':run_id,'method':method,'metrics':metrics,'results':detailed},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        register_artifact(con,run_id,'retrieval-detail',output)
    return {'run_id':run_id,'metrics':metrics,'output':str(output)}
