# Model API Testing Documentation

This document describes the testing process for the model API, as implemented in the `test_model_api.py` file.

## Overview

The test file uses FastAPI's `TestClient` to simulate HTTP requests to the model API. It tests the `/generate` endpoint, which is responsible for generating 3D models from input images.

## Test Setup

### Imports and Client Initialization

```python
from fastapi.testclient import TestClient
from model_api import app
import os

client = TestClient(app)
```

- The `TestClient` from FastAPI is used to create a test client for the application.
- The `app` is imported from `model_api`, which is the main FastAPI application.
- The `os` module is used for environment variable access and file path operations.

### API Key Setup

```python
API_KEY = os.getenv("API_KEY")
headers = {"Authorization": f"Bearer {API_KEY}"}
```

- The API key is retrieved from an environment variable.
- Headers are created with the API key for authentication.

## Test Cases

### 1. Successful 3D Model Generation

```python
def test_generate_3d_model_success():
    test_image_path = "/data/storage/images/plane/000002_plane_cessna caravan_flying.png"
    response = client.post("/generate", json={"image_path": test_image_path}, headers=headers)
    assert response.status_code == 200
    assert "object_3d" in response.json()
    assert "object_2d" in response.json()
    assert os.path.exists(response.json()["object_3d"])
    assert os.path.exists(response.json()["object_2d"])
```

This test case checks if:
- The API responds with a 200 status code for a valid request.
- The response JSON contains `object_3d` and `object_2d` keys.
- The files referenced in the response actually exist on the filesystem.

### 2. Image Not Found Error

```python
def test_generate_3d_model_image_not_found():
    response = client.post("/generate", json={"image_path": "/non/existent/path.jpg"}, headers=headers)
    assert response.status_code == 404
    assert "Image not found" in response.json()["detail"]
```

This test case checks if:
- The API responds with a 404 status code when an non-existent image path is provided.
- The response contains an appropriate error message.

## Test Execution

```python
if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
```

This block allows the tests to be run directly by executing the Python file. It uses pytest to discover and run the tests in the file.

## Key Points

1. **Authentication**: The tests use an API key for authentication, simulating real-world usage of the API.
2. **File System Interaction**: The tests not only check the API response but also verify that the generated files exist on the file system.
3. **Error Handling**: There's a specific test to ensure that the API correctly handles cases where the input image is not found.
4. **Environment Variables**: The test relies on an environment variable (`API_KEY`) being set correctly.

## Maintenance and Expansion

- Ensure the `API_KEY` environment variable is set correctly in the testing environment.
- The test image path (`/data/storage/images/plane/000002_plane_cessna caravan_flying.png`) should be updated if the file structure changes.
- Additional test cases can be added to cover more scenarios, such as:
  - Invalid API key
  - Malformed request data
  - Edge cases in image processing
  - Performance tests for large images

By running these tests, developers can ensure that the model API is functioning correctly, handling both successful cases and error scenarios appropriately.
