from fastapi import FastAPI, HTTPException, Depends, Request
from sqlmodel import Session, select, col
from typing import List
from datetime import datetime
from models import Image, Usage
from services import get_db, create_db_and_tables
import os
import time
import logging
from models import ServiceMetrics
from datetime import datetime

IMAGES_DIR = "/data/storage/images"

# Create logs directory if it doesn't exist
os.makedirs("/app/logs", exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="/app/logs/data_api.log",
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


# Use a callback to trigger the creation of tables if they don't exist yet
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logger.debug("Creating database tables...")


@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Image.image_category).distinct().all()
    logger.debug(f"Categories: {categories}")
    return [category[0] for category in categories]


@app.post("/usages")
def create_usage(usage: dict, db: Session = Depends(get_db)):
    new_usage = Usage(
        selection_time=usage["selection_time"],
        selected_category=usage["selected_category"],
    )
    logger.debug(f"New usage: {new_usage}")
    db.add(new_usage)
    db.commit()
    db.refresh(new_usage)
    return new_usage


@app.get("/usages/latest")
def get_latest_usage(db: Session = Depends(get_db)):
    latest_usage = db.exec(
        select(Usage).order_by(col(Usage.selection_time).desc())
    ).first()
    logger.debug(f"Get latest usage: {latest_usage}")
    if not latest_usage:
        raise HTTPException(status_code=404, detail="No usage found")
    return latest_usage


@app.put("/usages/latest")
def update_latest_usage(update_data: dict, db: Session = Depends(get_db)):
    latest_usage = db.exec(
        select(Usage).order_by(col(Usage.selection_time).desc())
    ).first()
    if not latest_usage:
        raise HTTPException(status_code=404, detail="No usage found")
    for key, value in update_data.items():
        setattr(latest_usage, key, value)
    db.commit()
    db.refresh(latest_usage)
    logger.debug(f"Update latest usage: {update_data}")
    return latest_usage


@app.get("/images/{category}")
def get_images_by_category(
    category: str, page: int = 1, page_size: int = 21, db: Session = Depends(get_db)
):
    try:
        logger.debug(
            f"Fetching images for category: {category}, page: {page}, page_size: {page_size}"
        )
        skip = (page - 1) * page_size
        image_names = (
            db.query(Image.image_name)
            .filter(Image.image_category == category)
            .offset(skip)
            .limit(page_size)
            .all()
        )
        logger.debug(f"Images names: {image_names}")
        logger.debug(f"Fetched {len(image_names)} images")
        image_paths = []
        for image_name in image_names:
            image_path = os.path.join(IMAGES_DIR, image_name[0])
            image_paths.append(image_path)
        logger.debug(f"image paths: {image_paths}")
        return image_paths
    except Exception as e:
        logger.error(f"Error fetching images: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
