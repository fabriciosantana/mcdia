"""Baselines de recuperação e persistência dos resultados."""
from __future__ import annotations

import csv, hashlib, json, math, os, re, gzip
from collections import Counter
from pathlib import Path
from typing import Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .config import ExperimentPaths
from .db import connect, initialize_database
from .registry import create_run, register_artifact
from .question_bank import catalog_questions_for_run

TOKEN = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)

def _list_doc_refs(value):
    if value is None or value=="": return []
    if isinstance(value,list): return [str(x) for x in value]
    try:
        parsed=json.loads(value)
        if isinstance(parsed,list): return [str(x) for x in parsed]
    except (TypeError,json.JSONDecodeError): pass
    return [x.strip() for x in str(value).split(";") if x.strip()]

def _bool_value(value):
    if isinstance(value,str): return value.strip().lower() in {'1','true','yes','sim'}
    return bool(value)

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


def load_catalog_questions(database, question_ids=None):
    rows = []
    with connect(database) as connection:
        for item in catalog_questions_for_run(connection, question_ids):
            rows.append({
                'question_id': item['question_id'], 'query': item['query'],
                'references': item['reference_doc_ids'], 'reference_chunks': item['reference_chunk_ids'],
                'judgments': item['relevance_judgments'], 'category': item['category'],
                'respondible': bool(item['respondible']),
            })
    return rows

def load_chunk_set(connection, chunk_set_id):
    rows=connection.execute("SELECT c.chunk_id AS id,c.document_id,c.text,c.metadata_json,d.source_url FROM document_chunks c JOIN documents d ON d.corpus_version_id=c.corpus_version_id AND d.document_id=c.document_id WHERE c.chunk_set_id=? ORDER BY c.document_id,c.position_start,c.chunk_id",(chunk_set_id,)).fetchall()
    if not rows: raise ValueError(f"conjunto de chunks vazio ou inexistente: {chunk_set_id}")
    return [{"id":r["id"],"document_id":r["document_id"],"text":r["text"],"metadata":json.loads(r["metadata_json"] or "{}"),"source_url":r["source_url"]} for r in rows]

def _tokens(text): return TOKEN.findall(text.lower())

class BM25Index:
    def __init__(self,docs):
        self.documents=docs;self.tokens=[_tokens(d['text']) for d in docs];self.frequencies=[Counter(x) for x in self.tokens];self.lengths=np.array([len(x) for x in self.tokens],dtype=float);self.avg=max(self.lengths.mean(),1);self.df={}
        for terms in self.tokens:
            for term in set(terms):self.df[term]=self.df.get(term,0)+1
    def score(self,query,k1=1.5,b=.75):
        qterms=set(_tokens(query));n=len(self.tokens);scores=[]
        for frequencies,dl in zip(self.frequencies,self.lengths):
            freq={t:frequencies.get(t,0) for t in qterms};score=0.
            for term,tf in freq.items():
                if not tf:continue
                idf=math.log(1+(n-self.df.get(term,0)+.5)/(self.df.get(term,0)+.5))
                score+=idf*tf*(k1+1)/(tf+k1*(1-b+b*dl/self.avg))
            scores.append(score)
        return np.asarray(scores)
    def serialize(self):
        payload={"document_ids":[d['id'] for d in self.documents],"frequencies":[dict(x) for x in self.frequencies],"lengths":self.lengths.astype(int).tolist(),"df":self.df,"avg":float(self.avg),"token_count":int(self.lengths.sum()),"version":"bm25-v1"}
        return gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(",",":"),sort_keys=True).encode())
    @classmethod
    def deserialize(cls,blob):
        payload=json.loads(gzip.decompress(blob).decode())
        instance=cls.__new__(cls);instance.documents=[{"id":item} for item in payload['document_ids']];instance.tokens=[];instance.frequencies=[Counter(item) for item in payload['frequencies']];instance.lengths=np.asarray(payload['lengths'],dtype=float);instance.avg=float(payload['avg']);instance.df={k:int(v) for k,v in payload['df'].items()};return instance

