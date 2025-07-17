import json
import os
import pytest
from unittest.mock import patch, mock_open, MagicMock
import sys

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGoogleWebhook:
    """Test suite for Google Webhook functionality."""
    
    @pytest.fixture
    def mock_secret_data(self):
        """Mock secret.json data."""
        return {
            "space_id": "test_space_id",
            "key": "test_key",
            "token": "test_token",
            "threadKey": "test_thread_key"
        }
    
    @pytest.fixture
    def expected_url(self, mock_secret_data):
        """Expected URL for Google Spaces API."""
        return (
            f"https://chat.googleapis.com/v1/spaces/{mock_secret_data['space_id']}/messages?"
            f"key={mock_secret_data['key']}&"
            f"token={mock_secret_data['token']}&"
            f"threadKey={mock_secret_data['threadKey']}&"
            "messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD"
        )
    
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    def test_send_message_success(self, mock_file, mock_http, mock_secret_data, expected_url):
        """Test successful message sending."""
        # Import after patching
        from googlewebhook import send_message
        
        # Setup
        mock_file.return_value.read.return_value = json.dumps(mock_secret_data)
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_response = ("response_headers", "response_body")
        mock_http_instance.request.return_value = mock_response
        
        test_message = "Test message"
        
        # Execute
        send_message(test_message)
        
        # Verify
        mock_file.assert_called_once_with('secret.json', 'r')
        mock_http.assert_called_once()
        mock_http_instance.request.assert_called_once_with(
            uri=expected_url,
            method='POST',
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            body=json.dumps({'text': test_message})
        )
    
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    def test_send_message_empty_message(self, mock_file, mock_http, mock_secret_data, expected_url):
        """Test sending empty message."""
        # Import after patching
        from googlewebhook import send_message
        
        # Setup
        mock_file.return_value.read.return_value = json.dumps(mock_secret_data)
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_response = ("response_headers", "response_body")
        mock_http_instance.request.return_value = mock_response
        
        test_message = ""
        
        # Execute
        send_message(test_message)
        
        # Verify
        mock_http_instance.request.assert_called_once_with(
            uri=expected_url,
            method='POST',
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            body=json.dumps({'text': test_message})
        )
    
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    def test_send_message_multiline_message(self, mock_file, mock_http, mock_secret_data, expected_url):
        """Test sending multiline message."""
        # Import after patching
        from googlewebhook import send_message
        
        # Setup
        mock_file.return_value.read.return_value = json.dumps(mock_secret_data)
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_response = ("response_headers", "response_body")
        mock_http_instance.request.return_value = mock_response
        
        test_message = "Line 1\nLine 2\nLine 3"
        
        # Execute
        send_message(test_message)
        
        # Verify
        mock_http_instance.request.assert_called_once_with(
            uri=expected_url,
            method='POST',
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            body=json.dumps({'text': test_message})
        )
    
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    def test_send_message_special_characters(self, mock_file, mock_http, mock_secret_data, expected_url):
        """Test sending message with special characters."""
        # Import after patching
        from googlewebhook import send_message
        
        # Setup
        mock_file.return_value.read.return_value = json.dumps(mock_secret_data)
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_response = ("response_headers", "response_body")
        mock_http_instance.request.return_value = mock_response
        
        test_message = "Test with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?~`"
        
        # Execute
        send_message(test_message)
        
        # Verify
        mock_http_instance.request.assert_called_once_with(
            uri=expected_url,
            method='POST',
            headers={'Content-Type': 'application/json; charset=UTF-8'},
            body=json.dumps({'text': test_message})
        )
    
    @patch('httplib2.Http')
    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_send_message_no_secret_file(self, mock_file, mock_http):
        """Test handling when secret.json file is not found."""
        # Import after patching
        from googlewebhook import send_message
        
        # Execute and verify
        with pytest.raises(FileNotFoundError):
            send_message("Test message")
    
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    def test_send_message_invalid_json(self, mock_file, mock_http):
        """Test handling of invalid JSON in secret.json."""
        # Import after patching
        from googlewebhook import send_message
        
        # Setup
        mock_file.return_value.read.return_value = "invalid json"
        
        # Execute and verify
        with pytest.raises(json.JSONDecodeError):
            send_message("Test message")
    
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    def test_send_message_missing_keys(self, mock_file, mock_http):
        """Test handling when required keys are missing from secret.json."""
        # Import after patching
        from googlewebhook import send_message
        
        # Setup
        incomplete_secret = {"space_id": "test_space_id"}  # Missing other keys
        mock_file.return_value.read.return_value = json.dumps(incomplete_secret)
        
        # Execute and verify
        with pytest.raises(KeyError):
            send_message("Test message")
    
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    def test_send_message_http_error(self, mock_file, mock_http, mock_secret_data):
        """Test handling of HTTP errors."""
        # Import after patching
        from googlewebhook import send_message
        
        # Setup
        mock_file.return_value.read.return_value = json.dumps(mock_secret_data)
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_http_instance.request.side_effect = Exception("HTTP Error")
        
        # Execute and verify
        with pytest.raises(Exception, match="HTTP Error"):
            send_message("Test message")
    
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    def test_url_construction(self, mock_file, mock_http, mock_secret_data, expected_url):
        """Test that URL is constructed correctly with all parameters."""
        # Import after patching
        from googlewebhook import send_message
        
        # Setup
        mock_file.return_value.read.return_value = json.dumps(mock_secret_data)
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_response = ("response_headers", "response_body")
        mock_http_instance.request.return_value = mock_response
        
        # Execute
        send_message("Test message")
        
        # Verify URL construction
        call_args = mock_http_instance.request.call_args
        actual_url = call_args[1]['uri']
        assert actual_url == expected_url
        
        # Verify all required parameters are in the URL
        assert "spaces/test_space_id/messages" in actual_url
        assert "key=test_key" in actual_url
        assert "token=test_token" in actual_url
        assert "threadKey=test_thread_key" in actual_url
        assert "messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD" in actual_url
    
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    def test_request_headers(self, mock_file, mock_http, mock_secret_data):
        """Test that request headers are set correctly."""
        # Import after patching
        from googlewebhook import send_message
        
        # Setup
        mock_file.return_value.read.return_value = json.dumps(mock_secret_data)
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_response = ("response_headers", "response_body")
        mock_http_instance.request.return_value = mock_response
        
        # Execute
        send_message("Test message")
        
        # Verify headers
        call_args = mock_http_instance.request.call_args
        actual_headers = call_args[1]['headers']
        expected_headers = {'Content-Type': 'application/json; charset=UTF-8'}
        assert actual_headers == expected_headers
    
    @patch('httplib2.Http')
    @patch('builtins.open', new_callable=mock_open)
    def test_request_body_format(self, mock_file, mock_http, mock_secret_data):
        """Test that request body is formatted correctly."""
        # Import after patching
        from googlewebhook import send_message
        
        # Setup
        mock_file.return_value.read.return_value = json.dumps(mock_secret_data)
        mock_http_instance = MagicMock()
        mock_http.return_value = mock_http_instance
        mock_response = ("response_headers", "response_body")
        mock_http_instance.request.return_value = mock_response
        
        test_message = "Test message"
        
        # Execute
        send_message(test_message)
        
        # Verify body format
        call_args = mock_http_instance.request.call_args
        actual_body = call_args[1]['body']
        expected_body = json.dumps({'text': test_message})
        assert actual_body == expected_body
        
        # Verify body is valid JSON
        parsed_body = json.loads(actual_body)
        assert parsed_body == {'text': test_message}