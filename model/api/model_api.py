from fastapi import FastAPI, HTTPException, Request
from sqlmodel import SQLModel, Field
import os
import shutil
import subprocess
import logging
import time
from glob import glob
from services import get_db
from sqlmodel import Session
from models import ServiceMetrics
from datetime import datetime

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


# Log the metrics that will be sent to Grafana via the postgreSQL database
def log_response_time(
    db: Session,
    service_name: str,
    endpoint: str,
    response_time: float,
    status_code: int,
):
    new_metric = ServiceMetrics(
        service_name=service_name,
        endpoint=endpoint,
        response_time=response_time,
        status_code=status_code,
        timestamp=datetime.utcnow(),
    )
    db.add(new_metric)
    db.commit()
    db.refresh(new_metric)
    return new_metric


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

    # Use a new database session for logging
    db = next(get_db())
    try:
        log_response_time(
            db=db,
            service_name="model_api",
            endpoint=request.url.path,
            response_time=response_time,
            status_code=response.status_code,
        )
    finally:
        db.close()  # Ensure the database session is closed

    return response


OBJECTS_DIR = "/data/storage/objects"
RENDERS_DIR = "/data/storage/renders"


@app.post("/generate")
async def generate_3d_model(model_parameters: dict):
    chunk_size = "8192"
    mc_resolution = "256"
    image_path = model_parameters["image_path"]
    logger.debug(f"Image path received by the model: {image_path}")
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    # Run the model using subprocess
    try:
        result = subprocess.run(
            [
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
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        # Access the captured output from the result object
        standard_output = result.stdout
        standard_error = result.stderr
        logger.debug(f"Subprocess output: {standard_output}")
        logger.debug(f"Subprocess error: {standard_error}")
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Model generation failed: {e.stderr}"
        )
    logger.debug(f"Subprocess run succesful")
    # Check if the 3D object was created
    generated_object = os.path.join(OBJECTS_DIR, "mesh.glb")
    if not os.path.exists(generated_object):
        raise HTTPException(
            status_code=500,
            detail="Model generation did not produce expected output files",
        )
    # Define the output gif path
    render_gif = os.path.join(OBJECTS_DIR, "render.gif")
    # Generate unique names for the output files
    base_name = os.path.basename(image_path)
    base_name = os.path.splitext(base_name)[0]
    object_3d_name = f"{base_name}.glb"
    object_2d_name = f"{base_name}.gif"
    object_3d_path = os.path.join(OBJECTS_DIR, object_3d_name)
    object_2d_path = os.path.join(RENDERS_DIR, object_2d_name)
    logger.debug(f"Paths generated by the model: {object_3d_path, object_2d_path}")
    # Move the results to the appropriate folders and delete intermediate images
    shutil.move(generated_object, object_3d_path)
    shutil.move(render_gif, object_2d_path)
    png_files = glob(os.path.join(OBJECTS_DIR, "*.png"))
    for png_file in png_files:
        os.remove(png_file)
    model_data = {"object_3d": object_3d_path, "object_2d": object_2d_path}
    return model_data
