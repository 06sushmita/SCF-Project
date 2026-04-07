# 🧪 Tests - Quality Assurance

This folder contains automated tests for all SCF platform components.

---

## 📂 Files & Importance

### 🟢 **IMPORTANT** (Quality Assurance)

#### **test_agents.py** | Importance: 🌟🌟🌟🌟
- **Purpose**: Unit tests for all five agents (core business logic)
- **Testing Framework**: pytest
- **Contains Test Cases**: 
  - `test_extract_agent()` – Tests PDF extraction, deduplication
  - `test_control_agent()` – Tests clause→control conversion
  - `test_registry_agent()` – Tests versioning, lifecycle, search
  - `test_policy_agent()` – Tests Rego + Python policy generation
  - `test_models()` – Tests data model validation
  - `test_api_endpoints()` – Tests REST API responses
  - `test_error_handling()` – Tests exception cases
  - `test_audit_trail()` – Tests immutable audit logging
- **Coverage**: All critical agents have test cases
- **Run Tests**:
  ```bash
  pytest tests/test_agents.py -v
  pytest tests/test_agents.py -v --cov=agents  # With coverage report
  pytest tests/test_agents.py::test_extract_agent -v  # Run single test
  ```
- **Expected Output**: All tests PASS (no failures)
- **Critical for**:
  - **Regression prevention** (catch bugs before deployment)
  - **Documentation** (test examples show how to use each agent)
  - **CI/CD** (automated testing in deployment pipeline)
  - **Confidence** (team trust in code quality)
- **Maintenance**: Update tests when agents change; aim for 80%+ code coverage

---

## 🧪 Test Structure

```
test_agents.py
├── Test Extraction
│   ├── test_extract_agent()
│   └── test_deduplication()
│
├── Test Control Generation
│   ├── test_control_agent()
│   ├── test_domain_inference()
│   └── test_title_generation()
│
├── Test Registry/Versioning
│   ├── test_registry_agent()
│   ├── test_immutable_versioning()
│   ├── test_lifecycle_transitions()
│   └── test_audit_trail()
│
├── Test Policy Generation
│   ├── test_policy_agent()
│   ├── test_rego_generation()
│   └── test_python_validator()
│
├── Test Integration
│   ├── test_api_endpoints()
│   └── test_end_to_end_workflow()
│
└── Test Error Handling
    └── test_error_cases()
```

---

## 🔄 Test Workflow

```
Code Change
    ↓
Run: pytest tests/test_agents.py -v
    ↓ (PASS)
Commit code
    ↓
CI/CD runs same tests
    ↓
Deploy to production
```

---

## 📊 Quality Metrics

- **Total Test Cases**: 8+ (covers all agents)
- **Code Coverage Target**: ≥80%
- **Current Status**: All tests passing ✅
- **Last Run**: Check CI/CD logs

---

## 🔗 Related Files

| File | Tested | 
|------|--------|
| [../agents/extract.py](../agents/extract.py) | Via `test_extract_agent()` |
| [../agents/control.py](../agents/control.py) | Via `test_control_agent()` |
| [../agents/registry.py](../agents/registry.py) | Via `test_registry_agent()` |
| [../agents/policy.py](../agents/policy.py) | Via `test_policy_agent()` |
| [../agents/models.py](../agents/models.py) | Via `test_models()` |
| [../api/main.py](../api/main.py) | Via `test_api_endpoints()` |

---

## 🚀 Running Tests Locally

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=agents --cov=api --cov-report=html

# Run specific test
pytest tests/test_agents.py::test_extract_agent -v

# Run tests matching pattern
pytest tests/ -k "registry" -v
```

---

## 🔐 Best Practices

1. **Test Before Committing**: Run locally first
2. **Add Tests for Bugs**: When you find a bug, write a test that catches it
3. **Keep Tests Fast**: Tests should complete in <5 seconds
4. **Test Isolation**: Each test should be independent (no shared state)
5. **Clear Assertions**: Use descriptive error messages in assertions
