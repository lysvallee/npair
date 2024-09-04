import pytest
import subprocess
from unittest.mock import patch, mock_open
from model_api import generate_3d_model
from fastapi import HTTPException
import os


@pytest.mark.asyncio
async def test_generate_3d_model_subprocess_success():
    with patch("subprocess.run") as mock_run, patch(
        "os.path.exists"
    ) as mock_exists, patch("shutil.move") as mock_move:

        mock_run.return_value.stdout = "Model generated successfully"
        mock_run.return_value.stderr = ""
        mock_exists.return_value = True

        result = await generate_3d_model(
            {
                "image_path": "/data/storage/images/plane/000002_plane_cessna caravan_flying.png"
            }
        )

        assert "object_3d" in result
        assert "object_2d" in result
        assert mock_run.called
        assert mock_move.call_count == 2


@pytest.mark.asyncio
async def test_generate_3d_model_subprocess_failure():
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "cmd", stderr="Error in model generation"
        )

        with pytest.raises(HTTPException) as exc_info:
            await generate_3d_model(
                {
                    "image_path": "/data/storage/images/plane/000002_plane_cessna caravan_flying.png"
                }
            )

        assert exc_info.value.status_code == 500
        assert "Model generation failed" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_generate_3d_model_file_not_found():
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await generate_3d_model(
                {
                    "image_path": "/data/storage/images/plane/000002_plane_cessna caravan_flying.png"
                }
            )

        assert exc_info.value.status_code == 404
        assert "Image not found" in str(exc_info.value.detail)


if __name__ == "__main__":
    pytest.main([__file__])
