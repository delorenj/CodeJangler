from typing import List, Dict
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import ast
import re

class CodeAnalysis(BaseTool):
    """A collection of tools for analyzing code changes and dependencies."""
    
    name: str = "code_analysis"
    description: str = "Tools for analyzing code structure, dependencies, and changes"

    def analyze_file_changes(self, diff_content: str) -> Dict[str, List[str]]:
        """
        Analyze changes in a diff to identify modified functions and their dependencies.
        
        Args:
            diff_content: The git diff content to analyze
            
        Returns:
            Dictionary mapping files to lists of modified functions/classes
        """
        try:
            changes = {}
            current_file = None
            current_changes = []
            
            for line in diff_content.split('\n'):
                if line.startswith('+++'):
                    if current_file and current_changes:
                        changes[current_file] = current_changes
                    current_file = line[6:]
                    current_changes = []
                elif line.startswith('+') and not line.startswith('+++'):
                    # Extract function/class definitions
                    if 'def ' in line or 'class ' in line:
                        name = re.search(r'(def|class)\s+(\w+)', line)
                        if name:
                            current_changes.append(name.group(2))
            
            if current_file and current_changes:
                changes[current_file] = current_changes
                
            return changes
        except Exception as e:
            return {"error": [str(e)]}

    def find_dependencies(self, file_path: str) -> Dict[str, List[str]]:
        """
        Analyze a Python file to find function and class dependencies.
        
        Args:
            file_path: Path to the Python file to analyze
            
        Returns:
            Dictionary mapping each function/class to its dependencies
        """
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())
            
            dependencies = {}
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    deps = set()
                    for child in ast.walk(node):
                        if isinstance(child, ast.Name):
                            deps.add(child.id)
                        elif isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                            deps.add(child.func.id)
                    dependencies[node.name] = list(deps)
            
            return dependencies
        except Exception as e:
            return {"error": [str(e)]}

    def identify_test_coverage(self, source_file: str, test_files: List[str]) -> Dict[str, List[str]]:
        """
        Analyze test coverage for functions/classes in a source file.
        
        Args:
            source_file: Path to the source file
            test_files: List of paths to test files
            
        Returns:
            Dictionary mapping functions/classes to their test coverage
        """
        try:
            # Parse source file to get functions/classes
            with open(source_file, 'r') as f:
                source_tree = ast.parse(f.read())
            
            source_items = set()
            for node in ast.walk(source_tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    source_items.add(node.name)
            
            # Find test coverage
            coverage = {item: [] for item in source_items}
            
            for test_file in test_files:
                try:
                    with open(test_file, 'r') as f:
                        test_tree = ast.parse(f.read())
                    
                    for node in ast.walk(test_tree):
                        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                            # Look for references to source items in test function
                            for child in ast.walk(node):
                                if isinstance(child, ast.Name) and child.id in source_items:
                                    coverage[child.id].append(node.name)
                except:
                    continue
            
            return coverage
        except Exception as e:
            return {"error": [str(e)]}

    def suggest_split_points(self, changes: Dict[str, List[str]], dependencies: Dict[str, List[str]]) -> List[Dict]:
        """
        Suggest logical points to split changes based on dependencies.
        
        Args:
            changes: Dictionary of files and their changes
            dependencies: Dictionary of dependencies between items
            
        Returns:
            List of suggested split groups with rationale
        """
        try:
            splits = []
            current_group = {}
            
            # Group closely related changes together
            for file, items in changes.items():
                for item in items:
                    deps = dependencies.get(item, [])
                    
                    # Check if item should go in current group
                    should_group = False
                    for group_file, group_items in current_group.items():
                        for group_item in group_items:
                            if group_item in deps or item in dependencies.get(group_item, []):
                                should_group = True
                                break
                    
                    if should_group:
                        if file not in current_group:
                            current_group[file] = []
                        current_group[file].append(item)
                    else:
                        # Start new group if current one is not empty
                        if current_group:
                            splits.append({
                                "files": current_group,
                                "rationale": "Grouped based on direct dependencies"
                            })
                            current_group = {file: [item]}
                        else:
                            current_group = {file: [item]}
            
            # Add final group
            if current_group:
                splits.append({
                    "files": current_group,
                    "rationale": "Grouped based on direct dependencies"
                })
            
            return splits
        except Exception as e:
            return [{"error": str(e)}]
