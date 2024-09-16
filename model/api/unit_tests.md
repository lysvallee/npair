# Model Unit Tests Documentation

This document describes the unit tests for the model, as implemented in the `unit_tests.py` file.

## Overview

The unit tests focus on the `generate_3d_model` function from the `model_api` module. These tests use pytest and mock objects to isolate the function and test its behavior under different scenarios.

## Test Setup

### Imports

```python
import pytest
import subprocess
from unittest.mock import patch, mock_open
from model_api import generate_3d_model
from fastapi import HTTPException
import os
```

- `pytest` is used as the testing framework.
- `subprocess` is imported to mock system calls.
- `unittest.mock` provides mocking capabilities.
- `generate_3d_model` is the main function being tested.
- `HTTPException` is used to test error handling.
- `os` is used for file system operations.

## Test Cases

### 1. Successful 3D Model Generation

```python
@pytest.mark.asyncio
async def test_generate_3d_model_subprocess_success():
    with patch("subprocess.run") as mock_run, patch("os.path.exists") as mock_exists, patch("shutil.move") as mock_move:
        mock_run.return_value.stdout = "Model generated successfully"
        mock_run.return_value.stderr = ""
        mock_exists.return_value = True

        result = await generate_3d_model({"image_path": "/data/storage/images/plane/000002_plane_cessna caravan_flying.png"})

        assert "object_3d" in result
        assert "object_2d" in result
        assert mock_run.called
        assert mock_move.call_count == 2
```

This test case checks if:
- The function returns the expected result when subprocess runs successfully.
- The result contains both `object_3d` and `object_2d` keys.
- The subprocess.run method is called.
- The shutil.move method is called twice (once for 3D object, once for 2D object).

### 2. Subprocess Failure

```python
@pytest.mark.asyncio
async def test_generate_3d_model_subprocess_failure():
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="Error in model generation")

        with pytest.raises(HTTPException) as exc_info:
            await generate_3d_model({"image_path": "/data/storage/images/plane/000002_plane_cessna caravan_flying.png"})

        assert exc_info.value.status_code == 500
        assert "Model generation failed" in str(exc_info.value.detail)
```

This test case checks if:
- The function raises an HTTPException with status code 500 when subprocess fails.
- The error message contains "Model generation failed".

### 3. File Not Found Error

```python
@pytest.mark.asyncio
async def test_generate_3d_model_file_not_found():
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await generate_3d_model({"image_path": "/data/storage/images/plane/000002_plane_cessna caravan_flying.png"})

        assert exc_info.value.status_code == 404
        assert "Image not found" in str(exc_info.value.detail)
```

This test case checks if:
- The function raises an HTTPException with status code 404 when the input file doesn't exist.
- The error message contains "Image not found".

## Test Execution

```python
if __name__ == "__main__":
    pytest.main([__file__])
```

This block allows the tests to be run directly by executing the Python file. It uses pytest to discover and run the tests in the file.

## Key Points

1. **Asynchronous Testing**: All test functions are decorated with `@pytest.mark.asyncio`, indicating they are testing asynchronous code.
2. **Mocking**: Extensive use of `patch` to mock external dependencies (`subprocess.run`, `os.path.exists`, `shutil.move`).
3. **Error Handling**: Tests cover both success scenarios and different types of failures (subprocess error, file not found).
4. **Isolation**: By mocking external calls, these tests isolate the `generate_3d_model` function, focusing on its logic rather than the behavior of its dependencies.

## Maintenance and Expansion

- Ensure that the mocked paths and function calls are updated if the `generate_3d_model` function implementation changes.
- Consider adding more test cases to cover additional scenarios, such as:
  - Edge cases in input data
  - Different types of subprocess outputs
  - File system interaction edge cases
- Regularly update the tests as new features are added to the `generate_3d_model` function.

These unit tests help ensure that the core functionality of the 3D model generation process works as expected, handling both successful operations and various error conditions correctly.
