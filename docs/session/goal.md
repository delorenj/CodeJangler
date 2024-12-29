# Goal

A comprehensive state management for the PR Optimizer crew. This will help track the optimization process and maintain data between tasks.


## Implementation Plan

1. First, let's create a robust state model using Pydantic. Create a new file `src/pr_optimizer/models.py`:

```python
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from datetime import datetime

class PRFile(BaseModel):
    """Represents a file in a pull request"""
    filename: str
    changes: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)

class PRSplit(BaseModel):
    """Represents a suggested PR split"""
    files: Dict[str, List[str]]
    rationale: str
    branch_name: Optional[str] = None
    pr_number: Optional[int] = None
    review_status: Optional[str] = None

class AnalysisResult(BaseModel):
    """Results from PR analysis"""
    files: Dict[str, PRFile] = Field(default_factory=dict)
    dependency_graph: Dict[str, List[str]] = Field(default_factory=dict)
    suggested_splits: List[PRSplit] = Field(default_factory=list)
    risk_assessment: Dict[str, str] = Field(default_factory=dict)
    test_coverage: Dict[str, float] = Field(default_factory=dict)

class PROptimizationState(BaseModel):
    """Main state model for PR optimization process"""
    # Input parameters
    pr_url: str
    owner: str
    repo: str
    pr_number: int
    base_branch: str = "main"
    
    # Process tracking
    start_time: datetime = Field(default_factory=datetime.now)
    status: str = "initialized"
    current_task: Optional[str] = None
    completed_tasks: Set[str] = Field(default_factory=set)
    
    # Analysis state
    analysis_results: Optional[AnalysisResult] = None
    
    # Split tracking
    splits: List[PRSplit] = Field(default_factory=list)
    created_branches: List[str] = Field(default_factory=list)
    created_prs: List[int] = Field(default_factory=list)
    
    # Validation state
    validation_results: Dict[int, Dict[str, bool]] = Field(default_factory=dict)
    merge_sequence: List[int] = Field(default_factory=list)
    
    # Error tracking
    errors: List[Dict[str, str]] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
```

2. Now, let's modify the `PrOptimizer` crew to use this state. Update `src/pr_optimizer/crew.py`:

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import Optional
from datetime import datetime
from .models import PROptimizationState, AnalysisResult, PRSplit
from .tools import tool_collections
import re

@CrewBase
class PrOptimizer():
    """PrOptimizer crew"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

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

    @agent
    def pr_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['pr_analyzer'],
            tools=tool_collections['git_tools'] + tool_collections['code_analysis'],
            verbose=True
        )

    @agent
    def pr_splitter(self) -> Agent:
        return Agent(
            config=self.agents_config['pr_splitter'],
            tools=tool_collections['git_tools'] + tool_collections['github_api'],
            verbose=True
        )

    @agent
    def pr_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['pr_reviewer'],
            tools=tool_collections['code_analysis'] + tool_collections['github_api'],
            verbose=True
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
            config=self.tasks_config['analyze_pr'],
            callback=analyze_callback,
            output_file='analysis_report.md'
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
            config=self.tasks_config['create_split_strategy'],
            callback=split_callback,
            output_file='split_strategy.md'
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
            config=self.tasks_config['validate_splits'],
            callback=validation_callback,
            output_file='validation_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the PrOptimizer crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            respect_context_window=True
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
```

3. Finally, let's create a simple state persistence mechanism. Create `src/pr_optimizer/state_manager.py`:

```python
import json
from pathlib import Path
from typing import Optional
from .models import PROptimizationState

class StateManager:
    """Manages persistence of optimization state"""
    
    def __init__(self, storage_dir: str = ".pr_optimizer"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def _get_state_path(self, pr_url: str) -> Path:
        """Get path for state file"""
        # Create safe filename from PR URL
        safe_name = pr_url.replace("/", "_").replace(":", "_")
        return self.storage_dir / f"{safe_name}.json"

    def save_state(self, state: PROptimizationState) -> None:
        """Save state to file"""
        state_path = self._get_state_path(state.pr_url)
        with state_path.open("w") as f:
            json.dump(state.dict(), f, indent=2, default=str)

    def load_state(self, pr_url: str) -> Optional[PROptimizationState]:
        """Load state from file"""
        state_path = self._get_state_path(pr_url)
        if not state_path.exists():
            return None
            
        with state_path.open("r") as f:
            data = json.load(f)
            return PROptimizationState.parse_obj(data)
```

To use this state management system:

1. Initialize the optimizer with state management:
```python
from pr_optimizer import PrOptimizer
from pr_optimizer.state_manager import StateManager

state_manager = StateManager()
optimizer = PrOptimizer()

# Run optimization
pr_url = "https://github.com/user/repo/pull/123"
try:
    # Check for existing state
    state = state_manager.load_state(pr_url)
    if not state:
        # Run optimization
        state = optimizer.kickoff(pr_url)
        # Save final state
        state_manager.save_state(state)
    
    # Access state information
    print(f"Status: {state.status}")
    print(f"Created PRs: {state.created_prs}")
    print(f"Validation Results: {state.validation_results}")
except Exception as e:
    print(f"Optimization failed: {e}")
```

This state management system provides:

1. **Comprehensive State Tracking**: Tracks all aspects of the PR optimization process
2. **Type Safety**: Using Pydantic models ensures type safety and validation
3. **Persistence**: Allows saving and loading state between runs
4. **Error Tracking**: Built-in error tracking and status monitoring
5. **Progress Tracking**: Tracks completed tasks and overall progress
6. **Async Support**: Compatible with async operations through callbacks

Would you like me to explain any particular aspect in more detail or help with implementing additional features in the state management system?