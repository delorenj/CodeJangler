from typing import List, Optional
from git import Repo
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class GitTools(BaseTool):
    """A collection of tools for Git operations."""
    
    name: str = "git_tools"
    description: str = "Tools for performing Git operations like cloning repos, creating branches, and managing commits"

    def __init__(self):
        super().__init__()
        self.repo = None

    def clone_repository(self, url: str, path: str) -> str:
        """Clone a repository to the specified path."""
        try:
            self.repo = Repo.clone_from(url, path)
            return f"Successfully cloned repository to {path}"
        except Exception as e:
            return f"Error cloning repository: {str(e)}"

    def create_branch(self, branch_name: str, base_branch: str = "main") -> str:
        """Create a new branch from the specified base branch."""
        if not self.repo:
            return "No repository is currently loaded"
        
        try:
            base = self.repo.heads[base_branch]
            new_branch = self.repo.create_head(branch_name, base)
            new_branch.checkout()
            return f"Successfully created and checked out branch {branch_name}"
        except Exception as e:
            return f"Error creating branch: {str(e)}"

    def cherry_pick_commits(self, commits: List[str]) -> str:
        """Cherry-pick the specified commits onto the current branch."""
        if not self.repo:
            return "No repository is currently loaded"
        
        try:
            for commit in commits:
                self.repo.git.cherry_pick(commit)
            return f"Successfully cherry-picked {len(commits)} commits"
        except Exception as e:
            return f"Error cherry-picking commits: {str(e)}"

    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> str:
        """Commit changes to the repository."""
        if not self.repo:
            return "No repository is currently loaded"
        
        try:
            if files:
                self.repo.index.add(files)
            else:
                self.repo.git.add(A=True)
            
            self.repo.index.commit(message)
            return f"Successfully committed changes with message: {message}"
        except Exception as e:
            return f"Error committing changes: {str(e)}"

    def push_branch(self, branch_name: Optional[str] = None, remote: str = "origin") -> str:
        """Push the current or specified branch to the remote repository."""
        if not self.repo:
            return "No repository is currently loaded"
        
        try:
            if branch_name:
                self.repo.git.push(remote, branch_name)
            else:
                self.repo.git.push()
            return f"Successfully pushed branch to {remote}"
        except Exception as e:
            return f"Error pushing branch: {str(e)}"

    def get_commit_diff(self, commit_hash: str) -> str:
        """Get the diff for a specific commit."""
        if not self.repo:
            return "No repository is currently loaded"
        
        try:
            commit = self.repo.commit(commit_hash)
            return commit.diff(commit.parents[0], create_patch=True)
        except Exception as e:
            return f"Error getting commit diff: {str(e)}"

    def get_current_branch(self) -> str:
        """Get the name of the current branch."""
        if not self.repo:
            return "No repository is currently loaded"
        
        try:
            return str(self.repo.active_branch)
        except Exception as e:
            return f"Error getting current branch: {str(e)}"
