"""
Models for Code Jangler PR Splitting

This module contains all the Pydantic models used for PR data representation.
"""

from enum import Enum, auto
from typing import List, Optional, Set

from pydantic import BaseModel

# Default PR template
PR_TEMPLATE = """
## Context

This PR provides context on the changes being proposed and their business impacts.

## Linked PR

- All PRs must be linked to a Notion ticket. Please ensure to reference the corresponding ticket in your PR title or description.
- PR titles must contain the Notion ticket ID, which should be prefixed with "ENG-". For example: `Fix claim lead - exceptions for admin users[ENG-643] `

- Link to related PRs involving Augusta
- Link to related PRs involving Models

## Changes

- Detailed breakdown of changes made:
- ...
"""


# Pydantic Type: Available Stack Managers: one of 'none','graphite', 'graphene'
class StackManagerType(str, Enum):
    NONE = "none"
    GRAPHITE = "graphite"
    GRAPHENE = "graphene"


class StackManager(BaseModel):
    type: StackManagerType
    description: str = ""
    url: str = ""


class InputQuery(BaseModel):
    # can be either an existing PR url or a branch name
    target: str
    trunk: str = "staging"
    stack_manager_type: StackManagerType = StackManagerType.NONE
    pr_template: str = PR_TEMPLATE


class PRTypeEnum(str, Enum):
    FEAT = "feat"
    CHORE = "chore"
    FIX = "fix"
    REFACTOR = "refactor"
    STYLE = "style"
    TEST = "test"
    PERF = "perf"
    CI = "ci"
    DOCS = "docs"
    BUILD = "build"
    REVERT = "revert"


class PRType(BaseModel):
    type: PRTypeEnum = PRTypeEnum.FEAT


class SprintBoardTicket(BaseModel):
    id: str
    # optional fields (with Optional type hint)
    title: Optional[str] = None
    description: Optional[str] = None
    story_task: Optional[str] = None
    acceptance_criteria: Optional[str] = None


class PRTitle(BaseModel):
    type: PRType
    ticket: SprintBoardTicket
    title: str


class PR(BaseModel):
    title: PRTitle
    context: str
    # Link to self
    url: str
    # Related PRs
    related_prs: List[str] = []
    files: List[str]
    diff: str
    status: str


class AcceptanceCriteria(BaseModel):
    title: str
    description: str
    is_passing: bool = False


class SplitBoundary(BaseModel):
    explanation: str
    files: List[str]
    commits: List[str]
    acceptance_criteria: Set[AcceptanceCriteria]


class SplitStrategy(BaseModel):
    explanation: str
    prs: List[SplitBoundary]


# Dictionary of available stack managers for easy reference
STACK_MANAGERS = {
    StackManagerType.NONE: StackManager(type=StackManagerType.NONE, description="No stack manager"),
    StackManagerType.GRAPHITE: StackManager(type=StackManagerType.GRAPHITE, description="Graphite"),
    StackManagerType.GRAPHENE: StackManager(type=StackManagerType.GRAPHENE, description="Graphene"),
}
