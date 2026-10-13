import csv
import json
import tempfile
import unittest
from pathlib import Path

from experiment_registry.config import ExperimentPaths
from experiment_registry.db import connect, initialize_database
from experiment_registry.retrieval import run_retrieval


class RetrievalTest(unittest.TestCase):
    def test_methods_persist_metrics_and_artifact(self):
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
                result = run_retrieval(paths, docs, questions, method, method)
                self.assertEqual(result["metrics"]["respondible_questions"], 1)
                self.assertTrue(Path(result["output"]).is_file())
            with connect(paths.database) as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM experiment_runs").fetchone()[0], 3)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM retrieval_metrics").fetchone()[0], 3)

    def test_rejects_unknown_method(self):
        with self.assertRaises(ValueError):
            from experiment_registry.retrieval import rank_documents
            rank_documents([{"id": "a", "text": "x"}], "x", "unknown")
