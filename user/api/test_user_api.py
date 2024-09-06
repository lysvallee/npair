import os
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from user_api import app, API_KEY
from fastapi.testclient import TestClient

DATA_API_URL = "http://data_api:8000"

API_KEY = os.getenv("API_KEY")


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_httpx_client():
    with patch("user_api.httpx.AsyncClient") as mock:
        yield mock


@pytest.mark.asyncio
async def test_home(mock_httpx_client):
    mock_response = AsyncMock()
    mock_response.json.return_value = ["category1", "category2"]
    mock_httpx_client.return_value.__aenter__.return_value.get.return_value = (
        mock_response
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")  # Await the async client call
        assert response.status_code == 200
        assert "category1" in response.text
        assert "category2" in response.text


@pytest.mark.asyncio
async def test_images(mock_httpx_client):
    mock_response = AsyncMock()
    mock_response.json.return_value = ["image1.jpg", "image2.jpg"]
    mock_httpx_client.return_value.__aenter__.return_value.get.return_value = (
        mock_response
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/category/test_category")  # Await the get request
        assert response.status_code == 200
        assert "image1.jpg" in response.text
        assert "image2.jpg" in response.text


@pytest.mark.asyncio
async def test_generate_object_page(client):
    response = client.get("/generate_object")
    assert response.status_code == 200
    assert "generate_object.html" in response.text


@pytest.mark.asyncio
async def test_api_key_usage(client, mock_httpx_client):
    mock_response = AsyncMock()
    mock_response.json.return_value = ["category1", "category2"]
    mock_httpx_client.return_value.__aenter__.return_value.get.return_value = (
        mock_response
    )
    response = client.get("/")  # Remove 'await'
    mock_httpx_client.return_value.__aenter__.return_value.get.assert_called_with(
        f"{DATA_API_URL}/categories", headers={"Authorization": f"Bearer {API_KEY}"}
    )
