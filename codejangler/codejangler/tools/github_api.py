from typing import List, Dict, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from github import Github
import os
import re

class GitHubAPI(BaseTool):
    """A collection of tools for interacting with GitHub's API."""
    
    name: str = "github_api"
    description: str = "Tools for managing GitHub pull requests and repositories"

    def __init__(self):
        super().__init__()
        self.gh = Github(os.getenv("GITHUB_TOKEN"))

    def parse_pr_url(self, pr_url: str) -> Dict[str, str]:
        """
        Parse a GitHub PR URL to extract owner, repo, and PR number.
        
        Args:
            pr_url: The GitHub PR URL to parse
            
        Returns:
            Dictionary containing owner, repo, and pr_number
        """
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

    def get_pr_details(self, owner: str, repo: str, pr_number: int) -> Dict:
        """
        Get details about a specific pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            Dictionary containing PR details
        """
        try:
            repo = self.gh.get_repo(f"{owner}/{repo}")
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

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str,
        draft: bool = False
    ) -> Dict:
        """
        Create a new pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: PR title
            body: PR description
            head: Head branch
            base: Base branch
            draft: Whether to create as draft PR
            
        Returns:
            Dictionary containing new PR details
        """
        try:
            repo = self.gh.get_repo(f"{owner}/{repo}")
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

    def update_pull_request(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None
    ) -> Dict:
        """
        Update an existing pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            title: New title (optional)
            body: New description (optional)
            state: New state (open/closed) (optional)
            
        Returns:
            Dictionary containing updated PR details
        """
        try:
            repo = self.gh.get_repo(f"{owner}/{repo}")
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

    def add_pr_comment(self, owner: str, repo: str, pr_number: int, comment: str) -> Dict:
        """
        Add a comment to a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            comment: Comment text
            
        Returns:
            Dictionary containing comment details
        """
        try:
            repo = self.gh.get_repo(f"{owner}/{repo}")
            pr = repo.get_pull(pr_number)
            comment = pr.create_issue_comment(comment)
            
            return {
                "id": comment.id,
                "body": comment.body
            }
        except Exception as e:
            return {"error": str(e)}

    def get_pr_reviews(self, owner: str, repo: str, pr_number: int) -> List[Dict]:
        """
        Get reviews for a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            List of review details
        """
        try:
            repo = self.gh.get_repo(f"{owner}/{repo}")
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

    def request_reviewers(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        reviewers: List[str]
    ) -> Dict:
        """
        Request reviewers for a pull request.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            reviewers: List of GitHub usernames
            
        Returns:
            Dictionary containing request status
        """
        try:
            repo = self.gh.get_repo(f"{owner}/{repo}")
            pr = repo.get_pull(pr_number)
            pr.create_review_request(reviewers=reviewers)
            
            return {
                "status": "success",
                "requested_reviewers": reviewers
            }
        except Exception as e:
            return {"error": str(e)}