def persistent_bm25_index(connection,chunk_set_id,docs):
    digest=hashlib.sha256(json.dumps([(d['id'],hashlib.sha256(d['text'].encode()).hexdigest()) for d in docs],separators=(",",":")).encode()).hexdigest()
    row=connection.execute("SELECT * FROM lexical_indexes WHERE chunk_set_id=?",(chunk_set_id,)).fetchone()
    if row and row['corpus_digest']==digest and hashlib.sha256(row['index_gzip']).hexdigest()==row['index_sha256']:
        return BM25Index.deserialize(row['index_gzip']),row['index_sha256']
    job_id=__import__('uuid').uuid4().hex
    with connection:connection.execute("INSERT INTO experiment_jobs(job_id,kind,state,progress_total,attempts) VALUES (?,'lexical-build','running',1,1)",(job_id,))
    try:
        index=BM25Index(docs);blob=index.serialize();checksum=hashlib.sha256(blob).hexdigest();token_count=int(index.lengths.sum())
        with connection:
            connection.execute("INSERT INTO lexical_indexes(chunk_set_id,algorithm,index_version,corpus_digest,document_count,token_count,index_sha256,index_gzip) VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(chunk_set_id) DO UPDATE SET algorithm=excluded.algorithm,index_version=excluded.index_version,corpus_digest=excluded.corpus_digest,document_count=excluded.document_count,token_count=excluded.token_count,index_sha256=excluded.index_sha256,index_gzip=excluded.index_gzip,created_at=CURRENT_TIMESTAMP",(chunk_set_id,'bm25','bm25-v1',digest,len(docs),token_count,checksum,blob))
            connection.execute("UPDATE experiment_jobs SET state='completed',progress_done=1,finished_at=CURRENT_TIMESTAMP WHERE job_id=?",(job_id,))
    except Exception as exc:
        with connection:connection.execute("UPDATE experiment_jobs SET state='failed',error=?,finished_at=CURRENT_TIMESTAMP WHERE job_id=?",(str(exc),job_id))
        raise
    return index,checksum

class TfidfIndex:
    def __init__(self,docs):
        self.vectorizer=TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True);self.matrix=self.vectorizer.fit_transform([d['text'] for d in docs])
    def score(self,query):return (self.matrix@self.vectorizer.transform([query]).T).toarray().ravel()

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

def rank_documents(docs, query, method, embedding_model=None, embedding_client=None, embedding_cache=None, vector_index=None, parameters=None, lexical_index=None):
    parameters=parameters or {}
    if method == 'dense':
        if vector_index:
            from .embedding_retrieval import rank_chroma
            return rank_chroma(embedding_cache,vector_index['collection_name'],query,embedding_model,embedding_client,limit=int(parameters.get('dense_candidate_k',1000)))
        from .embedding_retrieval import rank_dense
        return rank_dense(docs, query, embedding_model, embedding_client, embedding_cache)
    if method not in {'bm25','tfidf','hybrid','hybrid_legacy'}: raise ValueError(f'estratégia não suportada: {method}')
    bm=(lexical_index['bm25'].score(query,float(parameters.get('k1',1.5)),float(parameters.get('b',.75))) if lexical_index and 'bm25' in lexical_index else bm25_scores(docs,query,float(parameters.get('k1',1.5)),float(parameters.get('b',.75)))) if method in {'bm25','hybrid','hybrid_legacy'} else None
    tf=(lexical_index['tfidf'].score(query) if lexical_index and 'tfidf' in lexical_index else tfidf_scores(docs,query)) if method in {'tfidf','hybrid_legacy'} else None
    if method=='bm25': scores=bm
    elif method=='tfidf': scores=tf
    elif method=='hybrid_legacy': scores=(_normalize(bm)+_normalize(tf))/2
    else:
        from .embedding_retrieval import rank_dense
        if vector_index:
            from .embedding_retrieval import rank_chroma
            dense=rank_chroma(embedding_cache,vector_index['collection_name'],query,embedding_model,embedding_client,limit=int(parameters.get('dense_candidate_k',1000)))
        else: dense=rank_dense(docs,query,embedding_model,embedding_client,embedding_cache)
        dense_by_id={item['id']:item['score'] for item in dense}
        sparse_order=np.argsort(-bm,kind='stable')
        sparse_rank={int(i):rank+1 for rank,i in enumerate(sparse_order)}
        dense_rank={item['id']:rank+1 for rank,item in enumerate(dense)}
        rrf_k=max(1,int(parameters.get('rrf_k',60)))
        scores=np.array([1/(rrf_k+sparse_rank[i])+1/(rrf_k+dense_rank.get(docs[i]['id'],len(docs)+1)) for i in range(len(docs))])
    order=np.argsort(-scores,kind='stable')
    return [{'id':docs[i]['id'],'document_id':str(docs[i].get('document_id', docs[i]['id']).split(':', 1)[0]),'score':float(scores[i])} for i in order]

