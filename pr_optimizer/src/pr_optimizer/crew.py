from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import Optional
from datetime import datetime
import re

from .tools import tool_collections
from .models import PROptimizationState, AnalysisResult, PRSplit

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class PrOptimizer:
    """PrOptimizer crew"""

    def __init__(self):
        self.state: Optional[PROptimizationState] = None

    def _initialize_state(self, pr_url: str) -> None:
        """Initialize state from PR URL"""
        # Parse PR URL to get owner, repo, and PR number
        pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
        match = re.match(pattern, pr_url)
        if not match:
            raise ValueError("Invalid GitHub PR URL")
            
        self.state = PROptimizationState(
            pr_url=pr_url,
            owner=match.group(1),
            repo=match.group(2),
            pr_number=int(match.group(3))
        )

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools

    @agent
    def pr_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config["pr_analyzer"],
            tools=tool_collections["git_tools"] + tool_collections["code_analysis"],
            verbose=True,
        )

    @agent
    def pr_splitter(self) -> Agent:
        return Agent(
            config=self.agents_config["pr_splitter"],
            tools=tool_collections["git_tools"] + tool_collections["github_api"],
            verbose=True,
        )

    @agent
    def pr_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["pr_reviewer"],
            tools=tool_collections["code_analysis"] + tool_collections["github_api"],
            verbose=True,
        )

    @task
    def analyze_pr(self) -> Task:
        async def analyze_callback(output):
            """Update state with analysis results"""
            if self.state:
                self.state.status = "analysis_completed"
                self.state.analysis_results = AnalysisResult.parse_raw(output)
                self.state.completed_tasks.add("analyze_pr")

        return Task(
            config=self.tasks_config["analyze_pr"],
            callback=analyze_callback,
            output_file="analysis_report.md"
        )

    @task
    def create_split_strategy(self) -> Task:
        async def split_callback(output):
            """Update state with split results"""
            if self.state:
                self.state.status = "splits_created"
                splits = [PRSplit.parse_raw(split) for split in output]
                self.state.splits.extend(splits)
                self.state.completed_tasks.add("create_split_strategy")

        return Task(
            config=self.tasks_config["create_split_strategy"],
            callback=split_callback,
            output_file="split_strategy.md"
        )

    @task
    def validate_splits(self) -> Task:
        async def validation_callback(output):
            """Update state with validation results"""
            if self.state:
                self.state.status = "validation_completed"
                validation_data = output
                for pr_number, results in validation_data.items():
                    self.state.validation_results[int(pr_number)] = results
                self.state.completed_tasks.add("validate_splits")

        return Task(
            config=self.tasks_config["validate_splits"],
            callback=validation_callback,
            output_file="validation_report.md"
        )

    @crew
    def crew(self) -> Crew:
        """Creates the PrOptimizer crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_retry_limit=3,
            respect_context_window=True,
            planning=True,
            memory=True
        )

    def kickoff(self, pr_url: str) -> PROptimizationState:
        """Run the crew and return final state"""
        self._initialize_state(pr_url)
        
        try:
            result = self.crew().kickoff(inputs={"pr_url": pr_url})
            if self.state:
                self.state.status = "completed"
            return self.state
        except Exception as e:
            if self.state:
                self.state.status = "failed"
                self.state.errors.append({
                    "time": datetime.now().isoformat(),
                    "error": str(e)
                })
            raise
