from .git_tools import GitTools
from .code_analysis import CodeAnalysisTools
from .github_api import GitHubTools

# Export all tool classes
__all__ = [
    # Git Tools
    'GitTools.CloneRepo',
    'GitTools.CreateBranch',
    'GitTools.CherryPick',
    'GitTools.CommitChanges',
    'GitTools.PushBranch',
    'GitTools.GetCommitDiff',
    
    # Code Analysis Tools
    'CodeAnalysisTools.AnalyzeChanges',
    'CodeAnalysisTools.FindDependencies',
    'CodeAnalysisTools.AnalyzeTestCoverage',
    'CodeAnalysisTools.SuggestSplitPoints',
    
    # GitHub Tools
    'GitHubTools.ParsePRUrl',
    'GitHubTools.GetPRDetails',
    'GitHubTools.CreatePR',
    'GitHubTools.UpdatePR',
    'GitHubTools.AddComment',
    'GitHubTools.GetReviews',
    'GitHubTools.RequestReviewers'
]

# Create tool instances
git_tools = [
    GitTools.CloneRepo(),
    GitTools.CreateBranch(),
    GitTools.CherryPick(),
    GitTools.CommitChanges(),
    GitTools.PushBranch(),
    GitTools.GetCommitDiff()
]

code_analysis_tools = [
    CodeAnalysisTools.AnalyzeChanges(),
    CodeAnalysisTools.FindDependencies(),
    CodeAnalysisTools.AnalyzeTestCoverage(),
    CodeAnalysisTools.SuggestSplitPoints()
]

github_tools = [
    GitHubTools.ParsePRUrl(),
    GitHubTools.GetPRDetails(),
    GitHubTools.CreatePR(),
    GitHubTools.UpdatePR(),
    GitHubTools.AddComment(),
    GitHubTools.GetReviews(),
    GitHubTools.RequestReviewers()
]

# Export tool collections
tool_collections = {
    'git_tools': git_tools,
    'code_analysis': code_analysis_tools,
    'github_api': github_tools
}
