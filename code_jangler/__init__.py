"""
Code Jangler

An agentic system that splits PRs into a stack of smaller, easier-to-review PRs.
"""

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the main module
from .pr_manager import main
