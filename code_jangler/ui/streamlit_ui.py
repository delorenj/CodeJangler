"""
Streamlit UI for Code Jangler

This module contains all the Streamlit UI components and layout for the Code Jangler application.
"""

import uuid
from datetime import datetime

import streamlit as st

from code_jangler.models.pr_models import PR_TEMPLATE, STACK_MANAGERS, InputQuery


def setup_page():
    """Set up the basic page configuration and title"""
    # Set up page configuration
    st.set_page_config(page_title="Code Jangler", page_icon="📰", layout="wide", initial_sidebar_state="expanded")

    # App title and description
    st.title("📰 Code Jangler")
    st.subheader("Agentic PR Splitter")
    st.markdown("""
    Is your PR so big everyone just pretends it doesn't exist? Are you known for creating commits so large they're mistaken for standalone apps? 

    Let Code Jangler Jangle your code into shape!

    **How to use:**
    1. Choose between GitHub or Local repository option
    2. For GitHub: Enter the URL of the PR you want to split
    3. For Local: Enter the path to your local repository
    4. Click "Start Analysis" to generate split strategies
    5. Review the strategies and implement the one you prefer
    """)

    # Check for API key - we'll show error but not stop execution here
    if not st.session_state.get("api_key_set", False):
        st.error("Please set your OPENROUTER_API_KEY environment variable")


def setup_debug_logging():
    """Set up debug logging functionality"""
    # Initialize session state for debug logging
    if "debug_log" not in st.session_state:
        st.session_state.debug_log = []
        st.session_state.debug_log.append("Initializing debug_log")

    # Ensure the tabs are always visible with content
    if "tabs_initialized" not in st.session_state:
        st.session_state.tabs_initialized = False
        st.session_state.debug_log.append("Setting tabs_initialized to False")

    # Generate unique ID for this UI render
    if "current_render_id" not in st.session_state:
        st.session_state.current_render_id = uuid.uuid4().hex
        st.session_state.debug_log.append(f"New render ID: {st.session_state.current_render_id}")
    else:
        old_id = st.session_state.current_render_id
        st.session_state.current_render_id = uuid.uuid4().hex
        st.session_state.debug_log.append(
            f"UI State: Render ID changed from {old_id} to {st.session_state.current_render_id}"
        )

    # Display debug info in an expander
    with st.expander("Debug Info", expanded=False):
        st.write("Session State Variables:")
        st.json({k: str(v) if k == "debug_log" else v for k, v in st.session_state.items()})
        st.write("Debug Log:")
        for log in st.session_state.debug_log[-20:]:  # Show last 20 log entries
            st.write(f"- {log}")


def sidebar_input_form():
    """Create the sidebar input form and return input values"""
    with st.sidebar:
        st.header("PR Manager")

        # Initialize session variables if they don't exist
        if "user_pr_url" not in st.session_state:
            st.session_state.user_pr_url = ""
        if "user_local_path" not in st.session_state:
            st.session_state.user_local_path = ""
        if "repo_source" not in st.session_state:
            st.session_state.repo_source = "GitHub"

        # Function to update repo source when dropdown changes
        def update_repo_source():
            """Called when dropdown value changes"""
            st.session_state.debug_log.append(f"Dropdown value changed: {st.session_state.repo_source_dropdown}")

            # Store the current repo_source for comparison
            old_source = st.session_state.get("repo_source", "GitHub")
            st.session_state.repo_source = st.session_state.repo_source_dropdown

            # Log the change for debugging
            if old_source != st.session_state.repo_source:
                st.session_state.debug_log.append(f"SOURCE CHANGED: {old_source} -> {st.session_state.repo_source}")

        # Add a dropdown to select between GitHub or local repository with controlled on_change
        repo_source = st.selectbox(
            "Repository Source:",
            options=["GitHub", "Local"],
            index=0 if st.session_state.repo_source == "GitHub" else 1,
            key="repo_source_dropdown",
            on_change=update_repo_source,
        )

        # Log dropbox selection
        st.session_state.debug_log.append(
            f"VISIBLE SELECTION: repo_source={repo_source}, session={st.session_state.repo_source}"
        )

        # Create a placeholder for input field
        input_container = st.empty()

        # Conditionally show the appropriate input field based on STORED selection (not dropdown value)
        current_source = st.session_state.repo_source

        with input_container:
            if current_source == "GitHub":
                st.session_state.debug_log.append("RENDERING: GitHub input field")
                user_pr_url = st.text_input(
                    "Enter a GitHub PR URL:", value=st.session_state.user_pr_url, key="github_input"
                )
                st.session_state.user_pr_url = user_pr_url
                input_value = user_pr_url
                st.session_state.debug_log.append(f"Set input_value to PR URL: {input_value}")
            else:
                st.session_state.debug_log.append("RENDERING: Local repo input field")
                user_local_path = st.text_input(
                    "Enter local repository path:", value=st.session_state.user_local_path, key="local_input"
                )
                st.session_state.user_local_path = user_local_path
                input_value = user_local_path
                st.session_state.debug_log.append(f"Set input_value to local path: {input_value}")

        # Add stack manager selection
        stack_manager_type = st.selectbox(
            "Stack Manager:",
            options=list(STACK_MANAGERS.keys()),
            format_func=lambda x: STACK_MANAGERS[x].description,
            index=0,
            key="stack_manager_select",
        )

        # Create the start button
        start_button = st.button("Start Split Analysis", type="primary", disabled=not input_value)
        st.session_state.debug_log.append(f"Start button rendered with disabled={not input_value}")

        return input_value, start_button, stack_manager_type


