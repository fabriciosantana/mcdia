import json,tempfile,unittest
from pathlib import Path
from experiment_registry.config import ExperimentPaths
from experiment_registry.db import connect,initialize_database
from experiment_registry.registry import create_run
from experiment_registry.corpus import prepare_documents
from experiment_registry.openai_adapter import generate_responses
class FakeResponse:
 output_text='Resposta [a:0]'
class FakeResponses:
 def create(self,**kwargs): self.kwargs=kwargs; return FakeResponse()
class FakeClient: responses=FakeResponses()
class AdapterTest(unittest.TestCase):
 def test_fake_client_generates_and_persists(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); paths=ExperimentPaths.from_environment(root/'run'); initialize_database(paths)
   docs=root/'docs.jsonl'; docs.write_text(json.dumps({'id':'a','text':'evidência documental sintética para validar geração e contexto'})+'\n')
   chunk_set=prepare_documents(paths,docs)['chunk_set_id']
   with connect(paths.database) as c:
      run=create_run(c,'r',{'method':'bm25'}); c.execute("INSERT INTO questions(run_id,question_id,query,reference_doc_ids_json,respondible) VALUES (?,?,?,?,?)",(run,'q1','pergunta','[\"a\"]',1))
      chunk=c.execute("SELECT chunk_id,document_id,text FROM document_chunks WHERE chunk_set_id=? LIMIT 1",(chunk_set,)).fetchone()
      c.execute("INSERT INTO retrieval_results(run_id,question_id,ranked_doc_ids_json,scores_json,ranked_chunks_json,scores_by_chunk_json) VALUES (?,?,?,?,?,?)",(run,'q1',json.dumps([chunk['chunk_id']]),json.dumps([1.0]),json.dumps([chunk['chunk_id']]),json.dumps([{'chunk_id':chunk['chunk_id'],'score':1.0}])))
      c.execute("INSERT INTO run_contexts(run_id,question_id,rank,chunk_set_id,chunk_id,document_id,text,score) VALUES (?,?,?,?,?,?,?,1)",(run,'q1',1,chunk_set,chunk['chunk_id'],chunk['document_id'],chunk['text']))
   result=generate_responses(paths,run,model='mock',client=FakeClient())
   self.assertEqual(len(result['generated']),1)
   with connect(paths.database) as c: self.assertEqual(c.execute('SELECT COUNT(*) FROM responses').fetchone()[0],1)
if __name__=='__main__': unittest.main()
