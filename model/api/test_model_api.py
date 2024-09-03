from fastapi.testclient import TestClient
from model_api import app
import os

client = TestClient(app)

# Get the API key from environment variable
API_KEY = os.getenv("API_KEY")

# Create headers with Authorization
headers = {"Authorization": f"Bearer {API_KEY}"}


def test_generate_3d_model_success():
    test_image_path = (
        "/data/storage/images/plane/000002_plane_cessna caravan_flying.png"
    )
    response = client.post(
        "/generate", json={"image_path": test_image_path}, headers=headers
    )
    assert response.status_code == 200
    assert "object_3d" in response.json()
    assert "object_2d" in response.json()
    assert os.path.exists(response.json()["object_3d"])
    assert os.path.exists(response.json()["object_2d"])


def test_generate_3d_model_image_not_found():
    response = client.post(
        "/generate", json={"image_path": "/non/existent/path.jpg"}, headers=headers
    )
    assert response.status_code == 404
    assert "Image not found" in response.json()["detail"]


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
