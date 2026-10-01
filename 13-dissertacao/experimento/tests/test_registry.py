import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiment_registry.config import ExperimentPaths
from experiment_registry.db import connect, initialize_database
from experiment_registry.registry import (
    create_run,
    get_run,
    list_runs,
    register_artifact,
    validate_run,
)


class RegistryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.paths = ExperimentPaths.from_environment(self.temp.name)
        initialize_database(self.paths)
        self.connection = connect(self.paths.database)

    def tearDown(self):
        self.connection.close()
        self.temp.cleanup()

    def test_create_run_and_list(self):
        run_id = create_run(self.connection, "baseline", {"method": "bm25", "k": 5})
        run = get_run(self.connection, run_id)
        self.assertEqual(run["state"], "created")
        self.assertEqual(len(list_runs(self.connection)), 1)

    def test_configuration_is_reused_but_runs_are_distinct(self):
        config = {"method": "bm25", "k": 5}
        first = create_run(self.connection, "first", config)
        second = create_run(self.connection, "second", config)
        self.assertNotEqual(first, second)
        rows = self.connection.execute("SELECT COUNT(*) FROM configurations").fetchone()[0]
        self.assertEqual(rows, 1)
        self.assertEqual(get_run(self.connection, first)["configuration_hash"], get_run(self.connection, second)["configuration_hash"])

    def test_reject_empty_configuration(self):
        with self.assertRaises(ValueError):
            create_run(self.connection, "invalid", {})

    def test_register_and_validate_artifact(self):
        run_id = create_run(self.connection, "artifact", {"method": "tfidf"})
        path = Path(self.temp.name) / "response.json"
        path.write_text(json.dumps({"answer": "ok"}), encoding="utf-8")
        register_artifact(self.connection, run_id, "response", path)
        report = validate_run(self.connection, run_id)
        self.assertTrue(report["ok"])
        path.write_text(json.dumps({"answer": "changed"}), encoding="utf-8")
        self.assertFalse(validate_run(self.connection, run_id)["ok"])

    def test_reject_missing_artifact(self):
        run_id = create_run(self.connection, "artifact", {"method": "tfidf"})
        with self.assertRaises(FileNotFoundError):
            register_artifact(self.connection, run_id, "response", Path(self.temp.name) / "missing.json")


if __name__ == "__main__":
    unittest.main()
