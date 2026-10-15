import json
import tempfile
import unittest
from pathlib import Path

from experiment_registry.config import ExperimentPaths
from experiment_registry.db import connect, initialize_database
from experiment_registry.question_bank import catalog_questions_for_run, get_catalog_question, list_catalog, save_catalog_question, seed_question_catalog
from experiment_registry.corpus import prepare_documents
from experiment_registry.question_bank import add_reference_chunk, validate_catalog_question


class QuestionBankTest(unittest.TestCase):
    def test_seed_edit_and_select_validated_questions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = ExperimentPaths.from_environment(root)
            initialize_database(paths)
            docs=root/"documents.jsonl";docs.write_text(json.dumps({"id":"doc-1","text":"Documento sintético com evidência para a pergunta do catálogo."})+"\n",encoding="utf-8")
            chunk_set=prepare_documents(paths,docs)["chunk_set_id"]
            source = root / "questions.json"
            source.write_text(json.dumps([{"question_id": "D001", "query": "Quem falou?", "category": "factual", "status": "rascunho", "reference_doc_ids": "doc-1"}], ensure_ascii=False), encoding="utf-8")
            with connect(paths.database) as connection:
                self.assertEqual(seed_question_catalog(connection, source), 1)
                self.assertEqual(len(list_catalog(connection)), 1)
                save_catalog_question(connection, {"question_id": "D001", "query": "Quem falou?", "category": "factual", "status": "revisar", "reference_doc_ids": "doc-1", "reference_chunk_ids": "doc-1:0", "respondible": True})
                add_reference_chunk(connection,"D001",chunk_set,"doc-1:0",2,True,"revisor","Trecho suficiente para resposta.","validated")
                validate_catalog_question(connection,"D001",chunk_set,"respondible","evidência direta","segmentação completa","revisor")
                self.assertEqual(get_catalog_question(connection, "D001")["status"], "validada")
                self.assertEqual([q["question_id"] for q in catalog_questions_for_run(connection)], ["D001"])


if __name__ == "__main__":
    unittest.main()
