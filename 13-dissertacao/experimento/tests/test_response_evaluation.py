import csv,json,tempfile,unittest
from pathlib import Path
from experiment_registry.config import ExperimentPaths
from experiment_registry.db import connect,initialize_database
from experiment_registry.registry import create_run
from experiment_registry.response_evaluation import record_response,record_human_evaluation,list_responses
class ResponseTest(unittest.TestCase):
 def test_response_citation_and_evaluation(self):
  with tempfile.TemporaryDirectory() as t:
   p=ExperimentPaths.from_environment(t); initialize_database(p)
   with connect(p.database) as c:
    run=create_run(c,'r',{'method':'bm25'}); c.execute("INSERT INTO questions(run_id,question_id,query,reference_doc_ids_json,respondible) VALUES (?,?,?,?,?)",(run,'q1','x','["d1"]',1))
    rid=record_response(c,run,'q1','Resposta',model='mock',citations=[{'document_id':'d1','chunk_id':'d1:0'}])
    eid=record_human_evaluation(c,rid,'avaliador',{'factual_correctness':2,'context_adherence':1,'citation_support':2,'proportional_completeness':1,'insufficiency_recognition':0})
    self.assertEqual(len(list_responses(c,run)),1); self.assertTrue(eid)
    with self.assertRaises(ValueError): record_human_evaluation(c,rid,'x',{'factual_correctness':3,'context_adherence':1,'citation_support':1,'proportional_completeness':1,'insufficiency_recognition':1})
if __name__=='__main__': unittest.main()
