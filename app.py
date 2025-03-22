"""
Code Jangler - PR Splitter Application

This is the main entry point for the Code Jangler application.
"""

# Import the PR manager from our package
from code_jangler.pr_manager import main

# The PR manager code already includes the Streamlit app setup
# So when this file is run with `streamlit run app.py`,
# it will launch the application

if __name__ == "__main__":
    # Call the main function to initialize the Streamlit app
    main()
