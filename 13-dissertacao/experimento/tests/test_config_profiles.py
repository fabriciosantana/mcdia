import tempfile
import unittest
from pathlib import Path

from experiment_registry.config import ExperimentPaths
from experiment_registry.config_profiles import get_profile, list_profiles, save_profile
from experiment_registry.db import connect, initialize_database


class ConfigurationProfileTest(unittest.TestCase):
    def test_save_update_and_read_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = ExperimentPaths.from_environment(directory)
            initialize_database(paths)
            with connect(paths.database) as connection:
                profile_id = save_profile(connection, "piloto", {"retrieval": {"method": "bm25"}})
                same_id = save_profile(connection, "piloto", {"retrieval": {"method": "hybrid"}})
                self.assertEqual(profile_id, same_id)
                self.assertEqual(len(list_profiles(connection)), 1)
                self.assertEqual(get_profile(connection, profile_id)["configuration"]["retrieval"]["method"], "hybrid")


if __name__ == "__main__":
    unittest.main()
