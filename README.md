# NotifyNews

네이버 뉴스의 API를 받아와서 구글 스페이스에 올려 놓는 프로그램
config.json 파일을 수정하여 사용할 것

# Usage

```
git clone git@github.com/jsheo96/NotifyNews.git
cd NotifyNews
conda create -y -n notify-news
conda activate notify-news
pip install -r requirements.txt
```
config.json 파일을 원하는 대로 수정
```
python main.py
```

# Testing

This project now includes comprehensive test coverage for all components.

## Running Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Files
```bash
python run_tests.py googlewebhook    # Run Google Spaces webhook tests
python run_tests.py integration      # Run integration tests
python run_tests.py main            # Run main functionality tests
```

### Run Tests with pytest directly
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_googlewebhook.py -v

# Run with coverage
python -m pytest tests/ -v --cov=. --cov-report=html
```

## Test Structure

- `tests/test_googlewebhook.py` - Unit tests for Google Spaces webhook functionality
- `tests/test_integration.py` - Integration tests for overall system functionality
- `tests/test_main.py` - Tests for main news processing logic
- `tests/conftest.py` - Shared test fixtures and configuration

## Test Coverage

The test suite covers:
- Google Spaces message sending with various message types
- Naver News API integration
- File handling (config.json, secret.json, previous_links.txt)
- Error handling and edge cases
- Integration between components
- Code quality and structure validation

## Dependencies

Testing dependencies are included in `requirements.txt`:
- pytest - Test framework
- pytest-mock - Mocking support
- pytest-cov - Coverage reporting
