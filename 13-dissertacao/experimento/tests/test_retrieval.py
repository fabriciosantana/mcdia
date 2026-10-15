import csv
import json
import tempfile
import unittest
from pathlib import Path

from experiment_registry.config import ExperimentPaths
from experiment_registry.db import connect, initialize_database
from experiment_registry.retrieval import calculate_retrieval_metrics, rank_documents, run_retrieval


class RetrievalTest(unittest.TestCase):
    def test_known_ranking_metrics_and_duplicate_suppression(self):
        questions=[{'question_id':'q','references':['a','b','c'],'reference_chunks':[],'judgments':{'a':2,'b':1,'c':1},'respondible':True,'answerability':'sim'}]
        results=[{'question_id':'q','ranking':[{'id':'a'},{'id':'a'},{'id':'b'},{'id':'x'}]}]
        metrics=calculate_retrieval_metrics(results,questions)
        self.assertAlmostEqual(metrics['recall_at_1'],1/3)
        self.assertAlmostEqual(metrics['recall_at_5'],2/3)
        self.assertEqual(metrics['hit_at_5'],1.0)
        self.assertAlmostEqual(metrics['precision_at_5'],2/5)
        self.assertGreaterEqual(metrics['ndcg_at_5'],0.0)
        self.assertLessEqual(metrics['ndcg_at_5'],1.0)
        no_gold=calculate_retrieval_metrics([{'question_id':'n','ranking':[]}],[{'question_id':'n','references':[],'reference_chunks':[],'respondible':True}])
        self.assertIsNone(no_gold['hit_at_5'])
        self.assertEqual(no_gold['coverage']['not_applicable'],1)

    def test_bm25_ties_follow_input_order(self):
        docs=[{'id':'first','text':'term shared'},{'id':'second','text':'term shared'}]
        ranked=rank_documents(docs,'term','bm25')
        self.assertEqual([item['id'] for item in ranked],['first','second'])

    def test_methods_persist_metrics_and_artifact(self):
        class EmbeddingItem:
            def __init__(self,index,embedding):self.index=index;self.embedding=embedding
        class Embeddings:
            def create(self,model,input):
                vectors=[[1.0,0.0] if 'segurança' in text else [0.0,1.0] for text in input]
                return type('Result',(),{'data':[EmbeddingItem(i,v) for i,v in enumerate(vectors)]})()
        client=type('Client',(),{'embeddings':Embeddings()})()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs.jsonl"
            docs.write_text('\n'.join([
                json.dumps({"id": "a", "text": "barragens mineração segurança"}),
                json.dumps({"id": "b", "text": "juros bancos economia"}),
                json.dumps({"id": "c", "text": "saúde tratamentos medicamentos"}),
            ]) + '\n', encoding="utf-8")
            questions = root / "questions.csv"
            with questions.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=["question_id", "query", "reference_doc_ids"])
                writer.writeheader()
                writer.writerow({"question_id": "q1", "query": "segurança barragens", "reference_doc_ids": "a"})
                writer.writerow({"question_id": "q2", "query": "tema ausente", "reference_doc_ids": ""})
            paths = ExperimentPaths.from_environment(root / "run")
            for method in ("bm25", "tfidf", "hybrid"):
                result = run_retrieval(paths, docs, questions, method, method, embedding_model='fake-embedding',embedding_client=client)
                self.assertEqual(result["metrics"]["respondible_questions"], 1)
                self.assertTrue(Path(result["output"]).is_file())
            with connect(paths.database) as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM experiment_runs").fetchone()[0], 3)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM retrieval_metrics").fetchone()[0], 3)

    def test_rejects_unknown_method(self):
        with self.assertRaises(ValueError):
            from experiment_registry.retrieval import rank_documents
            rank_documents([{"id": "a", "text": "x"}], "x", "unknown")
