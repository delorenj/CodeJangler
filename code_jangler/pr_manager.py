"""
PR Manager Main Module

This is the main entry point for the Code Jangler PR splitting functionality.
"""

import asyncio
import os

import streamlit as st

# Import from code_jangler modules
from code_jangler.agents.pr_agents import create_agents
from code_jangler.models.pr_models import STACK_MANAGERS
from code_jangler.ui.streamlit_ui import (
    create_input_query,
    create_tabs,
    display_analysis_process,
    display_split_strategies,
    render_tab_content,
    setup_debug_logging,
    setup_page,
    setup_session_state,
    sidebar_input_form,
)
from code_jangler.utils.api_helpers import check_api_key, run_split_planning


def main():
    """Main function to run the Code Jangler application"""
    # Check for API key
    api_key_set = check_api_key()

    # Setup page - This needs to be called regardless of API key status
    setup_page()

    # If no API key, the setup_page function will show an error and stop execution
    if not api_key_set:
        return

    # Setup debug logging
    setup_debug_logging()

    # Initialize session state
    setup_session_state()

    # Create and get sidebar inputs
    input_value, start_button, stack_manager_type = sidebar_input_form()

    # Create tabs
    tab1, tab2 = create_tabs()

    # Render default tab content
    render_tab_content(tab1, tab2, start_button)

    # Log that we've initialized the UI
    st.session_state.debug_log.append("UI initialization complete")

    # Run the analysis when the button is clicked
    if start_button:
        with st.spinner(f"Planning PR Split for: {input_value}"):
            try:
                # Create the input query from form values
                input_query = create_input_query(input_value, stack_manager_type)

                # Display analysis process
                display_analysis_process(tab1, input_query)

                # Create agents
                split_strategist, pr_manager = create_agents()

                # Run the planning
                strategies = asyncio.run(run_split_planning(input_query, pr_manager))

                # Store the strategies
                st.session_state.split_strategies = strategies

                # Display split strategies
                display_split_strategies(tab2)

                # Mark planning as done
                st.session_state.planning_done = True

            except Exception as e:
                st.error(f"An error occurred during planning: {str(e)}")
                st.session_state.debug_log.append(f"Error in main: {str(e)}")

    # Display strategies in the second tab if planning is done
    if st.session_state.get("planning_done", False):
        display_split_strategies(tab2)


# This ensures the main function runs when this module is executed directly
if __name__ == "__main__":
    main()
