import json,tempfile,unittest
from pathlib import Path
from experiment_registry.config import ExperimentPaths
from experiment_registry.db import connect,initialize_database
from experiment_registry.registry import create_run
from experiment_registry.openai_adapter import generate_responses
class FakeResponse:
 output_text='Resposta [a]'
class FakeResponses:
 def create(self,**kwargs): self.kwargs=kwargs; return FakeResponse()
class FakeClient: responses=FakeResponses()
class AdapterTest(unittest.TestCase):
 def test_fake_client_generates_and_persists(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); paths=ExperimentPaths.from_environment(root/'run'); initialize_database(paths)
   docs=root/'docs.jsonl'; docs.write_text(json.dumps({'id':'a','text':'evidência'})+'\n')
   with connect(paths.database) as c:
    run=create_run(c,'r',{'method':'bm25'}); c.execute("INSERT INTO questions VALUES (?,?,?,?,?)",(run,'q1','pergunta','[\\"a\\"]',1)); c.execute("INSERT INTO retrieval_results VALUES (?,?,?,?)",(run,'q1',json.dumps(['a']),json.dumps([1.0])))
   result=generate_responses(paths,run,docs,model='mock',client=FakeClient())
   self.assertEqual(len(result),1)
   with connect(paths.database) as c: self.assertEqual(c.execute('SELECT COUNT(*) FROM responses').fetchone()[0],1)
if __name__=='__main__': unittest.main()
