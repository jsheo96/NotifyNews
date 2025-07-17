import pytest
import os
import sys
import tempfile
from unittest.mock import patch

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_secret_file_content():
    """Standard mock content for secret.json file."""
    return {
        "clientId": "test_client_id",
        "clientSecret": "test_client_secret",
        "space_id": "test_space_id",
        "key": "test_key",
        "token": "test_token",
        "threadKey": "test_thread_key"
    }


@pytest.fixture
def mock_config_file_content():
    """Standard mock content for config.json file."""
    return {
        "query": "test_query",
        "max_news": 3
    }


@pytest.fixture
def mock_news_items():
    """Standard mock news items for testing."""
    return [
        {
            "title": "Test News 1",
            "link": "https://example.com/news1",
            "description": "This is test news 1",
            "pubDate": "2023-01-01"
        },
        {
            "title": "Test News 2",
            "link": "https://example.com/news2",
            "description": "This is test news 2",
            "pubDate": "2023-01-02"
        },
        {
            "title": "Test News 3",
            "link": "https://example.com/news3",
            "description": "This is test news 3",
            "pubDate": "2023-01-03"
        }
    ]


@pytest.fixture
def mock_naver_api_response(mock_news_items):
    """Standard mock Naver API response."""
    return {
        "lastBuildDate": "2023-01-01 12:00:00",
        "total": len(mock_news_items),
        "start": 1,
        "display": len(mock_news_items),
        "items": mock_news_items
    }


@pytest.fixture(autouse=True)
def clean_imports():
    """Clean up imported modules after each test."""
    yield
    # Remove any imported modules that might interfere with other tests
    modules_to_remove = [m for m in sys.modules.keys() if m.startswith('main') or m.startswith('googlewebhook')]
    for module in modules_to_remove:
        if module in sys.modules:
            del sys.modules[module]