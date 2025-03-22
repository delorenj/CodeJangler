"""
API Helper Functions

Contains utility functions for API interactions and other helpers.
"""

import asyncio
import os
from datetime import datetime

import streamlit as st
from agents import Runner

from code_jangler.models.pr_models import InputQuery


def check_api_key():
    """Check if the required API key is set"""
    if os.environ.get("OPENROUTER_API_KEY"):
        st.session_state.api_key_set = True
        return True

    # For development purposes, set a dummy key to allow the app to run
    # In a real app, you'd want to properly handle this case
    st.session_state.api_key_set = True
    os.environ["OPENROUTER_API_KEY"] = "dummy_key_for_development"
    st.warning("Using a dummy API key for development. Set OPENROUTER_API_KEY for full functionality.")
    return True


async def run_split_planning(input_query, pr_manager):
    """
    Main function to run the PR split planning process

    Args:
        input_query: InputQuery object with PR information
        pr_manager: The PR Manager agent instance

    Returns:
        List of SplitStrategy objects
    """
    # Log the start of planning
    st.session_state.debug_log.append(f"Starting run_split_planning with query={input_query}")

    # Reset state for new research
    st.session_state.split_boundaries = []
    st.session_state.split_strategies = []

    try:
        # Create a runner for the PR manager
        runner = Runner(pr_manager)

        # Log that we're about to create a trace
        st.session_state.debug_log.append(f"Creating trace for PR Manager agent")

        # Run the PR manager agent to analyze the PR and generate split strategies
        trace = await runner.arun(
            {
                "goal": "Split a PR into smaller, focused PRs for easier review",
                "pr_url": input_query.target,
                "trunk": input_query.trunk,
                "stack_manager": input_query.stack_manager_type,
            }
        )

        # Log completion of the trace
        st.session_state.debug_log.append(f"Trace completed successfully")

        # Extract the output (list of SplitStrategy objects)
        result = trace.output

        # Set session state to reflect planning completion
        st.session_state.planning_done = True

        # Return the strategies
        return result
    except Exception as e:
        # Log the error
        st.session_state.debug_log.append(f"Error in run_split_planning: {str(e)}")
        # Re-raise the exception
        raise
