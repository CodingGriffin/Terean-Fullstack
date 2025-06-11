# Backend Test Suite

This directory contains tests for the Terean backend application.

## Test Structure

```
tests/
├── manual_tests                          # Manually run, situational tests used during development.
├── old_tests                             # Auto-generated tests. Many of these do not work. They test the wrong thing,
│   │                                     #   or are set up incorrectly, or do not use the correct components.
│   │                                     #   However, they are a useful reference for tests that may be built in the future.
│   └── conftest.py                       # Shared fixtures and configuration. Auto generated, but functional.
├── integration_tests                     # Tests integrating multiple components
├── unit_tests                            # Unit tests, organized by subpackage, file, and specific test.
│   └── utils                             # Tests for utils submodule
│       ├── authentication                # Tests for utils.authentication
│       └── custom_types                  # Tests for utils.custom_types.*
└── README.md                             # This file
```

## Running Tests

### Install Dependencies

First, ensure all test dependencies are installed:

```bash
pip install -r requirements-dev.txt
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
