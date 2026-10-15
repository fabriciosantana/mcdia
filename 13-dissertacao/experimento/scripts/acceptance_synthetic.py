from pathlib import Path
import hashlib, json, os, sqlite3, sys, tempfile
from types import SimpleNamespace
import numpy as np
REPO_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from experiment_registry.config import ExperimentPaths
from experiment_registry.db import connect, initialize_database
from experiment_registry.corpus import prepare_documents, search_chunks, chunk_context
from experiment_registry.question_bank import save_catalog_question, create_battery, add_battery_member, add_reference_chunk, validate_catalog_question, freeze_battery, seed_question_catalog, import_pilot_battery
from experiment_registry.vector_index import create_index, set_index_state
from experiment_registry.embedding_retrieval import EmbeddingStore, rank_chroma
from experiment_registry.plans import create_plan
from experiment_registry.retrieval import run_retrieval
from experiment_registry.openai_adapter import generate_responses
from experiment_registry.evaluation_workflow import register_evaluator, authenticate_evaluator, create_round, assign_responses, blind_assignments, submit_assignment, add_claim, annotate_claim_evidence, ensure_protocol, save_analysis_protocol
from experiment_registry.evaluation_analysis import judge_response
from experiment_registry.response_evaluation import record_response
from experiment_registry.dissertation_reporting import build_report, export_report, create_audit_bundle, restore_audit_bundle
from experiment_registry.exports import export_run

base=Path(tempfile.mkdtemp(prefix='rag-acceptance-'))
# Exercise the shipped 200-question catalog and map the 24-item pilot by source ID in isolation.
pilot_root=base/'pilot-registry';pilot_paths=ExperimentPaths.from_environment(pilot_root);pilot_paths.ensure_directories();initialize_database(pilot_paths)
pilot_source=REPO_ROOT.parent/'dados'/'piloto'/'bateria_piloto_dissertacao_24_v1.json'
catalog_source=REPO_ROOT.parent/'dados'/'piloto'/'banco_perguntas_dissertacao_v1.json'
with connect(pilot_paths.database) as con:
    assert seed_question_catalog(con,catalog_source)==200
    pilot=import_pilot_battery(con,pilot_source)
    assert pilot['mapped']==24 and pilot['unmatched']==[]
    assert con.execute('SELECT COUNT(*) FROM question_catalog').fetchone()[0]==200
    assert con.execute('SELECT COUNT(*) FROM battery_members WHERE battery_id=?',(pilot['battery_id'],)).fetchone()[0]==24
print('PASS shipped question catalog and pilot mapped by provenance without duplicating questions')

