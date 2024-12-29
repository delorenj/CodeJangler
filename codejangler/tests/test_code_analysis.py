import pytest
from unittest.mock import mock_open, patch
from codejangler.tools.code_analysis import CodeAnalysis

@pytest.fixture
def code_analysis():
    return CodeAnalysis()

def test_analyze_file_changes():
    diff_content = """
+++ b/src/main.py
@@ -1,3 +1,3 @@
+def new_function():
+    pass
+
+class NewClass:
+    def method(self):
+        pass
    """
    
    analyzer = CodeAnalysis()
    result = analyzer.analyze_file_changes(diff_content)
    
    assert 'src/main.py' in result
    assert 'new_function' in result['src/main.py']
    assert 'NewClass' in result['src/main.py']

def test_find_dependencies():
    code_content = """
def function_a():
    return function_b()

def function_b():
    value = HelperClass()
    return value.process()

class HelperClass:
    def process(self):
        return function_a()
    """
    
    with patch('builtins.open', mock_open(read_data=code_content)):
        analyzer = CodeAnalysis()
        result = analyzer.find_dependencies('test.py')
        
        assert 'function_a' in result
        assert 'function_b' in result['function_a']
        assert 'HelperClass' in result['function_b']
        assert 'function_a' in result['HelperClass']

def test_identify_test_coverage():
    source_content = """
def target_function():
    pass

class TargetClass:
    def method(self):
        pass
    """
    
    test_content = """
def test_target_function():
    result = target_function()
    assert result is None

def test_target_class():
    obj = TargetClass()
    obj.method()
    """
    
    mock_files = {
        'source.py': source_content,
        'test_source.py': test_content
    }
    
    def mock_open_files(filename, *args, **kwargs):
        content = mock_files.get(filename, '')
        return mock_open(read_data=content).return_value
    
    with patch('builtins.open', side_effect=mock_open_files):
        analyzer = CodeAnalysis()
        result = analyzer.identify_test_coverage('source.py', ['test_source.py'])
        
        assert 'target_function' in result
        assert 'test_target_function' in result['target_function']
        assert 'TargetClass' in result
        assert 'test_target_class' in result['TargetClass']

def test_suggest_split_points():
    changes = {
        'src/auth.py': ['login', 'logout'],
        'src/user.py': ['create_user', 'update_user'],
        'src/profile.py': ['get_profile']
    }
    
    dependencies = {
        'login': ['create_user'],
        'logout': [],
        'create_user': ['get_profile'],
        'update_user': ['get_profile'],
        'get_profile': []
    }
    
    analyzer = CodeAnalysis()
    result = analyzer.suggest_split_points(changes, dependencies)
    
    # Verify we get logical groupings
    assert len(result) > 0
    assert all('files' in group for group in result)
    assert all('rationale' in group for group in result)
    
    # Verify dependencies are respected in groupings
    for group in result:
        files = group['files']
        # Check if dependent functions are in the same group
        for file, functions in files.items():
            for func in functions:
                deps = dependencies.get(func, [])
                for dep in deps:
                    # Find which group contains the dependency
                    dep_found = False
                    for dep_file, dep_funcs in files.items():
                        if dep in dep_funcs:
                            dep_found = True
                            break
                    assert dep_found, f"Dependency {dep} not found in same group as {func}"

def test_error_handling():
    analyzer = CodeAnalysis()
    
    # Test invalid diff content
    result = analyzer.analyze_file_changes(None)
    assert 'error' in result
    
    # Test invalid file path
    result = analyzer.find_dependencies('nonexistent.py')
    assert 'error' in result
    
    # Test invalid test files
    result = analyzer.identify_test_coverage('source.py', ['nonexistent_test.py'])
    assert 'error' in result
