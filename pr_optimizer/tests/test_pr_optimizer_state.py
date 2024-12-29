import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path
from datetime import datetime

from pr_optimizer.crew import PrOptimizer
from pr_optimizer.models import PROptimizationState, AnalysisResult, PRSplit

@patch('crewai.project.crew_base.CrewBase')
class TestPrOptimizerState(unittest.TestCase):
    def setUp(self):
        # Mock the tools
        self.mock_git_tool = MagicMock()
        self.mock_code_analysis_tool = MagicMock()
        self.mock_github_api_tool = MagicMock()

        # Mock the tool collections
        self.mock_tools = {
            'git_tools': [self.mock_git_tool],
            'code_analysis': [self.mock_code_analysis_tool],
            'github_api': [self.mock_github_api_tool]
        }

        # Mock the agents config
        self.agents_config_mock = {
            'pr_analyzer': {
                'role': 'Pull Request Analyzer',
                'backstory': 'Test backstory',
                'tools': ['git_tools', 'code_analysis']
            },
            'pr_splitter': {
                'role': 'Pull Request Splitter',
                'backstory': 'Test backstory',
                'tools': ['git_tools', 'github_api']
            },
            'pr_reviewer': {
                'role': 'Pull Request Reviewer',
                'backstory': 'Test backstory',
                'tools': ['code_analysis', 'github_api']
            }
        }

        # Mock the tasks config
        self.tasks_config_mock = {
            'analyze_pr': {
                'description': 'Analyze PR',
                'expected_output': 'Analysis result',
                'agent': 'pr_analyzer'
            },
            'create_split_strategy': {
                'description': 'Create split strategy',
                'expected_output': 'Split strategy',
                'agent': 'pr_splitter',
                'depends_on': ['analyze_pr']
            },
            'validate_splits': {
                'description': 'Validate splits',
                'expected_output': 'Validation result',
                'agent': 'pr_reviewer',
                'context': ['analyze_pr', 'create_split_strategy']
            }
        }

        # Set up patches
        self.tool_collections_patcher = patch('pr_optimizer.crew.tool_collections', self.mock_tools)
        self.agents_config_patcher = patch.object(PrOptimizer, 'agents_config', self.agents_config_mock)
        self.tasks_config_patcher = patch.object(PrOptimizer, 'tasks_config', self.tasks_config_mock)
        
        # Start patches
        self.tool_collections_patcher.start()
        self.agents_config_patcher.start()
        self.tasks_config_patcher.start()

        # Initialize optimizer
        self.optimizer = PrOptimizer()
        self.pr_url = "https://github.com/test_owner/test_repo/pull/123"

    def tearDown(self):
        self.tool_collections_patcher.stop()
        self.agents_config_patcher.stop()
        self.tasks_config_patcher.stop()

    def test_initialize_state(self, _):
        """Test state initialization from PR URL"""
        self.optimizer._initialize_state(self.pr_url)
        self.assertIsNotNone(self.optimizer.state)
        self.assertEqual(self.optimizer.state.pr_url, self.pr_url)
        self.assertEqual(self.optimizer.state.owner, "test_owner")
        self.assertEqual(self.optimizer.state.repo, "test_repo")
        self.assertEqual(self.optimizer.state.pr_number, 123)
        self.assertEqual(self.optimizer.state.status, "initialized")

    def test_initialize_state_invalid_url(self, _):
        """Test state initialization with invalid PR URL"""
        invalid_url = "https://github.com/invalid/url"
        with self.assertRaises(ValueError):
            self.optimizer._initialize_state(invalid_url)

    async def test_analyze_pr_callback(self, _):
        """Test analyze_pr task callback updates state correctly"""
        self.optimizer._initialize_state(self.pr_url)
        task = self.optimizer.analyze_pr()
        
        # Mock analysis result
        analysis_result = {
            "files": {},
            "dependency_graph": {},
            "suggested_splits": [],
            "risk_assessment": {},
            "test_coverage": {}
        }
        
        # Call the callback
        await task.callback(json.dumps(analysis_result))
        
        self.assertEqual(self.optimizer.state.status, "analysis_completed")
        self.assertIsNotNone(self.optimizer.state.analysis_results)
        self.assertIn("analyze_pr", self.optimizer.state.completed_tasks)

    async def test_create_split_strategy_callback(self, _):
        """Test create_split_strategy task callback updates state correctly"""
        self.optimizer._initialize_state(self.pr_url)
        task = self.optimizer.create_split_strategy()
        
        # Mock split result
        split_result = [{
            "files": {"src/file1.py": ["change1"]},
            "rationale": "Test split",
            "branch_name": "test-branch",
            "pr_number": 124,
            "review_status": "pending"
        }]
        
        # Call the callback
        await task.callback(json.dumps(split_result))
        
        self.assertEqual(self.optimizer.state.status, "splits_created")
        self.assertEqual(len(self.optimizer.state.splits), 1)
        self.assertIn("create_split_strategy", self.optimizer.state.completed_tasks)

    async def test_validate_splits_callback(self, _):
        """Test validate_splits task callback updates state correctly"""
        self.optimizer._initialize_state(self.pr_url)
        task = self.optimizer.validate_splits()
        
        # Mock validation result
        validation_result = {
            "124": {
                "tests_pass": True,
                "lint_pass": True
            }
        }
        
        # Call the callback
        await task.callback(validation_result)
        
        self.assertEqual(self.optimizer.state.status, "validation_completed")
        self.assertIn(124, self.optimizer.state.validation_results)
        self.assertIn("validate_splits", self.optimizer.state.completed_tasks)

    @patch('pr_optimizer.crew.Crew')
    def test_kickoff_success(self, mock_crew, _):
        """Test successful kickoff updates state correctly"""
        mock_crew_instance = Mock()
        mock_crew.return_value = mock_crew_instance
        mock_crew_instance.kickoff.return_value = {"status": "success"}
        
        state = self.optimizer.kickoff(self.pr_url)
        
        self.assertEqual(state.status, "completed")
        mock_crew_instance.kickoff.assert_called_once_with(inputs={"pr_url": self.pr_url})

    @patch('pr_optimizer.crew.Crew')
    def test_kickoff_failure(self, mock_crew, _):
        """Test failed kickoff updates state correctly"""
        mock_crew_instance = Mock()
        mock_crew.return_value = mock_crew_instance
        mock_crew_instance.kickoff.side_effect = Exception("Test error")
        
        with self.assertRaises(Exception):
            self.optimizer.kickoff(self.pr_url)
        
        self.assertEqual(self.optimizer.state.status, "failed")
        self.assertEqual(len(self.optimizer.state.errors), 1)
        self.assertEqual(self.optimizer.state.errors[0]["error"], "Test error")

    def test_state_persistence_integration(self, _):
        """Test integration between PrOptimizer and StateManager"""
        from pr_optimizer.state_manager import StateManager
        
        # Initialize components
        state_manager = StateManager(storage_dir="test_state")
        
        try:
            # Run optimization with state management
            self.optimizer._initialize_state(self.pr_url)
            state_manager.save_state(self.optimizer.state)
            
            # Load state
            loaded_state = state_manager.load_state(self.pr_url)
            
            # Verify state
            self.assertIsNotNone(loaded_state)
            self.assertEqual(loaded_state.pr_url, self.pr_url)
            self.assertEqual(loaded_state.owner, "test_owner")
            self.assertEqual(loaded_state.repo, "test_repo")
            self.assertEqual(loaded_state.pr_number, 123)
        finally:
            # Cleanup
            state_path = state_manager._get_state_path(self.pr_url)
            if state_path.exists():
                state_path.unlink()
            Path("test_state").rmdir()

if __name__ == '__main__':
    unittest.main()
