import json
import os
import pytest
from unittest.mock import patch, mock_open, MagicMock
import sys
import tempfile
import importlib

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMainFunctionality:
    """Test suite for main.py functionality."""
    
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
                },
                {
                    "title": "Test News 4",
                    "link": "https://example.com/news4"
                }
            ]
        }
    
    @pytest.fixture
    def mock_previous_links(self):
        """Mock previous_links.txt content."""
        return ["https://example.com/news2\n"]
    
    @patch('requests.get')
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_main_execution_with_new_news(self, mock_exists, mock_file, mock_http, mock_requests, 
                                         mock_secret_data, mock_config_data, mock_naver_response):
        """Test main execution with new news items."""
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
        
        # Mock HTTP requests
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_naver_response)
        mock_requests.return_value = mock_response
        
        # Mock httplib2.Http for google webhook
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_http_instance.request.return_value = ("response_headers", "response_body")
        
        # Execute main.py script
        with patch('sys.argv', ['main.py']):
            try:
                exec(open('/home/runner/work/NotifyNews/NotifyNews/main.py').read())
            except SystemExit:
                pass
        
        # Verify Naver API was called
        mock_requests.assert_called_once()
        
        # Verify HTTP request was made with correct parameters
        call_args = mock_requests.call_args
        assert "https://openapi.naver.com/v1/search/news?query=test_query" in call_args[0][0]
        assert call_args[1]['headers']['X-Naver-Client-Id'] == 'test_client_id'
        assert call_args[1]['headers']['X-Naver-Client-Secret'] == 'test_client_secret'
        
        # Verify Google Spaces messages were sent (should be 3 calls for 3 news items)
        assert mock_http_instance.request.call_count == 3
    
    @patch('requests.get')
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_main_execution_with_existing_news(self, mock_exists, mock_file, mock_http, mock_requests,
                                             mock_secret_data, mock_config_data, mock_naver_response):
        """Test main execution when news already exists in previous_links.txt."""
        # Setup
        mock_exists.return_value = True
        
        # Mock previous_links.txt with all news already processed
        previous_links_content = "https://example.com/news1\nhttps://example.com/news2\nhttps://example.com/news3\nhttps://example.com/news4\n"
        
        def mock_open_files(filename, mode='r', encoding=None):
            if filename == 'secret.json':
                return mock_open(read_data=json.dumps(mock_secret_data))()
            elif filename == 'config.json':
                return mock_open(read_data=json.dumps(mock_config_data))()
            elif filename == 'previous_links.txt':
                if 'r' in mode:
                    mock_file_obj = mock_open(read_data=previous_links_content)()
                    mock_file_obj.readlines.return_value = previous_links_content.splitlines(keepends=True)
                    return mock_file_obj
                else:
                    return mock_open()()
            return mock_open()()
        
        mock_file.side_effect = mock_open_files
        
        # Mock HTTP requests
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_naver_response)
        mock_requests.return_value = mock_response
        
        # Mock httplib2.Http for google webhook
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_http_instance.request.return_value = ("response_headers", "response_body")
        
        # Execute main.py script
        with patch('sys.argv', ['main.py']):
            try:
                exec(open('/home/runner/work/NotifyNews/NotifyNews/main.py').read())
            except SystemExit:
                pass
        
        # Verify Naver API was called
        mock_requests.assert_called_once()
        
        # Verify no Google Spaces messages were sent (all news already processed)
        assert mock_http_instance.request.call_count == 0
    
    @patch('requests.get')
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_main_execution_with_max_news_limit(self, mock_exists, mock_file, mock_http, mock_requests,
                                               mock_secret_data, mock_naver_response):
        """Test main execution respects max_news limit."""
        # Setup
        mock_exists.return_value = True
        
        # Config with max_news = 2
        limited_config = {
            "query": "test_query",
            "max_news": 2
        }
        
        def mock_open_files(filename, mode='r', encoding=None):
            if filename == 'secret.json':
                return mock_open(read_data=json.dumps(mock_secret_data))()
            elif filename == 'config.json':
                return mock_open(read_data=json.dumps(limited_config))()
            elif filename == 'previous_links.txt':
                if 'r' in mode:
                    return mock_open(read_data="")()
                else:
                    return mock_open()()
            return mock_open()()
        
        mock_file.side_effect = mock_open_files
        
        # Mock HTTP requests
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_naver_response)
        mock_requests.return_value = mock_response
        
        # Mock httplib2.Http for google webhook
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_http_instance.request.return_value = ("response_headers", "response_body")
        
        # Execute main.py script
        with patch('sys.argv', ['main.py']):
            try:
                exec(open('/home/runner/work/NotifyNews/NotifyNews/main.py').read())
            except SystemExit:
                pass
        
        # Verify only 2 messages were sent (max_news limit)
        assert mock_http_instance.request.call_count == 2
    
    @patch('os.path.exists')
    def test_main_no_secret_file(self, mock_exists):
        """Test main execution when secret.json doesn't exist."""
        # Setup
        mock_exists.return_value = False
        
        # Execute and verify exception is raised
        with pytest.raises(FileNotFoundError):
            exec(open('/home/runner/work/NotifyNews/NotifyNews/main.py').read())
    
    @patch('requests.get')
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_main_empty_naver_response(self, mock_exists, mock_file, mock_http, mock_requests,
                                      mock_secret_data, mock_config_data):
        """Test main execution with empty Naver response."""
        # Setup
        mock_exists.return_value = True
        
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
        
        # Mock empty Naver response
        empty_response = {"items": []}
        mock_response = MagicMock()
        mock_response.text = json.dumps(empty_response)
        mock_requests.return_value = mock_response
        
        # Mock httplib2.Http for google webhook
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_http_instance.request.return_value = ("response_headers", "response_body")
        
        # Execute main.py script
        with patch('sys.argv', ['main.py']):
            try:
                exec(open('/home/runner/work/NotifyNews/NotifyNews/main.py').read())
            except SystemExit:
                pass
        
        # Verify no messages were sent (empty response)
        assert mock_http_instance.request.call_count == 0
    
    @patch('requests.get')
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_naver_api_request_format(self, mock_exists, mock_file, mock_http, mock_requests,
                                     mock_secret_data, mock_config_data, mock_naver_response):
        """Test that Naver API request is formatted correctly."""
        # Setup
        mock_exists.return_value = True
        
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
        
        # Mock HTTP requests
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_naver_response)
        mock_requests.return_value = mock_response
        
        # Mock httplib2.Http for google webhook
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_http_instance.request.return_value = ("response_headers", "response_body")
        
        # Execute main.py script
        with patch('sys.argv', ['main.py']):
            try:
                exec(open('/home/runner/work/NotifyNews/NotifyNews/main.py').read())
            except SystemExit:
                pass
        
        # Verify API call format
        mock_requests.assert_called_once()
        call_args = mock_requests.call_args
        
        # Check URL
        expected_url = "https://openapi.naver.com/v1/search/news?query=test_query"
        assert call_args[0][0] == expected_url
        
        # Check headers
        expected_headers = {
            'X-Naver-Client-Id': 'test_client_id',
            'X-Naver-Client-Secret': 'test_client_secret'
        }
        assert call_args[1]['headers'] == expected_headers
    
    @patch('requests.get')
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_message_format_and_content(self, mock_exists, mock_file, mock_http, mock_requests,
                                       mock_secret_data, mock_config_data, mock_naver_response):
        """Test that messages are formatted and sent correctly."""
        # Setup
        mock_exists.return_value = True
        
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
        
        # Mock HTTP requests
        mock_response = MagicMock()
        mock_response.text = json.dumps(mock_naver_response)
        mock_requests.return_value = mock_response
        
        # Mock httplib2.Http for google webhook
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_http_instance.request.return_value = ("response_headers", "response_body")
        
        # Execute main.py script
        with patch('sys.argv', ['main.py']):
            try:
                exec(open('/home/runner/work/NotifyNews/NotifyNews/main.py').read())
            except SystemExit:
                pass
        
        # Verify message format
        assert mock_http_instance.request.call_count == 3
        
        # Check first message content
        first_call = mock_http_instance.request.call_args_list[0]
        first_body = json.loads(first_call[1]['body'])
        expected_message = "Test News 1\nhttps://example.com/news1"
        assert first_body['text'] == expected_message
        
        # Check second message content
        second_call = mock_http_instance.request.call_args_list[1]
        second_body = json.loads(second_call[1]['body'])
        expected_message = "Test News 2\nhttps://example.com/news2"
        assert second_body['text'] == expected_message