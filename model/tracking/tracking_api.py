from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlmodel import Session, select
import httpx
import os
from models import Image, ModelMetrics
from services import get_db
from typing import List
import json
import logging

# Create logs directory if it doesn't exist
os.makedirs("/app/logs", exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="/app/logs/tracking_api.log",
)
logger = logging.getLogger(__name__)


app = FastAPI()

MODEL_API_URL = "http://model_api_track:8001/generate"


def log_model_metrics(db: Session, **kwargs):
    new_metric = ModelMetrics(**kwargs)
    db.add(new_metric)
    db.commit()
    return new_metric


async def run_experiment(image_name: str, chunk_size: int, mc_resolution: int):
    async with httpx.AsyncClient(timeout=3600) as client:
        try:
            response = await client.post(
                MODEL_API_URL,
                json={
                    "image_name": image_name,
                    "chunk_size": chunk_size,
                    "mc_resolution": mc_resolution,
                },
            )
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
        return None


@app.post("/run_experiments")
async def run_experiments(db: Session = Depends(get_db)):
    categories = ["bicycle"]
    chunk_sizes = [8192, 10240]
    mc_resolutions = [128, 256]

    try:
        for category in categories:
            images = db.exec(
                select(Image).where(Image.image_category == category).limit(2)
            ).all()
            for image in images:
                logger.info(f"image: {image}")
                for chunk_size in chunk_sizes:
                    logger.info(f"chunk_size: {chunk_size}")
                    for mc_resolution in mc_resolutions:
                        logger.info(f"mc_resolution: {mc_resolution}")
                        result = await run_experiment(
                            image.image_name, chunk_size, mc_resolution
                        )
                        if not result:
                            logger.error(
                                f"Failed to generate model for {image.image_name}"
                            )
                            raise HTTPException(
                                status_code=500,
                                detail=f"Failed to generate model for {image.image_name}",
                            )
                        else:
                            log_model_metrics(
                                db=db,
                                object_name=f"{image.image_name}_{chunk_size}_{mc_resolution}",
                                **result["metrics"],
                                chunk_size=chunk_size,
                                mc_resolution=mc_resolution,
                            )
                            logger.info(
                                f"Experiment completed: {image.image_name}, chunk_size={chunk_size}, mc_resolution={mc_resolution}"
                            )
        return {"status": "success", "message": "Experiments completed"}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
