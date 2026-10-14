import json
import tempfile
import unittest
from pathlib import Path

from experiment_registry.config import ExperimentPaths
from experiment_registry.db import connect, initialize_database
from experiment_registry.question_bank import catalog_questions_for_run, get_catalog_question, list_catalog, save_catalog_question, seed_question_catalog


class QuestionBankTest(unittest.TestCase):
    def test_seed_edit_and_select_validated_questions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = ExperimentPaths.from_environment(root)
            initialize_database(paths)
            source = root / "questions.json"
            source.write_text(json.dumps([{"question_id": "D001", "query": "Quem falou?", "category": "factual", "status": "rascunho", "reference_doc_ids": "doc-1"}], ensure_ascii=False), encoding="utf-8")
            with connect(paths.database) as connection:
                self.assertEqual(seed_question_catalog(connection, source), 1)
                self.assertEqual(len(list_catalog(connection)), 1)
                save_catalog_question(connection, {"question_id": "D001", "query": "Quem falou?", "category": "factual", "status": "validada", "reference_doc_ids": "doc-1", "reference_chunk_ids": "doc-1:0", "respondible": True})
                self.assertEqual(get_catalog_question(connection, "D001")["status"], "validada")
                self.assertEqual([q["question_id"] for q in catalog_questions_for_run(connection)], ["D001"])


if __name__ == "__main__":
    unittest.main()
