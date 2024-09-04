import pytest
from fastapi.testclient import TestClient
from model_api import app
import os
import shutil
import logging


client = TestClient(app)

# Get the API key from environment variable
API_KEY = os.getenv("API_KEY")

# Create headers with Authorization
headers = {"Authorization": f"Bearer {API_KEY}"}


# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def test_image():
    logger.info("Setting up test_image fixture")
    test_image_path = (
        "/data/storage/images/plane/000002_plane_cessna caravan_flying.png"
    )
    if not os.path.exists(test_image_path):
        logger.warning(f"Test image not found at {test_image_path}")
        pytest.skip("Test image not found")
    logger.info(f"Test image found at {test_image_path}")
    return test_image_path


@pytest.fixture(scope="module")
def cleanup_output():
    logger.info("Setting up cleanup_output fixture")
    yield
    logger.info("Cleaning up generated files after tests")
    output_dir = "/data/storage/test_data"
    for item in os.listdir(output_dir):
        item_path = os.path.join(output_dir, item)
        if os.path.isfile(item_path):
            logger.info(f"Removing file: {item_path}")
            os.unlink(item_path)
        elif os.path.isdir(item_path):
            logger.info(f"Removing directory: {item_path}")
            shutil.rmtree(item_path)
    logger.info("Cleanup completed")


def test_full_model_generation_flow(test_image, cleanup_output):
    logger.info("Starting test_full_model_generation_flow")
    logger.info(f"Using test image: {test_image}")

    response = client.post(
        "/generate", json={"image_path": test_image}, headers=headers
    )
    logger.info(f"Response status code: {response.status_code}")
    assert (
        response.status_code == 200
    ), f"Expected status code 200, but got {response.status_code}"

    result = response.json()
    logger.info(f"Response JSON: {result}")

    assert "object_3d" in result, "object_3d not found in response"
    assert "object_2d" in result, "object_2d not found in response"

    logger.info(f"Checking 3D object file: {result['object_3d']}")
    assert os.path.exists(
        result["object_3d"]
    ), f"3D object file does not exist: {result['object_3d']}"
    assert os.path.isfile(
        result["object_3d"]
    ), f"3D object is not a file: {result['object_3d']}"
    assert (
        os.path.getsize(result["object_3d"]) > 0
    ), f"3D object file is empty: {result['object_3d']}"

    logger.info(f"Checking 2D object file: {result['object_2d']}")
    assert os.path.exists(
        result["object_2d"]
    ), f"2D object file does not exist: {result['object_2d']}"
    assert os.path.isfile(
        result["object_2d"]
    ), f"2D object is not a file: {result['object_2d']}"
    assert (
        os.path.getsize(result["object_2d"]) > 0
    ), f"2D object file is empty: {result['object_2d']}"

    logger.info("test_full_model_generation_flow completed successfully")


def test_model_generation_invalid_image(cleanup_output):
    logger.info("Starting test_model_generation_invalid_image")
    invalid_image_path = "/data/storage/images/nonexistent_image.png"
    logger.info(f"Using invalid image path: {invalid_image_path}")

    response = client.post(
        "/generate", json={"image_path": invalid_image_path}, headers=headers
    )
    logger.info(f"Response status code: {response.status_code}")
    assert (
        response.status_code == 404
    ), f"Expected status code 404, but got {response.status_code}"

    response_json = response.json()
    logger.info(f"Response JSON: {response_json}")
    assert (
        "Image not found" in response_json["detail"]
    ), f"Expected 'Image not found' in response, but got: {response_json['detail']}"

    logger.info("test_model_generation_invalid_image completed successfully")


if __name__ == "__main__":
    logger.info("Starting test execution")
    pytest.main(["-v", __file__])
    logger.info("Test execution completed")
