# Backend Test Suite

This directory contains a comprehensive test suite for the Terean backend application.

## Test Structure

```
tests/
├── conftest.py                          # Shared fixtures and configuration
├── test_auth.py                         # Authentication tests
├── test_crud.py                         # CRUD operation tests
├── test_integration.py                  # Integration tests
├── test_main.py                         # Main application tests
├── test_models.py                       # Database model tests
├── test_utils.py                        # Utility function tests
├── test_routers/                        # Router-specific tests
│   ├── test_admin_router.py             # Admin endpoints tests
│   ├── test_authentication_router.py    # Auth endpoints tests
│   ├── test_project_router.py           # Project endpoints tests
│   ├── test_sgy_file_router.py          # SGY file endpoints tests
│   └── test_process_router.py           # Process endpoints tests
└── README.md                            # This file
```

## Running Tests

### Install Dependencies

First, ensure all test dependencies are installed:

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only authentication tests
pytest -m auth

# Run only database tests
pytest -m db

# Skip slow tests
pytest -m "not slow"
```

### Run Specific Test Files

```bash
# Run authentication tests
pytest tests/test_auth.py

# Run router tests
pytest tests/test_routers/

# Run a specific test class
pytest tests/test_auth.py::TestPasswordHashing

# Run a specific test method
pytest tests/test_auth.py::TestPasswordHashing::test_password_hash_verification
```

## Test Coverage

The pytest configuration requires a minimum of 80% code coverage. To view detailed coverage:

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View coverage in terminal
pytest --cov=src --cov-report=term-missing
```

Open `htmlcov/index.html` in a browser to view the detailed coverage report.

## Test Categories

### Unit Tests

- **Models** (`test_models.py`): Test database models and relationships
- **CRUD** (`test_crud.py`): Test CRUD operations for all entities
- **Utils** (`test_utils.py`): Test utility functions
- **Auth** (`test_auth.py`): Test authentication and authorization

### Integration Tests

- **Workflows** (`test_integration.py`): Test complete user workflows
- **Data Integrity**: Test cascade deletes and relationships
- **Error Handling**: Test error scenarios and recovery
- **Performance**: Test with larger datasets

### Router Tests

- **Authentication Router**: Login, token refresh, user profile
- **Admin Router**: User management, permissions
- **Project Router**: Project CRUD, file operations, search
- **SGY File Router**: File upload, processing, retrieval
- **Process Router**: Processing operations, status tracking

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `test_db`: In-memory SQLite database for each test
- `client`: FastAPI test client
- `test_user`: Regular test user
- `admin_user`: Admin test user
- `auth_headers`: Authentication headers for regular user
- `admin_auth_headers`: Authentication headers for admin user
- `temp_dir`: Temporary directory for file operations
- `mock_env_vars`: Mocked environment variables

## Writing New Tests

### Test Structure

```python
import pytest
from fastapi import status

class TestFeatureName:
    """Test feature description."""
    
    @pytest.mark.unit  # or integration, auth, db, slow
    def test_specific_behavior(self, client, auth_headers):
        """Test description."""
        # Arrange
        test_data = {"key": "value"}
        
        # Act
        response = client.post("/api/endpoint", json=test_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["key"] == "value"
```

### Best Practices

1. **Use descriptive test names**: Test names should clearly describe what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Use appropriate markers**: Mark tests with unit, integration, auth, db, or slow
4. **Mock external dependencies**: Use pytest-mock for external services
5. **Test edge cases**: Include tests for error conditions and boundary values
6. **Keep tests isolated**: Each test should be independent
7. **Use fixtures**: Leverage conftest.py fixtures for common setup

## Environment Variables

The test suite uses mocked environment variables. See `mock_env_vars` fixture in `conftest.py` for the list of variables.

For testing with real environment variables, create a `.env.test` file:

```env
MQ_SAVE_DIR=/tmp/test_data
YOUR_GOOGLE_EMAIL=test@gmail.com
YOUR_GOOGLE_EMAIL_APP_PASSWORD=test_password
SECRET_KEY=test-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pytest --cov=src --cov-report=xml --cov-fail-under=80
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Test Summary

### Total Test Coverage

- **Authentication**: ~30 tests covering login, tokens, permissions
- **Models**: ~25 tests covering all database models
- **CRUD Operations**: ~35 tests for all CRUD functions
- **Routers**: ~150+ tests across all API endpoints
- **Integration**: ~15 tests for complete workflows
- **Utilities**: ~20 tests for utility functions
- **Main App**: ~15 tests for app configuration

**Total**: ~290+ tests providing comprehensive coverage

### Key Testing Areas

1. **Security**: Authentication, authorization, permission levels
2. **Data Integrity**: Database operations, relationships, cascades
3. **API Contracts**: Request/response validation, status codes
4. **Error Handling**: Invalid inputs, edge cases, recovery
5. **Performance**: Pagination, search, batch operations
6. **File Operations**: Upload, download, processing

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure the `src` directory is in the Python path
2. **Database errors**: Check that SQLite is available
3. **Permission errors**: Some tests may need write permissions for temp files
4. **Slow tests**: Use `-m "not slow"` to skip performance tests during development

### Debugging Tests

```bash
# Run with debugging output
pytest -vvs

# Run with pytest debugger
pytest --pdb

# Run with logging
pytest --log-cli-level=DEBUG
```

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve code coverage
4. Add appropriate test markers
5. Update this README if adding new test categories 
