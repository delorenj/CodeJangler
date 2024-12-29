import unittest
import sys
sys.path.append('../../src')
import json
from pathlib import Path
from pr_optimizer.state_manager import StateManager
from pr_optimizer.models import PROptimizationState

class TestStateManager(unittest.TestCase):

    def setUp(self):
        self.storage_dir = "test_state"
        self.state_manager = StateManager(storage_dir=self.storage_dir)
        self.pr_url = "https://github.com/test_owner/test_repo/pull/123"
        self.state = PROptimizationState(pr_url=self.pr_url, owner="test_owner", repo="test_repo", pr_number=123)

    def tearDown(self):
        # Clean up test files
        state_path = self.state_manager._get_state_path(self.pr_url)
        if state_path.exists():
            state_path.unlink()
        Path(self.storage_dir).rmdir()

    def test_get_state_path(self):
        expected_path = Path(self.storage_dir) / "https___github_com_test_owner_test_repo_pull_123.json"
        self.assertEqual(self.state_manager._get_state_path(self.pr_url), expected_path)

    def test_save_state(self):
        self.state_manager.save_state(self.state)
        state_path = self.state_manager._get_state_path(self.pr_url)
        self.assertTrue(state_path.exists())
        with open(state_path, "r") as f:
            data = json.load(f)
        self.assertEqual(data['pr_url'], self.pr_url)

    def test_load_state(self):
        self.state_manager.save_state(self.state)
        loaded_state = self.state_manager.load_state(self.pr_url)
        self.assertIsNotNone(loaded_state)
        self.assertEqual(loaded_state.pr_url, self.state.pr_url)
        self.assertEqual(loaded_state.owner, self.state.owner)
        self.assertEqual(loaded_state.repo, self.state.repo)
        self.assertEqual(loaded_state.pr_number, self.state.pr_number)

    def test_load_state_not_found(self):
        loaded_state = self.state_manager.load_state("https://github.com/another/repo/pull/456")
        self.assertIsNone(loaded_state)

if __name__ == '__main__':
    unittest.main()