def calculate_retrieval_metrics(results, questions):
    """Calcula métricas de relevância e cobertura por pergunta.

    `results` contém rankings de chunks; `questions` contém gold documental/chunk
    e julgamentos graduados. Perguntas sem gold ou fora do escopo são não aplicáveis.
    """
    by={q['question_id']:q for q in questions}; ranks=[]; values={key:[] for key in ('precision_at_1','precision_at_5','precision_at_10','hit_at_1','hit_at_5','hit_at_10','ndcg_at_5','ndcg_at_10')}; coverage={"eligible":0,"not_applicable":0}
    for result in results:
        q=by[result['question_id']]; refs=set(q['reference_chunks'] or q['references'])
        grades=q.get('judgments',{})
        applicable=q.get('respondible',True) and str(q.get('answerability','')).lower() not in {'parcial','partially_respondible'}
        if not refs or not applicable:
            coverage['not_applicable']+=1
            continue
        coverage['eligible']+=1
        ranking=result['ranking']; seen=set(); unique=[]
        for item in ranking:
            key=item['id']
            if key not in seen: seen.add(key); unique.append(item)
        ranking=unique
        def is_relevant(item): return item['id'] in refs or item.get('document_id') in refs
        relevant=[item for item in ranking if is_relevant(item)]
        rank=next((i+1 for i,item in enumerate(ranking) if item['id'] in refs or item.get('document_id') in refs),None)
        ranks.append(rank)
        for k in (1,5,10):
            top=ranking[:k]; hits=[item for item in top if is_relevant(item)]
            values[f'precision_at_{k}'].append(len(hits)/k); values[f'hit_at_{k}'].append(float(bool(hits)))
            if k in (5,10):
                relevance={item['id']:float(grades.get(item['id'],grades.get(item.get('document_id'),1))) for item in hits}
                dcg=sum((2**relevance.get(item['id'],0)-1)/math.log2(i+2) for i,item in enumerate(top))
                ideal=sorted((float(v) for v in grades.values()),reverse=True)[:k] if grades else [1.0 for _ in refs]
                idcg=sum((2**v-1)/math.log2(i+2) for i,v in enumerate(ideal)); values[f'ndcg_at_{k}'].append(min(1.0,dcg/idcg) if idcg else None)
    n=len(ranks)
    def recall_at(k):
        per_question=[]
        for result_row in results:
            question=by[result_row['question_id']]; gold=set(question['reference_chunks'] or question['references'])
            if not gold or not question.get('respondible',True) or str(question.get('answerability','')).lower() in {'parcial','partially_respondible'}: continue
            found={gold_id for gold_id in gold if any(hit['id']==gold_id or hit.get('document_id')==gold_id for hit in result_row['ranking'][:k])}
            per_question.append(len(found)/len(gold))
        return sum(per_question)/len(per_question) if per_question else None
    result={'recall_at_1':recall_at(1),'recall_at_5':recall_at(5),'recall_at_10':recall_at(10),'mrr':sum(1/r if r else 0 for r in ranks)/n if n else None,'respondible_questions':n,'metric_version':'retrieval-v2','coverage':coverage}
    result.update({key:(sum(valid)/len(valid) if (valid:=[v for v in vals if v is not None]) else None) for key,vals in values.items()})
    return result

