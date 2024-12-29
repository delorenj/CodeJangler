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
        safe_name = pr_url.replace("/", "_").replace(":", "_").replace(".", "_")
        return self.storage_dir / f"{safe_name}.json"

    def save_state(self, state: PROptimizationState) -> None:
        """Save state to file"""
        state_path = self._get_state_path(state.pr_url)
        with state_path.open("w") as f:
            json.dump(state.model_dump(), f, indent=2, default=str)

    def load_state(self, pr_url: str) -> Optional[PROptimizationState]:
        """Load state from file"""
        state_path = self._get_state_path(pr_url)
        if not state_path.exists():
            return None
            
        with state_path.open("r") as f:
            data = json.load(f)
            # Convert completed_tasks back to a set
            if "completed_tasks" in data:
                data["completed_tasks"] = set(data["completed_tasks"])
            return PROptimizationState.model_validate(data)
