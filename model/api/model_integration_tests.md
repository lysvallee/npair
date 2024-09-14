# Model Integration Tests

This document describes the integration tests for the model API.

## Running the Tests

To run the integration tests, use the following commands:

```bash
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml run --rm model_api pytest --log-cli-level=DEBUG test_integration.py
```

## Test File Overview

The integration tests are defined in `test_integration.py`. This file contains the following components:

1. **Imports and Setup**
   - The necessary modules are imported, including pytest, FastAPI's TestClient, and the main application.
   - The API key is retrieved from an environment variable.
   - Logging is set up for detailed test execution information.

2. **Fixtures**
   - `test_image`: Provides the path to a test image for use in the tests.
   - `cleanup_output`: Cleans up generated files after the tests run.

3. **Test Cases**
   - `test_full_model_generation_flow`: Tests the complete flow of model generation.
   - `test_model_generation_invalid_image`: Tests the API's response to an invalid image path.

## Test Cases in Detail

### test_full_model_generation_flow

This test case verifies the entire process of model generation:

1. Sends a POST request to the `/generate` endpoint with a valid image path.
2. Checks that the response status code is 200 (OK).
3. Verifies that the response JSON contains `object_3d` and `object_2d` keys.
4. Checks that the 3D and 2D object files exist, are actual files, and are not empty.

### test_model_generation_invalid_image

This test case checks the API's handling of invalid input:

1. Sends a POST request to the `/generate` endpoint with an invalid image path.
2. Verifies that the response status code is 404 (Not Found).
3. Checks that the response JSON contains an appropriate error message.

## Logging

The tests use Python's logging module to provide detailed information about the test execution. Log messages are output at the DEBUG level, providing insights into each step of the test process.

## Cleanup

The `cleanup_output` fixture ensures that any files generated during the tests are removed after test execution. This keeps the test environment clean and prevents interference between test runs.

## Running Tests Manually

The test file includes a `__main__` block, allowing the tests to be run directly if needed:

```python
if __name__ == "__main__":
    logger.info("Starting test execution")
    pytest.main(["-v", __file__])
    logger.info("Test execution completed")
```

This provides an alternative way to run the tests, though using pytest via Docker as described at the beginning of this document is the recommended method.
