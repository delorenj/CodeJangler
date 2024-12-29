from crewai import Agent, Task, Crew
from typing import Any

class PROptimizerCrew:
    """Crew for optimizing GitHub pull requests by breaking them into smaller, manageable pieces."""
    
    def __init__(self):
        self.analyzer = Agent(
            role="PR Analyzer",
            goal="Analyze PR for optimal split points based on logical changes and dependencies",
            backstory="""Expert code analyst specializing in identifying logical boundaries 
            between changes and understanding code dependencies. You excel at finding natural 
            split points in large changes that maintain functionality."""
        )
        
        self.splitter = Agent(
            role="PR Splitter",
            goal="Create optimal PR split strategy and execute git operations",
            backstory="""Git operations expert who excels at creating clean, focused PRs. 
            You understand how to split changes while maintaining git history and ensuring 
            each PR can be reviewed and merged independently."""
        )
        
        self.reviewer = Agent(
            role="PR Reviewer",
            goal="Validate PR splits and ensure quality",
            backstory="""Senior code reviewer focused on maintainability and best practices. 
            You ensure split PRs maintain functionality, have proper test coverage, and follow 
            a logical order for review and merge."""
        )
        
        self.crew = Crew(
            agents=[self.analyzer, self.splitter, self.reviewer],
            tasks=self.get_tasks(),
            verbose=True
        )

    def get_tasks(self) -> list[Task]:
        """Define the sequence of tasks for PR optimization."""
        return [
            Task(
                description="""Analyze the PR to identify logical split points. Consider:
                1. Related code changes that should stay together
                2. Dependencies between changes
                3. Test coverage and potential risks
                4. Natural boundaries in the codebase
                
                Provide a detailed analysis with recommended split points.""",
                agent=self.analyzer
            ),
            Task(
                description="""Create a PR split strategy based on the analysis. Include:
                1. Sequence of PRs to be created
                2. Changes included in each PR
                3. Git operations needed (cherry-pick, new commits, etc.)
                4. Dependencies between PRs
                
                Execute the necessary git operations to create the splits.""",
                agent=self.splitter
            ),
            Task(
                description="""Review the split PRs to ensure:
                1. Each PR is focused and reviewable
                2. Dependencies are properly handled
                3. Test coverage is maintained
                4. The merge sequence is logical
                
                Provide feedback on the split strategy and suggest improvements.""",
                agent=self.reviewer
            )
        ]

    def run(self, pr_url: str, async_mode: bool = False) -> Any:
        """Run the PR optimization process.
        
        Args:
            pr_url: URL of the GitHub PR to optimize
            async_mode: Whether to run the process asynchronously
            
        Returns:
            Result of the PR optimization process
        """
        # TODO: Add async support
        result = self.crew.kickoff()
        return result
