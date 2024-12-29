import pytest
from unittest.mock import Mock, patch
from git import Repo
from codejangler.tools.git_tools import GitTools

@pytest.fixture
def git_tools():
    return GitTools()

@pytest.fixture
def mock_repo():
    return Mock(spec=Repo)

def test_clone_repository(git_tools, mock_repo):
    with patch('git.Repo.clone_from', return_value=mock_repo) as mock_clone:
        result = git_tools.clone_repository('https://github.com/test/repo.git', '/tmp/test')
        assert 'Successfully cloned repository' in result
        mock_clone.assert_called_once_with('https://github.com/test/repo.git', '/tmp/test')

def test_create_branch(git_tools, mock_repo):
    git_tools.repo = mock_repo
    mock_head = Mock()
    mock_repo.heads = {'main': mock_head}
    mock_head.checkout = Mock()
    
    result = git_tools.create_branch('feature-branch', 'main')
    assert 'Successfully created' in result
    mock_repo.create_head.assert_called_once_with('feature-branch', mock_head)

def test_cherry_pick_commits(git_tools, mock_repo):
    git_tools.repo = mock_repo
    commits = ['abc123', 'def456']
    
    result = git_tools.cherry_pick_commits(commits)
    assert 'Successfully cherry-picked' in result
    assert mock_repo.git.cherry_pick.call_count == len(commits)

def test_commit_changes(git_tools, mock_repo):
    git_tools.repo = mock_repo
    message = 'Test commit message'
    
    result = git_tools.commit_changes(message)
    assert 'Successfully committed changes' in result
    mock_repo.index.commit.assert_called_once_with(message)

def test_push_branch(git_tools, mock_repo):
    git_tools.repo = mock_repo
    
    result = git_tools.push_branch('feature-branch')
    assert 'Successfully pushed branch' in result
    mock_repo.git.push.assert_called_once()

def test_get_commit_diff(git_tools, mock_repo):
    git_tools.repo = mock_repo
    mock_commit = Mock()
    mock_repo.commit.return_value = mock_commit
    mock_commit.parents = [Mock()]
    
    git_tools.get_commit_diff('abc123')
    mock_repo.commit.assert_called_once_with('abc123')
    mock_commit.diff.assert_called_once()

def test_get_current_branch(git_tools, mock_repo):
    git_tools.repo = mock_repo
    mock_repo.active_branch = 'feature-branch'
    
    result = git_tools.get_current_branch()
    assert result == 'feature-branch'

def test_error_handling_no_repo(git_tools):
    result = git_tools.get_current_branch()
    assert 'No repository is currently loaded' in result
