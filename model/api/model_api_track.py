from fastapi import FastAPI, HTTPException, Request
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
    filename="/app/logs/model_api_track.log",
)
logger = logging.getLogger(__name__)

OBJECTS_DIR = "/data/storage/objects"
RENDERS_DIR = "/data/storage/renders"

app = FastAPI()

# API_KEY = os.getenv("API_KEY")

# @app.middleware("http")
# async def validate_api_key(request: Request, call_next):
#     if request.headers.get("Authorization") != f"Bearer {API_KEY}":
#         raise HTTPException(status_code=403, detail="Invalid API key")
#     return await call_next(request)


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

    return metrics


# The new HTTP POST endpoint for generating 3D models
@app.post("/generate")
async def generate_3d_model(request: Request):
    try:
        # Parse JSON data from the incoming request
        model_parameters = await request.json()
        image_name = model_parameters.get("image_name")
        image_path = f"/data/storage/images/{image_name}"
        logger.debug(f"Image path received by the model: {image_path}")

        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found")
        # Retrieve hyperparameters
        chunk_size = str(model_parameters.get("chunk_size", 8192))
        mc_resolution = str(model_parameters.get("mc_resolution", 256))
        # Command to run the external process for model generation
        command = [
            "python3",
            "/app/triposr/run.py",
            image_path,
            "--model-save-format",
            "glb",
            "--render",
            "--chunk-size",
            chunk_size,
            "--mc-resolution",
            mc_resolution,
            "--output-dir",
            OBJECTS_DIR,
        ]

        logger.debug(f"Running command: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,  # Capture stdout
                stderr=subprocess.STDOUT,  # Redirect stderr to stdout
                text=True,
            )
            standard_output = result.stdout
            logger.debug(
                f"Subprocess output (combined stdout and stderr): {standard_output}"
            )

            # Extract metrics from standard output
            metrics = parse_model_output(standard_output)
            return {"metrics": metrics}

        except subprocess.CalledProcessError as e:
            logger.error(f"Model generation failed: {e.stderr}")
            raise HTTPException(
                status_code=500, detail=f"Model generation failed: {e.stderr}"
            )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
