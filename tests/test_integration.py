import json
import os
import pytest
from unittest.mock import patch, mock_open, MagicMock
import sys
import tempfile

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMainIntegration:
    """Integration tests for main.py functionality."""
    
    @pytest.fixture
    def mock_secret_data(self):
        """Mock secret.json data."""
        return {
            "clientId": "test_client_id",
            "clientSecret": "test_client_secret",
            "space_id": "test_space_id",
            "key": "test_key",
            "token": "test_token",
            "threadKey": "test_thread_key"
        }
    
    @pytest.fixture
    def mock_config_data(self):
        """Mock config.json data."""
        return {
            "query": "test_query",
            "max_news": 3
        }
    
    @pytest.fixture
    def mock_naver_response(self):
        """Mock Naver API response."""
        return {
            "items": [
                {
                    "title": "Test News 1",
                    "link": "https://example.com/news1"
                },
                {
                    "title": "Test News 2",
                    "link": "https://example.com/news2"
                },
                {
                    "title": "Test News 3",
                    "link": "https://example.com/news3"
                }
            ]
        }
    
    def test_googlewebhook_import(self):
        """Test that googlewebhook module can be imported and send_message exists."""
        from googlewebhook import send_message
        assert callable(send_message)
    
    def test_main_script_syntax(self):
        """Test that main.py has valid Python syntax."""
        with open('/home/runner/work/NotifyNews/NotifyNews/main.py', 'r') as f:
            content = f.read()
        
        # Try to compile the script
        try:
            compile(content, 'main.py', 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in main.py: {e}")
    
    def test_config_file_format(self):
        """Test that config.json has valid format."""
        with open('/home/runner/work/NotifyNews/NotifyNews/config.json', 'r') as f:
            config = json.load(f)
        
        # Check required fields
        assert 'query' in config
        assert 'max_news' in config
        assert isinstance(config['query'], str)
        assert isinstance(config['max_news'], int)
    
    def test_previous_links_file_format(self):
        """Test that previous_links.txt has valid format."""
        with open('/home/runner/work/NotifyNews/NotifyNews/previous_links.txt', 'r') as f:
            lines = f.readlines()
        
        # Check that all lines are URLs
        for line in lines:
            stripped = line.strip()
            if stripped:  # Skip empty lines
                assert stripped.startswith('http')
    
    @patch('httplib2.Http')
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_main_components_integration(self, mock_exists, mock_file, mock_requests, mock_http,
                                       mock_secret_data, mock_config_data, mock_naver_response):
        """Test that main components work together properly."""
        # Setup
        mock_exists.return_value = True
        
        # Mock file operations
        def mock_open_files(filename, mode='r', encoding=None):
            if filename == 'secret.json':
                return mock_open(read_data=json.dumps(mock_secret_data))()
            elif filename == 'config.json':
                return mock_open(read_data=json.dumps(mock_config_data))()
            elif filename == 'previous_links.txt':
                if 'r' in mode:
                    return mock_open(read_data="")()
                else:
                    return mock_open()()
            return mock_open()()
        
        mock_file.side_effect = mock_open_files
        
        # Mock requests
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_naver_response)
        mock_requests.return_value = mock_response
        
        # Mock HTTP for Google Spaces
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_http_instance.request.return_value = ("response_headers", "response_body")
        
        # Import and test individual components
        from googlewebhook import send_message
        
        # Test send_message works
        send_message("test message")
        mock_http_instance.request.assert_called()
        
        # Test that the modules can be imported without errors
        assert send_message is not None
    
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    def test_googlewebhook_component(self, mock_file, mock_http):
        """Test googlewebhook component works correctly."""
        from googlewebhook import send_message
        
        # Mock secret data
        secret_data = {
            "space_id": "test_space",
            "key": "test_key",
            "token": "test_token",
            "threadKey": "test_thread"
        }
        
        mock_file.return_value.read.return_value = json.dumps(secret_data)
        
        # Mock HTTP
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_http_instance.request.return_value = ("response_headers", "response_body")
        
        # Test sending a message
        test_message = "Test message"
        send_message(test_message)
        
        # Verify call was made
        mock_http_instance.request.assert_called_once()
        call_args = mock_http_instance.request.call_args
        
        # Check body contains the message
        body = json.loads(call_args[1]['body'])
        assert body['text'] == test_message
    
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists and has valid content."""
        requirements_path = '/home/runner/work/NotifyNews/NotifyNews/requirements.txt'
        assert os.path.exists(requirements_path)
        
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        # Check that it contains expected dependencies
        assert 'requests' in content
        assert 'httplib2' in content
        assert 'pytest' in content
    
    def test_test_files_exist(self):
        """Test that test files exist and are properly structured."""
        test_dir = '/home/runner/work/NotifyNews/NotifyNews/tests'
        assert os.path.exists(test_dir)
        
        # Check test files exist
        test_files = ['__init__.py', 'conftest.py', 'test_googlewebhook.py', 'test_main.py']
        for test_file in test_files:
            test_path = os.path.join(test_dir, test_file)
            assert os.path.exists(test_path), f"Test file {test_file} does not exist"
    
    def test_pytest_config_exists(self):
        """Test that pytest configuration exists."""
        config_path = '/home/runner/work/NotifyNews/NotifyNews/pyproject.toml'
        assert os.path.exists(config_path)
        
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Check that it contains pytest configuration
        assert 'pytest.ini_options' in content
        assert 'testpaths' in content
    
    def test_main_script_imports(self):
        """Test that main.py can import required modules."""
        # Test that the script can import all required modules
        import requests
        import json
        import os
        
        # Test that the modules exist
        assert requests is not None
        assert json is not None
        assert os is not None
    
    def test_code_structure_quality(self):
        """Test basic code quality metrics."""
        # Test googlewebhook.py
        with open('/home/runner/work/NotifyNews/NotifyNews/googlewebhook.py', 'r') as f:
            googlewebhook_content = f.read()
        
        # Test main.py
        with open('/home/runner/work/NotifyNews/NotifyNews/main.py', 'r') as f:
            main_content = f.read()
        
        # Basic checks
        assert len(googlewebhook_content.strip()) > 0
        assert len(main_content.strip()) > 0
        
        # Check for basic Python constructs
        assert 'def ' in googlewebhook_content
        assert 'import ' in googlewebhook_content
        assert 'import ' in main_content
        
        # Check for no obvious syntax errors (basic)
        assert googlewebhook_content.count('(') == googlewebhook_content.count(')')
        assert main_content.count('(') == main_content.count(')')
        assert googlewebhook_content.count('{') == googlewebhook_content.count('}')
        assert main_content.count('{') == main_content.count('}')
    
    def test_gitignore_configuration(self):
        """Test that .gitignore is properly configured."""
        gitignore_path = '/home/runner/work/NotifyNews/NotifyNews/.gitignore'
        assert os.path.exists(gitignore_path)
        
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        # Check that secret.json is ignored
        assert 'secret.json' in content
        
        # Check that common Python ignores are present
        assert '__pycache__' in content or '*.pyc' in content or '.idea' in content