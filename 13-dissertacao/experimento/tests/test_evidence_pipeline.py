import csv
import json
import tempfile
import unittest
from pathlib import Path

from experiment_registry.config import ExperimentPaths
from experiment_registry.corpus import chunk_documents, prepare_documents, search_chunks
from experiment_registry.db import connect, initialize_database
from experiment_registry.evaluation_analysis import agreement_report, judge_response, parse_judge_json
from experiment_registry.exports import export_run
from experiment_registry.registry import create_run
from experiment_registry.response_evaluation import record_human_evaluation, record_response
from experiment_registry.question_curation import get_question_metadata, save_question_metadata
from experiment_registry.retrieval import run_retrieval
from experiment_registry.embedding_retrieval import rank_dense
from experiment_registry.analysis import bootstrap_mean, record_error_case
from experiment_registry.evaluation_workflow import create_round


class EvidencePipelineTest(unittest.TestCase):
    def test_bootstrap_and_error_case(self):
        interval = bootstrap_mean([0, 1, 1, 2], repetitions=100, seed=42)
        self.assertEqual(interval["n"], 4); self.assertLessEqual(interval["lower"], interval["mean"]); self.assertLessEqual(interval["mean"], interval["upper"])
        with tempfile.TemporaryDirectory() as tmp:
            paths = ExperimentPaths.from_environment(tmp); initialize_database(paths)
            with connect(paths.database) as con:
                run = create_run(con, "r", {"method": "bm25"}); con.execute("INSERT INTO questions(run_id,question_id,query,reference_doc_ids_json,respondible) VALUES (?,?,?,?,?)", (run, "q", "x", "[]", 0)); response = record_response(con, run, "q", "r")
                self.assertTrue(record_error_case(con, response, "falha_recuperacao"))

    def test_dense_ranking_with_injected_client(self):
        class Embeddings:
            def create(self, model, input):
                class Item:
                    def __init__(self, index, embedding): self.index, self.embedding = index, embedding
                vectors = [[1.0, 0.0] if "segurança" in text else [0.0, 1.0] for text in input]
                return type("R", (), {"data": [Item(i, value) for i, value in enumerate(vectors)]})()
        client = type("C", (), {"embeddings": Embeddings()})()
        ranked = rank_dense([{"id": "a", "text": "segurança"}, {"id": "b", "text": "economia"}], "segurança", "mock", client)
        self.assertEqual(ranked[0]["id"], "a")

    def test_dense_embeddings_are_reused_and_invalidated(self):
        class Embeddings:
            def __init__(self): self.calls = 0
            def create(self, model, input):
                self.calls += 1
                class Item:
                    def __init__(self, index, embedding): self.index, self.embedding = index, embedding
                vectors = [[1.0, 0.0] if "segurança" in text else [0.0, 1.0] for text in input]
                return type("R", (), {"data": [Item(i, value) for i, value in enumerate(vectors)]})()
        embeddings = Embeddings()
        client = type("C", (), {"embeddings": embeddings})()
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "embeddings"
            docs = [{"id": "a", "text": "segurança"}, {"id": "b", "text": "economia"}]
            rank_dense(docs, "segurança", "mock", client, cache)
            self.assertEqual(embeddings.calls, 2)
            rank_dense(docs, "segurança", "mock", client, cache)
            self.assertEqual(embeddings.calls, 2)
            rank_dense([{"id": "a", "text": "segurança alterada"}, docs[1]], "segurança", "mock", client, cache)
            self.assertEqual(embeddings.calls, 3)

    def test_prepare_chunks_and_export_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); paths = ExperimentPaths.from_environment(root / "run")
            docs = root / "docs.jsonl"; docs.write_text(json.dumps({"id": "a", "text": "segurança barragens mineração " * 12}) + "\n", encoding="utf-8")
            questions = root / "questions.csv"
            with questions.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=["question_id", "query", "reference_doc_ids", "category", "status"]); writer.writeheader(); writer.writerow({"question_id": "q1", "query": "segurança barragens", "reference_doc_ids": "a", "category": "factual", "status": "validada"})
            prepared = prepare_documents(paths, docs, window=20, overlap=4)
            self.assertGreater(prepared["chunks"], 0)
            with connect(paths.database) as con:
                persisted = search_chunks(con, text="segurança")
                self.assertEqual(len(persisted), prepared["chunks"])
                self.assertTrue(persisted[0]["chunk_id"].startswith("a:"))
            result = run_retrieval(paths, docs, questions, "bm25", "evidence")
            with connect(paths.database) as con:
                save_question_metadata(con, result["run_id"], "q1", "factual", "validada", ["a:0"], {"a:0": 2}, "suficiente")
                self.assertEqual(get_question_metadata(con, result["run_id"], "q1")["validation_status"], "validada")
                exported = export_run(con, paths.outputs, result["run_id"])
            self.assertTrue(Path(exported["latex"]).is_file())
            self.assertIsNotNone(result["metrics"]["precision_at_5"])

    def test_judge_and_agreement(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = ExperimentPaths.from_environment(tmp); initialize_database(paths)
            docs=Path(tmp)/"docs.jsonl";docs.write_text(json.dumps({"id":"d","text":"contexto sintético com evidência documental para a avaliação"})+"\n",encoding="utf-8")
            prepared=prepare_documents(paths,docs)
            with connect(paths.database) as con:
                run = create_run(con, "r", {"method": "bm25"}); con.execute("INSERT INTO questions(run_id,question_id,query,reference_doc_ids_json,respondible) VALUES (?,?,?,?,?)", (run, "q", "x", '["d"]', 1))
                chunk=con.execute("SELECT chunk_id,document_id,text FROM document_chunks WHERE chunk_set_id=? LIMIT 1",(prepared["chunk_set_id"],)).fetchone()
                con.execute("INSERT INTO run_contexts(run_id,question_id,rank,chunk_set_id,chunk_id,document_id,text,score) VALUES (?,?,?,?,?,?,?,1)",(run,"q",1,prepared["chunk_set_id"],chunk["chunk_id"],chunk["document_id"],chunk["text"]))
                response = record_response(con, run, "q", "resposta")
                record_human_evaluation(con, response, "h", {field: 2 for field in ("factual_correctness", "context_adherence", "citation_support", "proportional_completeness", "insufficiency_recognition")})
                class Responses:
                    def create(self, **kwargs):
                        class R: output_text = json.dumps({field: 2 for field in ("factual_correctness", "context_adherence", "citation_support", "proportional_completeness", "insufficiency_recognition")})
                        return R()
                class Client: responses = Responses()
                round_id=create_round(con,run,"juiz de teste","judge",True,"mock")
                judge_response(con, response, "mock", Client(),round_id=round_id)
                report = agreement_report(con, run)
            self.assertEqual(report["paired_responses"], 1)
            self.assertEqual(report["dimensions"]["citation_support"]["exact_agreement"], 1.0)
            self.assertEqual(parse_judge_json('{"factual_correctness":2,"context_adherence":1,"citation_support":0,"proportional_completeness":2,"insufficiency_recognition":1}')['scores']['citation_support'], 0)


if __name__ == "__main__":
    unittest.main()
