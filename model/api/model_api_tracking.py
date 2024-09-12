from fastapi import FastAPI, HTTPException, Request
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sqlmodel import SQLModel, Field, Session
import os
import re
import shutil
import subprocess
import logging
import time
from glob import glob
from services import get_db
from models import ModelMetrics
from datetime import datetime
from typing import Optional

# Create logs directory if it doesn't exist
os.makedirs("/app/logs", exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="/app/logs/model_api.log",
)
logger = logging.getLogger(__name__)


app = FastAPI()


def parse_model_output(output: str):
    metrics = {}

    # Regular expressions to match the time entries
    patterns = {
        "initialization_time_ms": r"Initializing model finished in (\d+\.\d+)ms",
        "processing_time_ms": r"Processing images finished in (\d+\.\d+)ms",
        "running_time_ms": r"Running model finished in (\d+\.\d+)ms",
        "rendering_time_ms": r"Rendering finished in (\d+\.\d+)ms",
        "mesh_extraction_time_ms": r"Extracting mesh finished in (\d+\.\d+)ms",
        "mesh_export_time_ms": r"Exporting mesh finished in (\d+\.\d+)ms",
    }

    for metric, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            metrics[metric] = float(match.group(1))

    # Calculate total time
    metrics["total_time_ms"] = sum(metrics.values())

    # Extract object name (assuming it's the filename without extension)
    object_name_match = re.search(r"/objects/(\w+)", output)
    if object_name_match:
        metrics["object_name"] = object_name_match.group(1)

    return metrics


@app.websocket("/generate")
async def generate_3d_model(websocket: WebSocket):
    await websocket.accept()

    try:
        model_parameters = await websocket.receive_json()
        image_name = model_parameters.get("image_name")
        image_path = f"/data/storage/images/{image_name}"

        logger.debug(f"Image path received by the model: {image_path}")

        if not os.path.exists(image_path):
            await websocket.send_json({"error": "Image not found"})
            return

        command = [
            "python3",
            "/app/triposr/run.py",
            image_path,
            "--model-save-format",
            "glb",
            "--render",
            "--chunk-size",
            str(model_parameters.get("chunk_size", 4096)),
            "--mc-resolution",
            str(model_parameters.get("mc_resolution", 128)),
            "--output-dir",
            OBJECTS_DIR,
        ]

        logger.debug(f"Running command: {' '.join(command)}")

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            standard_output = result.stdout
            standard_error = result.stderr
            logger.debug(f"Subprocess output: {standard_output}")
            logger.debug(f"Subprocess error: {standard_error}")

            # Extract metrics from standard output
            metrics = parse_model_output(standard_output)
            await websocket.send_json({"metrics": metrics})

        except subprocess.CalledProcessError as e:
            logger.error(f"Model generation failed: {e.stderr}")
            await websocket.send_json({"error": f"Model generation failed: {e.stderr}"})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        await websocket.send_json({"error": f"An unexpected error occurred: {str(e)}"})
    finally:
        await websocket.close()
