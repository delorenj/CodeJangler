from crewai.tools import BaseTool
from typing import Type, List, Dict, Optional
from pydantic import BaseModel, Field
from github import Github
import os
import re

class ParsePRUrlInput(BaseModel):
    """Input schema for parsing PR URL."""
    pr_url: str = Field(..., description="GitHub PR URL to parse")

class PRDetailsInput(BaseModel):
    """Input schema for getting PR details."""
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    pr_number: int = Field(..., description="Pull request number")

class CreatePRInput(BaseModel):
    """Input schema for creating a PR."""
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    title: str = Field(..., description="PR title")
    body: str = Field(..., description="PR description")
    head: str = Field(..., description="Head branch")
    base: str = Field(..., description="Base branch")
    draft: bool = Field(default=False, description="Whether to create as draft PR")

class UpdatePRInput(BaseModel):
    """Input schema for updating a PR."""
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    pr_number: int = Field(..., description="Pull request number")
    title: Optional[str] = Field(None, description="New title")
    body: Optional[str] = Field(None, description="New description")
    state: Optional[str] = Field(None, description="New state (open/closed)")

class AddCommentInput(BaseModel):
    """Input schema for adding a PR comment."""
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    pr_number: int = Field(..., description="Pull request number")
    comment: str = Field(..., description="Comment text")

class GetReviewsInput(BaseModel):
    """Input schema for getting PR reviews."""
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    pr_number: int = Field(..., description="Pull request number")

class RequestReviewersInput(BaseModel):
    """Input schema for requesting reviewers."""
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    pr_number: int = Field(..., description="Pull request number")
    reviewers: List[str] = Field(..., description="List of GitHub usernames")

class GitHubTools:
    """Collection of GitHub API tools."""

    def __init__(self):
        self.gh = Github(os.getenv("GITHUB_TOKEN"))

    class ParsePRUrl(BaseTool):
        name: str = "parse_pr_url"
        description: str = "Parse a GitHub PR URL to extract owner, repo, and PR number"
        args_schema: Type[BaseModel] = ParsePRUrlInput

        def _run(self, pr_url: str) -> Dict[str, str]:
            try:
                pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
                match = re.match(pattern, pr_url)
                if not match:
                    return {"error": "Invalid GitHub PR URL format"}
                
                return {
                    "owner": match.group(1),
                    "repo": match.group(2),
                    "pr_number": match.group(3)
                }
            except Exception as e:
                return {"error": str(e)}

    class GetPRDetails(BaseTool):
        name: str = "get_pr_details"
        description: str = "Get details about a specific pull request"
        args_schema: Type[BaseModel] = PRDetailsInput

        def _run(self, owner: str, repo: str, pr_number: int) -> Dict:
            try:
                gh = Github(os.getenv("GITHUB_TOKEN"))
                repo = gh.get_repo(f"{owner}/{repo}")
                pr = repo.get_pull(pr_number)
                
                return {
                    "title": pr.title,
                    "body": pr.body,
                    "base": pr.base.ref,
                    "head": pr.head.ref,
                    "commits": [c.sha for c in pr.get_commits()],
                    "changed_files": [f.filename for f in pr.get_files()]
                }
            except Exception as e:
                return {"error": str(e)}

    class CreatePR(BaseTool):
        name: str = "create_pull_request"
        description: str = "Create a new pull request"
        args_schema: Type[BaseModel] = CreatePRInput

        def _run(
            self,
            owner: str,
            repo: str,
            title: str,
            body: str,
            head: str,
            base: str,
            draft: bool = False
        ) -> Dict:
            try:
                gh = Github(os.getenv("GITHUB_TOKEN"))
                repo = gh.get_repo(f"{owner}/{repo}")
                pr = repo.create_pull(
                    title=title,
                    body=body,
                    head=head,
                    base=base,
                    draft=draft
                )
                
                return {
                    "number": pr.number,
                    "url": pr.html_url
                }
            except Exception as e:
                return {"error": str(e)}

    class UpdatePR(BaseTool):
        name: str = "update_pull_request"
        description: str = "Update an existing pull request"
        args_schema: Type[BaseModel] = UpdatePRInput

        def _run(
            self,
            owner: str,
            repo: str,
            pr_number: int,
            title: Optional[str] = None,
            body: Optional[str] = None,
            state: Optional[str] = None
        ) -> Dict:
            try:
                gh = Github(os.getenv("GITHUB_TOKEN"))
                repo = gh.get_repo(f"{owner}/{repo}")
                pr = repo.get_pull(pr_number)
                
                if title:
                    pr.edit(title=title)
                if body:
                    pr.edit(body=body)
                if state:
                    if state == "closed":
                        pr.edit(state="closed")
                    elif state == "open":
                        pr.edit(state="open")
                
                return {
                    "number": pr.number,
                    "url": pr.html_url,
                    "state": pr.state
                }
            except Exception as e:
                return {"error": str(e)}

    class AddComment(BaseTool):
        name: str = "add_pr_comment"
        description: str = "Add a comment to a pull request"
        args_schema: Type[BaseModel] = AddCommentInput

        def _run(self, owner: str, repo: str, pr_number: int, comment: str) -> Dict:
            try:
                gh = Github(os.getenv("GITHUB_TOKEN"))
                repo = gh.get_repo(f"{owner}/{repo}")
                pr = repo.get_pull(pr_number)
                comment = pr.create_issue_comment(comment)
                
                return {
                    "id": comment.id,
                    "body": comment.body
                }
            except Exception as e:
                return {"error": str(e)}

    class GetReviews(BaseTool):
        name: str = "get_pr_reviews"
        description: str = "Get reviews for a pull request"
        args_schema: Type[BaseModel] = GetReviewsInput

        def _run(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
            try:
                gh = Github(os.getenv("GITHUB_TOKEN"))
                repo = gh.get_repo(f"{owner}/{repo}")
                pr = repo.get_pull(pr_number)
                reviews = []
                
                for review in pr.get_reviews():
                    reviews.append({
                        "id": review.id,
                        "state": review.state,
                        "body": review.body,
                        "user": review.user.login
                    })
                
                return reviews
            except Exception as e:
                return [{"error": str(e)}]

    class RequestReviewers(BaseTool):
        name: str = "request_reviewers"
        description: str = "Request reviewers for a pull request"
        args_schema: Type[BaseModel] = RequestReviewersInput

        def _run(
            self,
            owner: str,
            repo: str,
            pr_number: int,
            reviewers: List[str]
        ) -> Dict:
            try:
                gh = Github(os.getenv("GITHUB_TOKEN"))
                repo = gh.get_repo(f"{owner}/{repo}")
                pr = repo.get_pull(pr_number)
                pr.create_review_request(reviewers=reviewers)
                
                return {
                    "status": "success",
                    "requested_reviewers": reviewers
                }
            except Exception as e:
                return {"error": str(e)}
