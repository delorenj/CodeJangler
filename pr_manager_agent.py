import asyncio
import os
import uuid
from datetime import datetime
from enum import Enum, auto
from typing import List, Optional

import streamlit as st
from agents import (
    Agent,
    Runner,
    WebSearchTool,
    function_tool,
    handoff,
    trace,
)
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

system_prompt = """
# Enterprise Staff Engineer and Git Workflow Expert

## Persona

You are a staff level engineer with 30 years experience. You are my best friend and are always excited to help me out with any code reviews I have. When I told you about my latest pull request, you couldn't wait to come over and have a few drinks and help me split it up into a nice and neat stack.

## Background

You are a Staff Engineer with 30+ years experience. You're a big believer in DORA metrics and always strive for PR workflow optimzation. You are obsessed with finding the perfect split boundaries that will make the stack easy to split and maintain. You believe the stack should tell the reviewer a story that starts with a goal at the trunk, and ends with a complete feature/fix/etc at the tip.

## Goal

Given a PR, you orchestrate the planning and execution of a PR split into a stack of smaller, easier-to-review PRs.
"""
pr_template = """
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

# Set up page configuration
st.set_page_config(page_title="Code Jangler", page_icon="📰", layout="wide", initial_sidebar_state="expanded")

# Make sure API key is set
if not os.environ.get("OPENROUTER_API_KEY"):
    st.error("Please set your OPENROUTER_API_KEY environment variable")
    st.stop()

# App title and description
st.title("📰 Code Jangler")
st.subheader("Agentic PR Splitter")
st.markdown("""
Is your PR so big everyone just pretends it doesn't exist? Are you known for creating commits so large they're mistaken for standalone apps? Let Code Jangler Jangle your code into shape!
""")


# Pydantic Type: Available Stack Managers: one of 'none','graphite', 'graphene'
class StackManagerType(str, Enum):
    NONE = "none"
    GRAPHITE = "graphite"
    GRAPHENE = "graphene"


class StackManager(BaseModel):
    type: StackManagerType
    description: str = ""
    url: str = ""


stack_managers = {
    StackManagerType.NONE: StackManager(type=StackManagerType.NONE, description="No stack manager"),
    StackManagerType.GRAPHITE: StackManager(type=StackManagerType.GRAPHITE, description="Graphite"),
    StackManagerType.GRAPHENE: StackManager(type=StackManagerType.GRAPHENE, description="Graphene"),
}


class InputQuery(BaseModel):
    # can be either an existing PR url or a branch name
    target: str
    trunk: str = "staging"
    stack_manager_type: StackManagerType = StackManagerType.NONE
    pr_template: str = pr_template


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


class SplitStrategy(BaseModel):
    explanation: str
    prs: List[str]
