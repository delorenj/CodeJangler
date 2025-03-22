"""
PR Splitting Agents

This module defines the agents used for PR splitting and their custom tools.
"""

import streamlit as st
from agents import Agent, function_tool, handoff

from code_jangler.models.pr_models import SplitBoundary, SplitStrategy


# Custom tool for saving possible split boundaries found during the planning phase.
@function_tool
def save_split_boundary(splitBoundary: SplitBoundary) -> str:
    """Save a possible split boundary found during the planning phase.

    Args:
        splitBoundary: The possible split boundary to save

    Returns:

        Confirmation message
    """
    if "possible_split_boundaries" not in st.session_state:
        st.session_state.possible_split_boundaries = []

    st.session_state.possible_split_boundaries.append(splitBoundary)

    return f"Split boundary saved: {splitBoundary.explanation}"


# Custom tool for saving split strategies found during the planning phase.
@function_tool
def save_split_strategy(splitStrategy: SplitStrategy) -> str:
    """Save a split strategy found during the planning phase.

    Args:
        splitStrategy: The split strategy to save

    Returns:

        Confirmation message
    """
    if "split_strategies" not in st.session_state:
        st.session_state.split_strategies = []

    st.session_state.split_strategies.append(splitStrategy)

    return f"Split strategy saved: {splitStrategy.explanation}"


# Define the agents
def create_agents():
    """Create and return the agents used for PR splitting"""

    # Split Strategist Agent
    split_strategist = Agent(
        name="Split Strategist",
        instructions="""
# Enterprise Staff Engineer and Git Workflow Expert

## Persona

You are a staff level engineer with 30 years experience. You are my best friend and are always excited to help me out with any code reviews I have. When I told you about my latest pull request, you couldn't wait to come over and have a few drinks and help me split it up into a nice and neat stack.

## Background

You are a Staff Engineer with 30+ years experience. You're a big believer in DORA metrics and always strive for PR workflow optimzation. You are obsessed with finding the perfect split boundaries that will make the stack easy to split and maintain. You believe the stack should tell the reviewer a story that starts with a goal at the trunk, and ends with a complete feature/fix/etc at the tip.

## Goal

Given a PR, you orchestrate the planning and execution of a PR split into a stack of smaller, easier-to-review PRs.
""",
        model="google/gemini-2.0-pro-exp-02-05:free",
        tools=[save_split_boundary],
    )

    # PR Manager Agent
    pr_manager = Agent(
        name="PR Manager",
        instructions="""You are the coordinator of this PR split operation. Your job is to:
    1. Understand the changes present in the PR relative to the trunk
    2. Hand off to the Split Strategist to find all the possible split boundaries.
    3. Weight the options and present the top 3 options to the user for approval.
    
    Make sure to return the options in the expected structured format with each option having an explanation, files, commits, and acceptance criteria.
    """,
        handoffs=[handoff(split_strategist)],
        model="google/gemini-2.0-pro-exp-02-05:free",
        output_type=list[SplitStrategy],
    )

    return split_strategist, pr_manager
