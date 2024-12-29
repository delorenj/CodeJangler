from typing import List, Optional, Type

from crewai.tools import BaseTool
from git import Repo
from pydantic import BaseModel, Field


class CloneRepoInput(BaseModel):
    """Input schema for cloning a repository."""

    url: str = Field(..., description="Repository URL to clone")
    path: str = Field(..., description="Local path to clone to")


class CreateBranchInput(BaseModel):
    """Input schema for creating a branch."""

    branch_name: str = Field(..., description="Name of the new branch")
    base_branch: str = Field(default="main", description="Base branch to create from")


class CherryPickInput(BaseModel):
    """Input schema for cherry-picking commits."""

    commits: List[str] = Field(..., description="List of commit hashes to cherry-pick")


class CommitChangesInput(BaseModel):
    """Input schema for committing changes."""

    message: str = Field(..., description="Commit message")
    files: Optional[List[str]] = Field(
        None, description="Optional list of files to commit"
    )


class PushBranchInput(BaseModel):
    """Input schema for pushing a branch."""

    branch_name: Optional[str] = Field(None, description="Branch name to push")
    remote: str = Field(default="origin", description="Remote name")


class GetCommitDiffInput(BaseModel):
    """Input schema for getting commit diff."""

    commit_hash: str = Field(..., description="Commit hash to get diff for")


class GitTools:
    """Collection of Git operation tools."""

    class CloneRepo(BaseTool):
        name: str = "clone_repository"
        description: str = "Clone a Git repository to a local path"
        args_schema: Type[BaseModel] = CloneRepoInput

        def _run(self, url: str, path: str) -> str:
            try:
                repo = Repo.clone_from(url, path)
                return f"Successfully cloned repository to {path}"
            except Exception as e:
                return f"Error cloning repository: {str(e)}"

    class CreateBranch(BaseTool):
        name: str = "create_branch"
        description: str = "Create a new Git branch from specified base"
        args_schema: Type[BaseModel] = CreateBranchInput

        def _run(self, branch_name: str, base_branch: str = "main") -> str:
            try:
                repo = Repo(".")
                base = repo.heads[base_branch]
                new_branch = repo.create_head(branch_name, base)
                new_branch.checkout()
                return f"Successfully created and checked out branch {branch_name}"
            except Exception as e:
                return f"Error creating branch: {str(e)}"

    class CherryPick(BaseTool):
        name: str = "cherry_pick_commits"
        description: str = "Cherry-pick specified commits onto current branch"
        args_schema: Type[BaseModel] = CherryPickInput

        def _run(self, commits: List[str]) -> str:
            try:
                repo = Repo(".")
                for commit in commits:
                    repo.git.cherry_pick(commit)
                return f"Successfully cherry-picked {len(commits)} commits"
            except Exception as e:
                return f"Error cherry-picking commits: {str(e)}"

    class CommitChanges(BaseTool):
        name: str = "commit_changes"
        description: str = "Commit changes to the repository"
        args_schema: Type[BaseModel] = CommitChangesInput

        def _run(self, message: str, files: Optional[List[str]] = None) -> str:
            try:
                repo = Repo(".")
                if files:
                    repo.index.add(files)
                else:
                    repo.git.add(A=True)

                repo.index.commit(message)
                return f"Successfully committed changes with message: {message}"
            except Exception as e:
                return f"Error committing changes: {str(e)}"

    class PushBranch(BaseTool):
        name: str = "push_branch"
        description: str = "Push current or specified branch to remote"
        args_schema: Type[BaseModel] = PushBranchInput

        def _run(
            self, branch_name: Optional[str] = None, remote: str = "origin"
        ) -> str:
            try:
                repo = Repo(".")
                if branch_name:
                    repo.git.push(remote, branch_name)
                else:
                    repo.git.push()
                return f"Successfully pushed branch to {remote}"
            except Exception as e:
                return f"Error pushing branch: {str(e)}"

    class GetCommitDiff(BaseTool):
        name: str = "get_commit_diff"
        description: str = "Get the diff for a specific commit"
        args_schema: Type[BaseModel] = GetCommitDiffInput

        def _run(self, commit_hash: str) -> str:
            try:
                repo = Repo(".")
                commit = repo.commit(commit_hash)
                return str(commit.diff(commit.parents[0], create_patch=True))
            except Exception as e:
                return f"Error getting commit diff: {str(e)}"