def create_tabs():
    """Create the main content tabs and return them"""
    # Main content area with two tabs
    st.session_state.debug_log.append("Creating tabs")
    tab1, tab2 = st.tabs(["Analysis Process", "Split Strategies"])
    st.session_state.debug_log.append("Created tab1 and tab2")

    # Mark tabs as initialized in session state
    st.session_state.tabs_initialized = True

    # For better debug visibility
    st.session_state.debug_log.append(f"TABS STATE: tabs_initialized={st.session_state.tabs_initialized}")

    # Force tabs to always be visible
    if "tabs_visible" not in st.session_state:
        st.session_state.tabs_visible = True
        st.session_state.debug_log.append("Initialized tabs_visible to True")

    return tab1, tab2


def render_tab_content(tab1, tab2, start_button):
    """Render the content for both tabs"""
    # Add default content to the first tab
    with tab1:
        # Always show a header to ensure the tab has content
        st.write("## Analysis Process")

        # Log rendering for debugging
        st.session_state.debug_log.append(f"RENDERING TAB1: start_button={start_button}")

        # Show appropriate content based on state
        if not start_button:
            st.info("Enter your repository details and click 'Start Split Analysis' to begin.")
            st.session_state.debug_log.append("Showing initial info message in tab1")
        else:
            st.session_state.debug_log.append("Start button was clicked, tab1 will show analysis content")

    # Add default content to the second tab
    with tab2:
        # Always show a header to ensure the tab has content
        st.write("## Split Strategies")

        # Log rendering for debugging
        st.session_state.debug_log.append(
            f"RENDERING TAB2: planning_done={st.session_state.get('planning_done', False)}"
        )

        # Show appropriate content based on state
        if not st.session_state.get("planning_done", False):
            st.info("Split strategies will appear here after analysis is complete.")
            st.session_state.debug_log.append("Showing waiting message in tab2")
        else:
            st.session_state.debug_log.append("Planning is done, tab2 will show strategies")


def setup_session_state():
    """Initialize all required session state variables"""
    # Initialize session state for storing results
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4().hex[:16])
    if "split_boundaries" not in st.session_state:
        st.session_state.split_boundaries = []
    if "split_strategies" not in st.session_state:
        st.session_state.split_strategies = []
    if "research_done" not in st.session_state:
        st.session_state.planning_done = False


def display_analysis_process(tab1, input_query):
    """Display the analysis process in the first tab"""
    with tab1:
        st.write(f"### Analyzing PR")
        st.write(f"Target: {input_query.target}")
        st.write(f"Trunk: {input_query.trunk}")
        st.write(f"Stack Manager: {STACK_MANAGERS[input_query.stack_manager_type].description}")


def display_split_strategies(tab2):
    """Display split strategies in the second tab"""
    with tab2:
        if "split_strategies" in st.session_state and st.session_state.split_strategies:
            for i, strategy in enumerate(st.session_state.split_strategies):
                with st.expander(f"Strategy {i + 1}: {strategy.explanation}", expanded=i == 0):
                    st.write("### PRs in this strategy:")
                    for j, pr in enumerate(strategy.prs):
                        st.write(f"#### PR {j + 1}: {pr.explanation}")
                        st.write("**Files:** ")
                        st.write(", ".join(pr.files))
                        st.write("**Commits:** ")
                        st.write(", ".join(pr.commits))
                        st.write("**Acceptance Criteria:** ")
                        for ac in pr.acceptance_criteria:
                            st.write(f"- {'✅' if ac.is_passing else '❌'} {ac.title}: {ac.description}")
        else:
            st.info("No split strategies found yet. Run the analysis first.")


def create_input_query(input_value, stack_manager_type):
    """Create an InputQuery object from the input values"""
    return InputQuery(
        target=input_value,
        trunk="staging",  # Default, could be customizable
        stack_manager_type=stack_manager_type,
        pr_template=PR_TEMPLATE,
    )
