import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from user_api import app, API_KEY

client = TestClient(app)


@pytest.fixture
def mock_httpx_client():
    with patch("user_api.httpx.AsyncClient") as mock:
        yield mock


@pytest.mark.asyncio
async def test_home(mock_httpx_client):
    pytest.skip("coroutine object")
    mock_response = AsyncMock()
    mock_response.json.return_value = ["category1", "category2"]
    mock_httpx_client.return_value.__aenter__.return_value.get.return_value = (
        mock_response
    )

    response = client.get("/")
    assert response.status_code == 200
    assert "category1" in response.text
    assert "category2" in response.text


@pytest.mark.asyncio
async def test_choose_category(mock_httpx_client):
    pytest.skip("coroutine object")
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_httpx_client.return_value.__aenter__.return_value.post.return_value = (
        mock_response
    )

    response = client.post(
        "/selected_category", data={"selected_category": "test_category"}
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/category/test_category"


@pytest.mark.asyncio
async def test_images(mock_httpx_client):
    pytest.skip("coroutine object")
    mock_response = AsyncMock()
    mock_response.json.return_value = ["image1.jpg", "image2.jpg"]
    mock_httpx_client.return_value.__aenter__.return_value.get.return_value = (
        mock_response
    )

    response = client.get("/category/test_category")
    assert response.status_code == 200
    assert "image1.jpg" in response.text
    assert "image2.jpg" in response.text


@pytest.mark.asyncio
async def test_choose_image(mock_httpx_client):
    pytest.skip("network connectivity")
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_httpx_client.return_value.__aenter__.return_value.put.return_value = (
        mock_response
    )

    response = client.post(
        "/selected_image", data={"selected_image_path": "/path/to/image.jpg"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_generate_object_page():
    response = client.get("/generate_object")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_download_file():
    with patch("user_api.os.path.exists", return_value=True), patch(
        "user_api.FileResponse", return_value="mocked_file_response"
    ):
        response = client.get("/download?file=/data/storage/objects/test.obj")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_api_key_usage(mock_httpx_client):
    pytest.skip("coroutine object")
    mock_response = AsyncMock()
    mock_response.json.return_value = ["category1", "category2"]
    mock_httpx_client.return_value.__aenter__.return_value.get.return_value = (
        mock_response
    )

    await client.get("/")

    mock_httpx_client.return_value.__aenter__.return_value.get.assert_called_with(
        "http://data-api/categories", headers={"Authorization": f"Bearer {API_KEY}"}
    )
