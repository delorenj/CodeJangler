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