def run_retrieval(paths:ExperimentPaths, documents_path=None, questions_path=None, method='bm25', name='retrieval-run', embedding_model=None, embedding_client=None, question_ids=None, chunk_set_id=None, battery_id=None, top_k=10, parameters=None, vector_index_id=None,plan_id=None):
    initialize_database(paths)
    if plan_id:
        with connect(paths.database) as con:
            plan=con.execute("SELECT * FROM experiment_plans WHERE plan_id=? AND state='frozen'",(plan_id,)).fetchone()
            if not plan: raise ValueError("plano inexistente ou não congelado")
            saved=json.loads(plan['configuration_json']); retrieval=saved['retrieval']
            method=retrieval['method'];top_k=int(retrieval.get('k',10));parameters=retrieval.get('parameters',{});embedding_model=retrieval.get('embedding_model');chunk_set_id=plan['chunk_set_id'];battery_id=plan['battery_id'];vector_index_id=plan['index_id'];name=plan['name'] if name=='retrieval-run' else name
    if chunk_set_id:
        with connect(paths.database) as con: docs=load_chunk_set(con,chunk_set_id)
        documents_sha=hashlib.sha256(json.dumps([(d['id'],d['text']) for d in docs],ensure_ascii=False).encode()).hexdigest()
    else:
        if not documents_path: raise ValueError('selecione um conjunto de chunks do catálogo')
        docs=load_documents(documents_path); documents_sha=file_sha256(documents_path)
    if battery_id and chunk_set_id:
        with connect(paths.database) as con:
            state=con.execute("SELECT state,chunk_set_id FROM question_batteries WHERE battery_id=?",(battery_id,)).fetchone()
            if not state or state['state']!='frozen': raise ValueError("a bateria precisa estar congelada antes da execução")
            if state['chunk_set_id']!=chunk_set_id: raise ValueError("segmentação difere daquela congelada na bateria")
            raw_members=con.execute("SELECT bm.question_id,bm.question_revision,qr.question_json,v.decision FROM battery_members bm JOIN question_revisions qr ON qr.question_id=bm.question_id AND qr.revision=bm.question_revision JOIN question_validation v ON v.question_id=bm.question_id AND v.question_revision=bm.question_revision AND v.chunk_set_id=? WHERE bm.battery_id=? ORDER BY bm.position,bm.question_id",(chunk_set_id,battery_id)).fetchall()
            members={}
            for row in raw_members:
                snapshot=json.loads(row['question_json'])
                if str(snapshot.get('eligible',True)).lower() not in {'false','0','nao'}: members[row['question_id']]={**snapshot,'question_id':row['question_id'],'question_revision':row['question_revision'],'decision':row['decision']}
            if question_ids is not None: members={k:v for k,v in members.items() if k in question_ids}
            if not members: raise ValueError('a bateria não possui perguntas validadas e elegíveis')
            questions=[]
            for r in members.values():
                gold=con.execute("SELECT chunk_id,relevance_grade,sufficient FROM question_reference_chunks WHERE question_id=? AND question_revision=? AND chunk_set_id=? AND review_state IN ('validated','adjudicated')",(r['question_id'],r['question_revision'],chunk_set_id)).fetchall()
                questions.append({'question_id':r['question_id'],'query':r['query'],'references':_list_doc_refs(r.get('reference_doc_ids')),'reference_chunks':[x['chunk_id'] for x in gold if x['relevance_grade']>0],'sufficient_chunks':[x['chunk_id'] for x in gold if x['sufficient'] and x['relevance_grade']>0],'judgments':{x['chunk_id']:x['relevance_grade'] for x in gold},'category':r.get('category'),'source_category':r.get('source_category'),'secondary_categories':r.get('secondary_categories',[]),'expected_answer_criteria':r.get('expected_answer_criteria'),'answerability':r.get('answerability'),'respondible':_bool_value(r.get('respondible')) if r['decision']=='partially_respondible' else r['decision']=='respondible'})
    elif question_ids is None:
        if questions_path is None:
            raise ValueError('informe um arquivo de perguntas ou selecione perguntas validadas no catálogo')
        questions=load_questions(questions_path)
    else:
        questions=load_catalog_questions(paths.database, question_ids)
        if not questions:
            raise ValueError('nenhuma pergunta validada foi selecionada no catálogo')
    effective_embedding_model = embedding_model or os.environ.get('OPENAI_EMBEDDING_MODEL')
    if method in {'dense','hybrid'} and not effective_embedding_model: raise ValueError('configure o modelo de embeddings')
    if top_k<1: raise ValueError('k deve ser positivo')
    lexical_index={};lexical_index_hash=None
    if method in {'bm25','hybrid','hybrid_legacy'}:
        if chunk_set_id:
            with connect(paths.database) as con: bm25_index,lexical_index_hash=persistent_bm25_index(con,chunk_set_id,docs)
        else: bm25_index=BM25Index(docs)
        lexical_index['bm25']=bm25_index
    if method in {'tfidf','hybrid_legacy'}:lexical_index['tfidf']=TfidfIndex(docs)
    vector_index=None
    if method in {'dense','hybrid'} and vector_index_id:
        with connect(paths.database) as con:
            row=con.execute("SELECT * FROM vector_indexes WHERE index_id=? AND state='completed' AND chunk_set_id=? AND model=?",(vector_index_id,chunk_set_id,effective_embedding_model)).fetchone()
            if row is None: raise ValueError("índice vetorial não concluído ou incompatível com a segmentação/modelo")
            vector_index=dict(row)
    question_hash = file_sha256(questions_path) if questions_path and question_ids is None and not battery_id else hashlib.sha256(json.dumps(questions, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
    config={'retrieval':{'method':method,'k':top_k,'embedding_model':effective_embedding_model,'parameters':parameters or {},'lexical_index_version':'bm25-v1' if lexical_index_hash else None,'lexical_index_sha256':lexical_index_hash},'inputs':{'documents_sha256':documents_sha,'questions_sha256':question_hash,'question_source':'battery' if battery_id else ('catalog' if question_ids is not None else 'file'),'chunk_set_id':chunk_set_id,'battery_id':battery_id}}
    paths.ensure_directories()
    with connect(paths.database) as con:
        if not (chunk_set_id and battery_id): members={}
        run_id=create_run(con,name,config)
        attempt=1
        if plan_id:
            attempt=con.execute("SELECT COALESCE(MAX(attempt),0)+1 FROM experiment_runs WHERE plan_id=?",(plan_id,)).fetchone()[0]
            con.execute("UPDATE experiment_runs SET plan_id=?,attempt=? WHERE run_id=?",(plan_id,attempt,run_id))
        for q in questions:
            con.execute('INSERT INTO questions(run_id,question_id,query,reference_doc_ids_json,respondible) VALUES (?,?,?,?,?)',(run_id,q['question_id'],q['query'],json.dumps(q['references']),int(q['respondible'])))
            con.execute('INSERT INTO question_metadata(run_id,question_id,category,validation_status,reference_chunks_json,relevance_judgments_json) VALUES (?,?,?,?,?,?)',(run_id,q['question_id'],q.get('category'),'validated',json.dumps(q.get('reference_chunks',[])),json.dumps(q.get('judgments',{}))))
            if chunk_set_id and battery_id:
                member=members[q['question_id']]
                con.execute('INSERT INTO run_question_snapshots(run_id,question_id,question_revision,battery_id,chunk_set_id,query,expected_answer_criteria,answerability,category,source_category,secondary_categories_json,reference_chunks_json,sufficient_chunks_json,judgments_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(run_id,q['question_id'],member['question_revision'],battery_id,chunk_set_id,q['query'],member.get('expected_answer_criteria'),member.get('answerability'),member.get('category'),member.get('source_category'),json.dumps(member.get('secondary_categories',[]),ensure_ascii=False),json.dumps(q['reference_chunks']),json.dumps(q.get('sufficient_chunks',[])),json.dumps(q['judgments'])))
        con.execute("UPDATE experiment_runs SET state='running' WHERE run_id=?",(run_id,))
        job_id=__import__('uuid').uuid4().hex
        con.execute("INSERT INTO experiment_jobs(job_id,run_id,kind,state,progress_total,progress_done,attempts) VALUES (?,?, 'retrieval','running',?,0,1)",(job_id,run_id,len(questions)))
    detailed=[]; by_id={d['id']:d for d in docs}
    try:
      for q in questions:
        with connect(paths.database) as state_con:
            job_state=state_con.execute("SELECT state FROM experiment_jobs WHERE job_id=?",(job_id,)).fetchone()
        if not job_state or job_state['state']!='running': break
        ranking=rank_documents(docs,q['query'],method,effective_embedding_model,embedding_client,paths.embeddings if method in {'dense','hybrid'} else None,vector_index,parameters,lexical_index)
        top=ranking[:top_k]; detailed.append({'question_id':q['question_id'],'ranking':top})
        with connect(paths.database) as item_con:
            item_con.execute('INSERT INTO retrieval_results(run_id,question_id,ranked_doc_ids_json,scores_json,ranked_chunks_json,scores_by_chunk_json) VALUES (?,?,?,?,?,?)',(run_id,q['question_id'],json.dumps([x['id'] for x in top]),json.dumps([x['score'] for x in top]),json.dumps([x['id'] for x in top]),json.dumps([{'chunk_id':x['id'],'score':x['score']} for x in top])))
            if chunk_set_id:
                for rank,item in enumerate(top,1):
                    doc=by_id[item['id']]
                    item_con.execute('INSERT INTO run_contexts(run_id,question_id,rank,chunk_set_id,chunk_id,document_id,text,source_url,score) VALUES (?,?,?,?,?,?,?,?,?)',(run_id,q['question_id'],rank,chunk_set_id,item['id'],doc['document_id'],doc.get('text',''),doc.get('source_url'),item['score']))
            item_con.execute("UPDATE experiment_jobs SET progress_done=progress_done+1,heartbeat_at=CURRENT_TIMESTAMP WHERE job_id=?",(job_id,))
      if len(detailed)<len(questions):
        with connect(paths.database) as cancelled_con:cancelled_con.execute("UPDATE experiment_runs SET state='cancelled',finished_at=CURRENT_TIMESTAMP WHERE run_id=?",(run_id,))
        return {"run_id":run_id,"state":"cancelled","completed_questions":len(detailed),"job_id":job_id}
      metrics=calculate_retrieval_metrics(detailed,questions)
      with connect(paths.database) as metric_con:
        metric_con.execute('INSERT INTO retrieval_metrics(run_id,method,recall_at_1,recall_at_5,recall_at_10,mrr,respondible_questions,precision_at_1,precision_at_5,precision_at_10,hit_at_1,hit_at_5,hit_at_10,ndcg_at_5,ndcg_at_10) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(run_id,method,metrics['recall_at_1'],metrics['recall_at_5'],metrics['recall_at_10'],metrics['mrr'],metrics['respondible_questions'],metrics['precision_at_1'],metrics['precision_at_5'],metrics['precision_at_10'],metrics['hit_at_1'],metrics['hit_at_5'],metrics['hit_at_10'],metrics['ndcg_at_5'],metrics['ndcg_at_10']))
        for detail,q in zip(detailed,questions):
            per=calculate_retrieval_metrics([detail],[q]); state='eligible' if per['respondible_questions'] else 'not_applicable'
            reason=None if state=='eligible' else ('respondibilidade parcial pendente de regra analítica' if str(q.get('answerability','')).lower() in {'parcial','partially_respondible'} else 'sem julgamento gold de evidência' if not q['references'] and not q['reference_chunks'] else 'pergunta não respondível')
            metric_con.execute("INSERT INTO retrieval_question_metrics(run_id,question_id,metric_version,coverage_state,metrics_json,not_applicable_reason) VALUES (?,?,?,?,?,?)",(run_id,q['question_id'],per['metric_version'],state,json.dumps(per,ensure_ascii=False),reason))
        metric_con.execute("UPDATE experiment_runs SET state='completed',finished_at=CURRENT_TIMESTAMP WHERE run_id=?",(run_id,))
        metric_con.execute("UPDATE experiment_jobs SET state='completed',finished_at=CURRENT_TIMESTAMP WHERE job_id=?",(job_id,))
    except Exception as exc:
      with connect(paths.database) as failure_con:
        failure_con.execute("UPDATE experiment_runs SET state='failed',error=?,finished_at=CURRENT_TIMESTAMP WHERE run_id=?",(str(exc),run_id))
        failure_con.execute("UPDATE experiment_jobs SET state='failed',error=?,finished_at=CURRENT_TIMESTAMP WHERE job_id=?",(str(exc),job_id))
      raise
    with connect(paths.database) as con:
        if documents_path is not None: register_artifact(con,run_id,'documents-input',documents_path)
        if questions_path is not None:
            register_artifact(con,run_id,'questions-input',questions_path)
        if vector_index:
            con.execute("INSERT INTO audit_events(entity_type,entity_id,action,detail_json) VALUES ('vector_index',?,'used',?)",(vector_index['index_id'],json.dumps({'run_id':run_id})))
        output=paths.outputs/f'{run_id}-retrieval.json'; output.write_text(json.dumps({'run_id':run_id,'method':method,'metrics':metrics,'results':detailed},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        register_artifact(con,run_id,'retrieval-detail',output)
    return {'run_id':run_id,'metrics':metrics,'output':str(output)}