root=base/'project'; paths=ExperimentPaths.from_environment(root); paths.ensure_directories()
print('TEMP_ROOT',base)
# Create a real pre-migration 001-008 registry and legacy rows, then apply 009-015 via app initializer.
with sqlite3.connect(paths.database) as raw:
    for migration in sorted(paths.migrations.glob('[0-9][0-9][0-9]_*.sql')):
        version=int(migration.name[:3])
        if version>8: break
        raw.executescript(migration.read_text())
        raw.execute('CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, filename TEXT NOT NULL, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
        raw.execute('INSERT INTO schema_migrations(version,filename) VALUES (?,?)',(version,migration.name))
    raw.execute("INSERT INTO document_chunks(chunk_id,document_id,text,metadata_json,source_sha256) VALUES ('legacy:0','legacy','texto legado preservado','{}','legacysha')")
initialize_database(paths)
with connect(paths.database) as con:
    assert [r[0] for r in con.execute('SELECT version FROM schema_migrations ORDER BY version')][-7:]==list(range(9,16))
    assert con.execute('SELECT COUNT(*) FROM document_chunks').fetchone()[0]==1
    assert con.execute('SELECT COUNT(*) FROM migration_reconciliation').fetchone()[0]==1
assert (paths.artifacts/'experiment_registry-pre-versioned-corpus.sqlite3').exists()
print('PASS migrations 009-015, legacy chunk preservation, backup, reconciliation')

# Make a corpus with integral, summary-only, and missing text records.
import pandas as pd
source=base/'synthetic.parquet'
long_tokens=('dados orçamento transparência parlamento evidência pública orçamento anual debate comissão relatório receita despesa política pública '\
             'fiscalização mandato sessão documento oficial fonte verificável análise legislativa informação detalhada '.split())
long_text='ultrazeta '+' '.join(long_tokens*5)
frame=pd.DataFrame([
 {'id':'d1','TextoDiscursoIntegral':long_text,'Resumo':'','Data':'2024-03-12','NomeAutor':'Ana','URL':'https://example.test/d1','Casa':'Câmara'},
 {'id':'d2','TextoDiscursoIntegral':None,'Resumo':'debate sobre dados públicos e orçamento parlamentar em comissão.','Data':'2023-06-01','NomeAutor':'Beto','URL':'https://example.test/d2','Casa':'Senado'},
 {'id':'d3','TextoDiscursoIntegral':None,'Resumo':None,'Data':None,'NomeAutor':None,'URL':None,'Casa':None},
])
frame.to_parquet(source)
corpus=prepare_documents(paths,source,window=32,overlap=8)
with connect(paths.database) as con:
    assert con.execute('SELECT COUNT(*) FROM documents WHERE corpus_version_id=?',(corpus['corpus_version_id'],)).fetchone()[0]==3
    assert con.execute("SELECT COUNT(*) FROM documents WHERE corpus_version_id=? AND text_source='resumo'",(corpus['corpus_version_id'],)).fetchone()[0]==1
    assert con.execute("SELECT COUNT(*) FROM documents WHERE corpus_version_id=? AND text_source='ausente'",(corpus['corpus_version_id'],)).fetchone()[0]==1
    chunks=con.execute('SELECT chunk_id,document_id FROM document_chunks WHERE chunk_set_id=? ORDER BY chunk_id',(corpus['chunk_set_id'],)).fetchall()
    d1chunk=next(r['chunk_id'] for r in chunks if r['document_id']=='d1')
    d2chunk=next(r['chunk_id'] for r in chunks if r['document_id']=='d2')
print('PASS corpus version, integral/summary/missing text and persistent chunks')
with connect(paths.database) as con:
    filtered=search_chunks(con,author='Ana',date_from='2024-01-01',date_to='2024-12-31',chunk_set_id=corpus['chunk_set_id'],limit=1,offset=0)
    assert filtered and all(item['document_id']=='d1' for item in filtered)
    page=search_chunks(con,chunk_set_id=corpus['chunk_set_id'],limit=2,offset=1)
    assert len(page)==2
    assert chunk_context(con,corpus['chunk_set_id'],d1chunk,radius=1)
repeat=prepare_documents(paths,source,window=32,overlap=8)
assert repeat['chunk_set_id']==corpus['chunk_set_id'] and repeat['persisted_chunks']==corpus['chunks']
print('PASS corpus filters, numeric pagination, neighboring context and idempotent reimport')

# Re-import changed source content under the same document IDs with a second segmentation.
with connect(paths.database) as con:
    first_chunks={r['chunk_id']:r['text'] for r in con.execute('SELECT chunk_id,text FROM document_chunks WHERE chunk_set_id=?',(corpus['chunk_set_id'],))}
changed=frame.copy();changed.loc[0,'TextoDiscursoIntegral']=long_text+' alteração de fonte para teste de versionamento.'
source_v2=base/'synthetic-v2.parquet';changed.to_parquet(source_v2)
corpus_v2=prepare_documents(paths,source_v2,window=40,overlap=8)
with connect(paths.database) as con:
    preserved={r['chunk_id']:r['text'] for r in con.execute('SELECT chunk_id,text FROM document_chunks WHERE chunk_set_id=?',(corpus['chunk_set_id'],))}
    assert first_chunks==preserved
    assert con.execute('SELECT COUNT(*) FROM corpus_versions').fetchone()[0]>=2
    assert corpus_v2['chunk_set_id']!=corpus['chunk_set_id']
invalid=base/'duplicate-ids.jsonl'
invalid.write_text('{"id":"same","text":"texto valido para o primeiro documento."}\\n{"id":"same","text":"texto valido para o segundo documento."}\\n',encoding='utf-8')
with connect(paths.database) as con: versions_before=con.execute('SELECT COUNT(*) FROM corpus_versions').fetchone()[0]
try: prepare_documents(paths,invalid)
except ValueError: pass
else: raise AssertionError('fontes com IDs repetidos devem falhar antes da importação')
with connect(paths.database) as con: assert con.execute('SELECT COUNT(*) FROM corpus_versions').fetchone()[0]==versions_before
print('PASS version coexistence, same-ID source change, immutable old chunks, and invalid-source rollback')

# Curate answerable, partial, and unanswerable questions; validate and freeze the battery.
with connect(paths.database) as con:
    qdata=[
        ('Q-S','ultrazeta','factual simples',d1chunk,'sim',True,'respondible'),
        ('Q-C','Como os debates relacionam orçamento e fiscalização parlamentar?','síntese complexa',d2chunk,'sim',True,'respondible'),
        ('Q-P','O que os documentos indicam parcialmente sobre transparência?','parcial',d1chunk, 'parcial',True,'partially_respondible'),
        ('Q-N','Qual foi o resultado sem evidência disponível?','não respondível','', 'nao',False,'not_respondible'),
    ]
    bid=create_battery(con,'Aceitação sintética','verificação de fluxo ponta a ponta')
    for position,(qid,query,category,gold,answerability,respondible,decision) in enumerate(qdata,1):
        save_catalog_question(con,{'question_id':qid,'query':query,'category':category,'source_category':category,'status':'revisar','difficulty':'medium','answerability':answerability,'respondible':respondible,'eligible':True,'reference_doc_ids':['d1' if qid=='Q-S' else 'd2'] if gold else [],'expected_answer_criteria':'usar apenas evidência documental'})
        if qid=='Q-S':
            save_catalog_question(con,{'question_id':qid,'query':query,'category':category})
            assert con.execute("SELECT expected_answer_criteria FROM question_catalog WHERE question_id=?",(qid,)).fetchone()[0]=='usar apenas evidência documental'
        add_battery_member(con,bid,qid,split='evaluation',position=position)
        if gold:
            add_reference_chunk(con,qid,corpus['chunk_set_id'],gold,1 if decision=='partially_respondible' else 2,decision=='respondible','curador-test','Trecho de referência sintético; suficiência adequada ao rótulo.','validated')
        try: add_reference_chunk(con,qid,corpus['chunk_set_id'],'chunk-inexistente',2,True,'curador-test','deve rejeitar chunk inexistente','validated')
        except ValueError: pass
        else: raise AssertionError('referência a chunk inexistente deveria ser rejeitada')
        validate_catalog_question(con,qid,corpus['chunk_set_id'],decision,'decisão sintética documentada','todos os chunks do corpus desta versão','curador-test')
    freeze_battery(con,bid,corpus['chunk_set_id'])
    frozen_revision=con.execute("SELECT question_revision FROM battery_members WHERE battery_id=? AND question_id='Q-S'",(bid,)).fetchone()[0]
    save_catalog_question(con,{'question_id':'Q-S','query':'ultrazeta versão revisada','category':'factual simples'})
    assert con.execute("SELECT question_revision FROM battery_members WHERE battery_id=? AND question_id='Q-S'",(bid,)).fetchone()[0]==frozen_revision
    assert json.loads(con.execute("SELECT question_json FROM question_revisions WHERE question_id='Q-S' AND revision=?",(frozen_revision,)).fetchone()[0])['query']=='ultrazeta'
    try: add_battery_member(con,bid,'Q-S',split='evaluation',position=10)
    except sqlite3.IntegrityError: pass
    else: raise AssertionError('membros de bateria congelada devem ser imutáveis')
print('PASS answerable/partial/unanswerable curation, partial-edit preservation, evidence validation and frozen battery')

# Build a persistent Chroma index with deterministic local vectors (no API call).
def vector_for(text):
    v=np.zeros(2048,dtype=np.float32)
    for token in text.lower().split():
        h=hashlib.sha256(token.encode()).digest(); idx=int.from_bytes(h[:2],'big')%len(v);v[idx]+=1 if h[2]%2 else -1
    if not v.any():v[0]=1
    return v/np.linalg.norm(v)
class FakeEmbeddingProvider:
    def __init__(self,cancel_database=None):self.embeddings=self;self.cancel_database=cancel_database
    def create(self,model,input):
        if self.cancel_database:
            with sqlite3.connect(self.cancel_database) as db:
                db.execute("UPDATE experiment_jobs SET state='cancelled',finished_at=CURRENT_TIMESTAMP WHERE kind='index-build' AND state='running'")
        return SimpleNamespace(data=[SimpleNamespace(index=i,embedding=vector_for(text).tolist()) for i,text in enumerate(input)])
embedding_client=FakeEmbeddingProvider()
index=create_index(paths,corpus['chunk_set_id'],'fake-embedding-v1',client=embedding_client,batch_size=2)
assert index['count']==corpus['chunks'] and index['dimensions']==2048
with connect(paths.database) as con:
    index_state=con.execute('SELECT state,total_items,completed_items FROM vector_indexes WHERE index_id=?',(index['index_id'],)).fetchone()
    assert tuple(index_state)==('completed',corpus['chunks'],corpus['chunks'])
assert EmbeddingStore(paths.embeddings)._client().get_collection(index['collection_name']).count()==index['count']
collection=EmbeddingStore(paths.embeddings)._client().get_collection(index['collection_name'])
query_vector=vector_for('ultrazeta').tolist()
direct=collection.query(query_embeddings=[query_vector],n_results=index['count'],include=['metadatas','distances'])
expected=list(zip(direct['ids'][0],[1.0-float(distance) for distance in direct['distances'][0]]))
actual=rank_chroma(paths.embeddings,index['collection_name'],'ultrazeta','fake-embedding-v1',client=embedding_client,limit=index['count'])
assert [item['id'] for item in actual]==[item[0] for item in expected]
assert all(np.isclose(item['score'],score) for item,(_,score) in zip(actual,expected))
set_index_state(paths,index['index_id'],'archived');set_index_state(paths,index['index_id'],'completed')
print('PASS persistent Chroma build and SQLite manifest')

# Interrupt one index build and prove a subsequent invocation resumes missing vectors.
interrupted=create_index(paths,corpus_v2['chunk_set_id'],'fake-resumable-embedding-v1',client=FakeEmbeddingProvider(paths.database),batch_size=2)
assert interrupted['state']=='cancelled'
resumed=create_index(paths,corpus_v2['chunk_set_id'],'fake-resumable-embedding-v1',client=embedding_client,batch_size=2)
assert resumed['count']==corpus_v2['chunks'] and resumed['dimensions']==2048
print('PASS interrupted Chroma index resumes and completes without deleting prior vectors')

# Run BM25, dense, and hybrid against the same frozen battery and chunk set.
run_ids={}
for method in ('bm25','dense','hybrid'):
    conf={'retrieval':{'method':method,'k':5,'embedding_model':'fake-embedding-v1' if method!='bm25' else None,'parameters':{'dense_candidate_k':20,'rrf_k':60,'k1':1.5,'b':0.75}}}
    with connect(paths.database) as con: plan=create_plan(con,'acceptance-'+method,bid,corpus['chunk_set_id'],conf,index['index_id'] if method!='bm25' else None,'synthetic-v1')
    if method=='dense':
        with connect(paths.database) as con:
            try: con.execute('DELETE FROM vector_indexes WHERE index_id=?',(index['index_id'],))
            except sqlite3.IntegrityError: pass
            else: raise AssertionError('índices vinculados a planos não podem ser excluídos')
    result=run_retrieval(paths,name='acceptance-'+method,plan_id=plan,embedding_client=embedding_client)
    run_ids[method]=result['run_id']
    assert result['metrics']['respondible_questions']==2
    with connect(paths.database) as con:
        assert con.execute('SELECT COUNT(*) FROM run_contexts WHERE run_id=?',(result['run_id'],)).fetchone()[0]>=2
        assert con.execute('SELECT COUNT(*) FROM run_question_snapshots WHERE run_id=?',(result['run_id'],)).fetchone()[0]==4
        coverage={r['question_id']:r['coverage_state'] for r in con.execute('SELECT question_id,coverage_state FROM retrieval_question_metrics WHERE run_id=?',(result['run_id'],))}
        assert sum(state=='eligible' for state in coverage.values())==2
        assert sum(state=='not_applicable' for state in coverage.values())==2
        if method=='bm25':
            q_metrics=json.loads(con.execute("SELECT metrics_json FROM retrieval_question_metrics WHERE run_id=? AND question_id='Q-S'",(result['run_id'],)).fetchone()[0])
            # The unique token occurs only in the first gold chunk: hand-computed metrics are R@1=1, Hit@1=1, P@5=1/5, nDCG@5=1.
            assert q_metrics['recall_at_1']==1.0 and q_metrics['hit_at_1']==1.0
            assert q_metrics['precision_at_5']==0.2 and q_metrics['ndcg_at_5']==1.0
        if method in {'dense','hybrid'}:
            ranking=json.loads(con.execute("SELECT ranked_chunks_json FROM retrieval_results WHERE run_id=? AND question_id='Q-S'",(result['run_id'],)).fetchone()[0])
            assert d1chunk in ranking
print('PASS BM25, dense and hybrid runs, snapshots, contexts and metrics')

# Generate responses with a fake provider; use citations to the top retrieved context.
class FakeResponses:
    def __init__(self,mode,fail_first=False,cancel_database=None): self.mode=mode;self.fail_first=fail_first;self.cancel_database=cancel_database;self.calls=0;self.requests=[]
    def create(self,**kwargs):
        self.calls+=1
        self.requests.append(kwargs)
        if self.fail_first and self.calls==1: raise RuntimeError('falha sintética antes de resposta confirmada')
        if self.mode=='generation':
            import re
            ids=re.findall(r'\[Documento ([^\]]+)\]',kwargs['input'])
            if self.cancel_database:
                with sqlite3.connect(self.cancel_database) as db:
                    db.execute("UPDATE experiment_jobs SET state='cancelled',error='cancelamento sintético',finished_at=CURRENT_TIMESTAMP WHERE kind='generation' AND state='running'")
            return SimpleNamespace(output_text=f"O contexto descreve evidências sobre orçamento e fiscalização. [{ids[0]}] [citacao-inexistente]",usage={'input_tokens':50,'output_tokens':12})
        payload={k:2 for k in ('factual_correctness','context_adherence','citation_support','proportional_completeness','insufficiency_recognition')};payload['notes']='julgamento sintético'
        return SimpleNamespace(output_text=json.dumps(payload))
class FakeClient:
    def __init__(self,mode,fail_first=False,cancel_database=None):self.responses=FakeResponses(mode,fail_first,cancel_database)
run_id=run_ids['hybrid']
generation_client=FakeClient('generation')
generated=generate_responses(paths,run_id,model='fake-llm-v1',client=generation_client,parameters={'temperature':0},attempt=1,max_items=10,max_total_prompt_tokens=10000,max_duration_seconds=30)
assert len(generated['generated'])==4
with connect(paths.database) as con:
    responses=[dict(r) for r in con.execute('SELECT * FROM responses WHERE run_id=? AND generation_attempt=1',(run_id,))]
    assert all(r['prompt_text'] and r['context_hash'] and r['usage_json'] for r in responses)
    assert con.execute("SELECT COUNT(*) FROM citations WHERE response_id IN (SELECT response_id FROM responses WHERE run_id=?) AND validity='valid'",(run_id,)).fetchone()[0]>=2
    assert con.execute("SELECT COUNT(*) FROM citations WHERE response_id IN (SELECT response_id FROM responses WHERE run_id=?) AND validity='unknown'",(run_id,)).fetchone()[0]==4
assert all(request['model']=='fake-llm-v1' and request['temperature']==0 for request in generation_client.responses.requests)
print('PASS deterministic response generation, context snapshots, valid and invalid citation persistence')

# Uncertain provider outcome is visible, blocks implicit retry, and retries only after confirmation.
try: generate_responses(paths,run_id,model='fake-llm-v1',client=FakeClient('generation',fail_first=True),parameters={'temperature':0},attempt=2,max_items=10,max_total_prompt_tokens=10000,max_duration_seconds=30)
except RuntimeError: pass
else: raise AssertionError('falha do provedor deveria deixar item incerto')
try: generate_responses(paths,run_id,model='fake-llm-v1',client=FakeClient('generation'),parameters={'temperature':0},attempt=2,max_items=10)
except ValueError as exc: assert 'incerto' in str(exc)
else: raise AssertionError('retentativa de item incerto requer confirmação explícita')
retry=generate_responses(paths,run_id,model='fake-llm-v1',client=FakeClient('generation'),parameters={'temperature':0},attempt=2,max_items=10,retry_uncertain=True)
assert len(retry['generated'])==4
print('PASS uncertain generation is persisted, implicit retry blocked, explicit retry succeeds')

budget_provider=FakeClient('generation')
try: generate_responses(paths,run_id,model='fake-llm-v1',client=budget_provider,parameters={'temperature':0},attempt=3,max_total_prompt_tokens=1)
except ValueError as exc: assert 'preflight' in str(exc)
else: raise AssertionError('teto de tokens deve bloquear a operação antes das chamadas')
assert budget_provider.responses.calls==0
print('PASS token budget preflight blocks calls before worker creation')

cancelled=generate_responses(paths,run_id,model='fake-llm-v1',client=FakeClient('generation',cancel_database=paths.database),parameters={'temperature':0},attempt=3,max_items=10)
assert len(cancelled['generated'])==1
continued=generate_responses(paths,run_id,model='fake-llm-v1',client=FakeClient('generation'),parameters={'temperature':0},attempt=3,max_items=10)
assert len(continued['generated'])==3
with connect(paths.database) as con:
    assert con.execute("SELECT COUNT(*) FROM responses WHERE run_id=? AND generation_attempt=3",(run_id,)).fetchone()[0]==4
    assert con.execute("SELECT COUNT(*) FROM experiment_jobs WHERE run_id=? AND kind='generation' AND state='cancelled'",(run_id,)).fetchone()[0]==1
print('PASS cancelled generation preserves completed items and resumes remaining queue')

# Missing frozen context blocks generation before any external provider call.
with connect(paths.database) as con:
    broken_run=run_ids['bm25'];broken_q=con.execute('SELECT question_id FROM questions WHERE run_id=? ORDER BY question_id LIMIT 1',(broken_run,)).fetchone()[0]
    con.execute('DELETE FROM run_contexts WHERE run_id=? AND question_id=?',(broken_run,broken_q))
    broken_judge_round=create_round(con,broken_run,'juiz sem contexto','judge',True,'fake-judge-v1')
blocked_provider=FakeClient('generation')
try: generate_responses(paths,broken_run,model='fake-llm-v1',client=blocked_provider,parameters={'temperature':0})
except ValueError as exc: assert 'contexto' in str(exc)
else: raise AssertionError('contexto ausente deve bloquear geração')
assert blocked_provider.responses.calls==0
blocked_judge=FakeClient('judge')
with connect(paths.database) as con:
    broken_response=record_response(con,broken_run,broken_q,'resposta sintética sem contexto')
    try: judge_response(con,broken_response,'fake-judge-v1',blocked_judge,round_id=broken_judge_round)
    except ValueError as exc: assert 'contexto recuperado ausente' in str(exc)
    else: raise AssertionError('contexto ausente deve bloquear o juiz')
assert blocked_judge.responses.calls==0
print('PASS missing context blocks generation and judge before provider call')

# Human blind rounds, independent reviewers, claim-level evidence, judge, then reporting.
with connect(paths.database) as con:
    p_id,_=ensure_protocol(con)
    h1={'H1':'H1 synthetic','H2':'H2 synthetic','H3':'H3 synthetic'}
    rules={'complexity_groups':{'simple':['factual simples'],'complex':['síntese complexa']},'document_length_bins_chars':[100,2000],'bootstrap_unit':'question','kappa_weights':'linear'}
    p_id=save_analysis_protocol(con,p_id,h1,rules,True)
    human_round=create_round(con,run_id,'rodada-cega-sintética','human',True)
    evaluator_ids=[register_evaluator(con,'revisor-a',True,'access-code-reviewer-a-123'),register_evaluator(con,'revisor-b',True,'access-code-reviewer-b-123')]
    assert authenticate_evaluator(con,'access-code-reviewer-a-123')['evaluator_id']==evaluator_ids[0]
    assert authenticate_evaluator(con,'wrong-access-code') is None
    response_ids=[r['response_id'] for r in responses]
    for eid in evaluator_ids:
        assert assign_responses(con,human_round,eid,response_ids)==4
        assert len(blind_assignments(con,human_round,eid))==4
        for assignment in con.execute("SELECT assignment_id,response_id FROM evaluation_assignments WHERE round_id=? AND evaluator_id=?",(human_round,eid)).fetchall():
            blind=next(a for a in blind_assignments(con,human_round,eid) if a['assignment_id']==assignment['assignment_id'])
            assert set(blind)=={'assignment_id','response_id','query','answer'}
            if eid==evaluator_ids[0] and assignment['response_id']==response_ids[0]:
                try: submit_assignment(con,assignment['assignment_id'],eid,{'factual_correctness':3},'nota inválida')
                except ValueError: pass
                else: raise AssertionError('nota fora de 0–2 deve ser rejeitada')
            submit_assignment(con,assignment['assignment_id'],eid,{k:2 for k in ('factual_correctness','context_adherence','citation_support','proportional_completeness','insufficiency_recognition')},'anotação sintética')
    judge_round=create_round(con,run_id,'juiz-sintético','judge',True,'fake-judge-v1')
    for response in responses: judge_response(con,response['response_id'],'fake-judge-v1',FakeClient('judge'),round_id=judge_round,attempt=1)
    # Add one claim and its citation support judgment per response and reviewer.
    for response in responses:
        claim_id=add_claim(con,response['response_id'],1,'O contexto sustenta a afirmação sobre orçamento.')
        citation=con.execute('SELECT citation_id FROM citations WHERE response_id=? AND validity=\'valid\' LIMIT 1',(response['response_id'],)).fetchone()[0]
        for eid in evaluator_ids: annotate_claim_evidence(con,claim_id,citation,'complete',eid,'citação adequada',human_round)
    adjudicator=register_evaluator(con,'adjudicador',True,'access-code-adjudicator-123')
    adjudication_round=create_round(con,run_id,'adjudicação-sintética','adjudication',True)
    assert assign_responses(con,adjudication_round,adjudicator,[response_ids[0]])==1
    adjudication_assignment=con.execute('SELECT assignment_id FROM evaluation_assignments WHERE round_id=? AND evaluator_id=?',(adjudication_round,adjudicator)).fetchone()[0]
    adjudicated=submit_assignment(con,adjudication_assignment,adjudicator,{k:1 for k in ('factual_correctness','context_adherence','citation_support','proportional_completeness','insufficiency_recognition')},'adjudicação sintética')
    assert con.execute('SELECT COUNT(*) FROM evaluation_adjudication_links WHERE adjudicated_evaluation_id=?',(adjudicated,)).fetchone()[0]==2
    rules.update({'human_round_id':human_round,'judge_round_id':judge_round})
    p_id=save_analysis_protocol(con,p_id,h1,rules,True)
    con.execute('SAVEPOINT missing_score_report')
    con.execute("DELETE FROM human_evaluations WHERE response_id IN (SELECT response_id FROM responses WHERE run_id=? AND question_id='Q-N')",(run_id,))
    missing_report=build_report(con,[run_id],p_id)
    assert missing_report['H2'][run_id]['by_category']['não respondível']['n']==0
    assert missing_report['H2'][run_id]['by_category']['não respondível']['missing_evaluations']==1
    con.execute('ROLLBACK TO missing_score_report');con.execute('RELEASE missing_score_report')
    report=build_report(con,[run_id],p_id)
    assert len(report['H1']['cases'])==4
    assert report['H3'][run_id]['paired_responses']==4
    assert report['H1']['coverage']['annotated_cases']==4
    assert report['H1']['coverage']['without_reference_gold']==1
    assert report['H1']['coverage']['without_sufficient_gold']==2
    assert report['H3'][run_id]['dimensions']['factual_correctness']['exact_agreement']==1.0
    assert report['H3'][run_id]['dimensions']['factual_correctness']['weighted_kappa'] is None
    report_files=export_report(report,paths.outputs/'acceptance-report')
    run_files=export_run(con,paths.outputs/'acceptance-run',run_id)
    con.execute('INSERT INTO analysis_reports(report_id,run_id,protocol_id,report_json) VALUES (?,?,?,?)',('report-synthetic',run_id,p_id,json.dumps(report,ensure_ascii=False)))
print('PASS blinded reviewers, judge, invalid-score rejection, adjudication links, claim evidence and H1-H3 report')

# Compile report TeX and exercise a reproducible DB+Chroma backup/restore.
tex=report_files['latex']
import subprocess
compiled=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory',str(paths.outputs/'acceptance-report'),str(tex)],text=True,capture_output=True)
assert compiled.returncode==0,compiled.stdout[-2000:]+compiled.stderr[-1000:]
assert Path(run_files['latex']).exists()
bundle=paths.outputs/'acceptance-bundle.zip';create_audit_bundle(paths,[run_id],bundle)
restored=base/'restored';restore_audit_bundle(bundle,restored)
with sqlite3.connect(restored/'registry.sqlite') as con:
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert con.execute('SELECT COUNT(*) FROM responses WHERE run_id=?',(run_id,)).fetchone()[0]==12
    assert con.execute('SELECT access_hash FROM evaluator_registry LIMIT 1').fetchone()[0] is None
    assert con.execute('SELECT COUNT(*) FROM human_evaluations').fetchone()[0]==9
with open(restored/'manifest.json',encoding='utf-8') as f: manifest=json.load(f)
assert manifest['secrets_included'] is False
import chromadb
restored_chroma=chromadb.PersistentClient(path=str(restored/'chromadb'))
assert restored_chroma.get_collection(index['collection_name']).count()==index['count']
print('PASS standalone LaTeX compilation; audit bundle restore; SQLite integrity/anonymization; Chroma collection restored')
# Render the complete Streamlit dashboard over the isolated acceptance database.
os.environ['EXPERIMENTO_ROOT']=str(root)
from streamlit.testing.v1 import AppTest
app=AppTest.from_file(str(REPO_ROOT/'dashboard'/'app.py'),default_timeout=60).run()
assert not app.exception, '\n'.join(str(e.message) for e in app.exception)
labels={tab.label for tab in app.tabs}
assert {'Visão geral','Banco de perguntas','Baterias','Documentos e chunks','Experimentos','Avaliação humana'} <= labels
print('PASS Streamlit dashboard renders all primary workflow tabs')
print('ACCEPTANCE_OK',json.dumps({'root':str(base),'run_ids':run_ids,'corpus':corpus,'report_tex':str(tex),'bundle':str(bundle)},ensure_ascii=False))
