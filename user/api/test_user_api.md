# User API Testing Documentation

This document describes the testing process for the user API, as implemented in the `test_user_api.py` file.

## Overview

The test file uses FastAPI's `TestClient` to simulate HTTP requests to the user API. It tests various endpoints and functionalities of the user interface, including fetching categories, selecting categories and images, generating objects, and downloading files.

## Test Setup

### Imports and Client Initialization

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from user_api import app, API_KEY

client = TestClient(app)
```

- `pytest` is used as the testing framework.
- `TestClient` from FastAPI is used to create a test client for the application.
- `patch` and `AsyncMock` from `unittest.mock` are used for mocking.
- The `app` and `API_KEY` are imported from `user_api`.

### Mock HTTP Client Fixture

```python
@pytest.fixture
def mock_httpx_client():
    with patch("user_api.httpx.AsyncClient") as mock:
        yield mock
```

This fixture mocks the `httpx.AsyncClient` used in the user API to make HTTP requests to other services.

## Test Cases

### 1. Home Page Test

```python
@pytest.mark.asyncio
async def test_home(mock_httpx_client):
    mock_response = AsyncMock()
    mock_response.json.return_value = ["category1", "category2"]
    mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response

    response = client.get("/")
    assert response.status_code == 200
    assert "category1" in response.text
    assert "category2" in response.text
```

This test checks if:
- The home page endpoint returns a 200 status code.
- The response contains the mocked categories.

### 2. Choose Category Test

```python
@pytest.mark.asyncio
async def test_choose_category(mock_httpx_client):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_httpx_client.return_value.__aenter__.return_value.post.return_value = mock_response

    response = client.post("/selected_category", data={"selected_category": "test_category"})
    assert response.status_code == 303
    assert response.headers["location"] == "/category/test_category"
```

This test verifies that:
- Selecting a category returns a 303 status code (redirect).
- The redirect location is correct.

### 3. Images Page Test

```python
@pytest.mark.asyncio
async def test_images(mock_httpx_client):
    mock_response = AsyncMock()
    mock_response.json.return_value = ["image1.jpg", "image2.jpg"]
    mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response

    response = client.get("/category/test_category")
    assert response.status_code == 200
    assert "image1.jpg" in response.text
    assert "image2.jpg" in response.text
```

This test checks if:
- The images page for a specific category returns a 200 status code.
- The response contains the mocked image names.

### 4. Choose Image Test

```python
@pytest.mark.asyncio
async def test_choose_image(mock_httpx_client):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_httpx_client.return_value.__aenter__.return_value.put.return_value = mock_response

    response = client.post("/selected_image", data={"selected_image_path": "/path/to/image.jpg"})
    assert response.status_code == 200
```

This test verifies that:
- Selecting an image returns a 200 status code.

### 5. Generate Object Page Test

```python
@pytest.mark.asyncio
async def test_generate_object_page():
    response = client.get("/generate_object")
    assert response.status_code == 200
```

This test checks if:
- The generate object page returns a 200 status code.

### 6. Download File Test

```python
@pytest.mark.asyncio
async def test_download_file():
    with patch("user_api.os.path.exists", return_value=True), patch("user_api.FileResponse", return_value="mocked_file_response"):
        response = client.get("/download?file=/data/storage/objects/test.obj")
        assert response.status_code == 200
```

This test verifies that:
- The file download endpoint returns a 200 status code when the file exists.

### 7. API Key Usage Test

```python
@pytest.mark.asyncio
async def test_api_key_usage(mock_httpx_client):
    mock_response = AsyncMock()
    mock_response.json.return_value = ["category1", "category2"]
    mock_httpx_client.return_value.__aenter__.return_value.get.return_value = mock_response

    await client.get("/")

    mock_httpx_client.return_value.__aenter__.return_value.get.assert_called_with(
        "http://data-api/categories", headers={"Authorization": f"Bearer {API_KEY}"}
    )
```

This test checks if:
- The API key is correctly used in requests to other services.

## Key Points

1. **Asynchronous Testing**: All test functions are decorated with `@pytest.mark.asyncio`, indicating they are testing asynchronous code.
2. **Mocking**: Extensive use of `AsyncMock` to mock asynchronous HTTP responses.
3. **API Key Verification**: A specific test to ensure the API key is used correctly in requests to other services.
4. **Comprehensive Coverage**: Tests cover various endpoints and functionalities of the user API.

## Maintenance and Expansion

- Keep the mock responses updated if the expected data format changes.
- Add more edge cases and error scenarios to improve test coverage.
- Update tests when new features or endpoints are added to the user API.

These tests help ensure that the user API functions correctly, handling both successful operations and various scenarios across different endpoints.
