RESTX_PROMPT = """As a senior Python developer specializing in API testing, your task is to write comprehensive and well-documented unit tests for a Flask-RESTx resource.

**Instructions:**
- Use the `pytest` framework.
- Assume the tests will be run with a Flask test client, so the `client` fixture is available.
- For any external dependencies (e.g., a database connection, a service layer, or another API call), use pytest-mock to mock the dependency and verify it was called correctly. Do not rely on a live database or service.
- Each test function should be a complete, self-contained test case.
- Include detailed comments explaining the purpose of each test.
- unit test should have at least 95% code coverage
- testing target module {module_name}
- output should only contains python code, no commentary, notes or explanation
- a filename and path should be generated for before each code block, for example "### Filename: my/module/test_my_function.py"

**Resource Code:**
```python
# {module_name}
{python_code}        
```  

"""


ATLAS_RESTX_PROMPT = """As a senior Python developer specializing in API testing, your task is to write comprehensive and well-documented unit tests for a Flask-RESTx resource.

**Instructions:**
- Use the `pytest` framework.
- Assume the tests will be run with a Flask test client, so the `client` fixture is available.
- For any external dependencies (e.g., a database connection, a service layer, or another API call), use pytest-mock to mock the dependency and verify it was called correctly. Do not rely on a live database or service.
- Each test function should be a complete, self-contained test case.
- Include detailed comments explaining the purpose of each test.
- unit test should have at least 95% code coverage
- testing target module {module_name}
- create mock_app and mock_client like below example and use it for the rest of test cases
- do not create mock object for SecuredResource 
- flask-restx Api has prefix, create a pytest.fixture for it and add it to function endpoint
- output should only contains python code, no commentary, notes or explanation
- a filename and path should be generated for before each code block, for example "### Filename: my/module/test_my_function.py"

mock_app and mock_client example:

```python
from {module_name} import <target_namespace>
from app.app_session import app as flask_app, api as restx_api

@pytest.fixture
def mock_app(): 
    restx_api.add_namespace(<target_namespace>)
    return flask_app

 
@pytest.fixture
def mock_client(mock_app):
    return  mock_app.test_client() 

```
**Resource Code:**
```python
# {module_name}
{python_code}        
```  

"""


FASTAPI_PROMPT = """As a senior Python developer specializing in API testing, your task is to write comprehensive and well-documented unit tests for a FastAPI application.

**Instructions:**
- Use the `pytest` framework.
- Assume the tests will use `TestClient` from `fastapi.testclient`.
- For any dependencies injected via `Depends` (e.g., a database session or service), use `app.dependency_overrides` to mock the dependency and verify it was called correctly. Do not rely on a live database or service.
- Each test function should be a complete, self-contained test case.
- Include detailed comments explaining the purpose of each test.
- unit test should have at least 95% code coverage
- testing target module {module_name}
- output should only contains python code, no commentary, notes or explanation
- a filename and path should be generated for before each code block, for example "### Filename: my/module/test_my_function.py"

**FastAPI Code:**
```python
# {module_name}
{python_code}        
```

"""

PYTHON_PROMPT = """As a senior Python developer specializing in unit testing, your task is to write comprehensive and well-documented `pytest` tests for a given Python Module {module_name}.

**Instructions:**
- Use the `pytest` and `pytest-mock` framework.
- Use mocking for any external dependencies, such as database connections, API calls, or file system operations. Use `pytest-mock`.
- Each test function should be a complete, self-contained test case.
- Include detailed comments explaining the purpose of each test.
- unit test should have at least 95% code coverage
- testing target module {module_name}
- output should only contains python code, no commentary, notes or explanation
- a filename and path should be generated for before each code block, for example "### Filename: my/module/test_my_function.py"


**Python Module Code:**
```python
# {module_name}
{python_code}        
```

"""
