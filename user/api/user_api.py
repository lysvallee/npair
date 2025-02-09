import os
import httpx
import json
import base64
from fastapi import FastAPI, Form, Request, WebSocket, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import List
from fastapi.staticfiles import StaticFiles
import time
import logging
import mimetypes
from services import get_db
from sqlmodel import Session
from models import ServiceMetrics
from datetime import datetime

# Setup logging
os.makedirs("/app/logs", exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="/app/logs/user_api.log",
)
logger = logging.getLogger(__name__)


app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

print(f"Current directory: {current_dir}")
print(f"Static directory: {static_dir}")
print(f"Static directory exists: {os.path.exists(static_dir)}")
print(f"Contents of static directory: {os.listdir(static_dir)}")

# Mount the static files directories
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/data", StaticFiles(directory="/data"), name="data")

DATA_API_URL = "http://data_api:8000"
MODEL_API_URL = "http://model_api:8001"
API_KEY = os.getenv("API_KEY")


# Handle Websocket connection issues
async def send_with_retries(websocket, data, max_retries=15, retry_delay=3):
    for attempt in range(max_retries):
        try:
            await websocket.send_text(data)
            return  # If successful, exit the function
        except Exception as e:
            print(f"Send attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                print("Max retries reached. Unable to send data.")
                raise  # Re-raise the last exception if all retries fail


# Helper function to create headers with API key
def get_api_headers():
    return {"Authorization": f"Bearer {API_KEY}"}


@app.get("/")
async def home(request: Request):
    """
    Renders the home page template with the list of image categories.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DATA_API_URL}/categories", headers=get_api_headers()
        )
        categories = response.json()
    return templates.TemplateResponse(
        "home.html", {"request": request, "categories": categories}
    )


@app.post("/selected_category")
async def choose_category(request: Request, selected_category: str = Form(...)):
    """
    Processes the user-selected category and stores it in the database.
    - Validates if at least one category is selected.
    - Retrieves the current timestamp.
    - Creates a new Usage record with selected category and timestamp.
    """
    if not selected_category:
        raise HTTPException(
            status_code=422, detail="Please select at least one category."
        )
    selection_time = datetime.now().isoformat()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DATA_API_URL}/usages",
            json={
                "selected_category": selected_category,
                "selection_time": selection_time,
            },
            headers=get_api_headers(),
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to create usage")
        logger.debug(f"Selection time: {selection_time}")
        logger.debug(f"Selected category: {selected_category}")
    return RedirectResponse(url=f"/category/{selected_category}", status_code=303)


@app.get("/category/{category}")
async def images(request: Request, category: str, page: int = 1):
    page_size = 9  # Number of images per page
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DATA_API_URL}/images/{category}?page={page}&page_size={page_size}",
            headers=get_api_headers(),
        )
        response.raise_for_status()
        image_paths = response.json()
        logger.debug(f"image paths: {image_paths}")
    return templates.TemplateResponse(
        "images.html",
        {
            "request": request,
            "images": image_paths,
            "category": category,
            "current_page": page,
        },
    )


@app.get("/category/load_more/{category}/{page}")
async def load_more(category: str, page: int):
    page_size = 9
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DATA_API_URL}/images/{category}?page={page}&page_size={page_size}",
            headers=get_api_headers(),
        )
        image_paths = response.json()
    return {"images": image_paths}


@app.post("/selected_image")
async def choose_image(request: Request, selected_image_path: str = Form(...)):
    """Associates the selected image with the latest user interaction data.
    - Retrieves the selected image ID from the form data.
    - Queries the database for the latest usage record.
    - Updates the latest usage record with the selected image ID.
    - Sends a POST request to the model API for 3D generation using the image ID.
    - Renders the "result.html" template with the model's response data.
    """
    logger.debug(f"Selected image path: {selected_image_path}")
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{DATA_API_URL}/usages/latest",
            json={"selected_image_path": selected_image_path},
            headers=get_api_headers(),
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to update usage")
    return RedirectResponse(url="/generate_object", status_code=303)


@app.get("/generate_object")
async def generate_object_page(request: Request):
    return templates.TemplateResponse("generate_object.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Set 1 hour timeout
    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout=3600)) as client:
        response = await client.get(
            f"{DATA_API_URL}/usages/latest", headers=get_api_headers()
        )
        if response.status_code != 200:
            await websocket.close(code=1000, reason="Failed to get latest usage")
            return
        latest_usage = response.json()
        image_path = latest_usage.get("selected_image_path")
        logger.debug(f"3D image path: {image_path}")
        response = await client.post(
            f"{MODEL_API_URL}/generate",
            json={"image_path": image_path},
            headers=get_api_headers(),
        )
        if response.status_code != 200:
            await websocket.close(code=1000, reason="Failed to generate model")
            return
        model_data = response.json()
        logger.debug(f"model data: {model_data}")
        response = await client.put(
            f"{DATA_API_URL}/usages/latest",
            json={
                "object_3d": model_data["object_3d"],
                "object_2d": model_data["object_2d"],
            },
            headers=get_api_headers(),
        )
        if response.status_code != 200:
            await websocket.close(code=1000, reason="Failed to update usage")
            return

        with open(model_data["object_2d"], "rb") as image_file:
            render_data = base64.b64encode(image_file.read()).decode("utf-8")
            await send_with_retries(websocket, json.dumps({"render": render_data}))

        await send_with_retries(
            websocket, json.dumps({"object_path": model_data["object_3d"]})
        )


@app.get("/download")
async def download_file(file: str):
    if not file.startswith("/data/storage/objects/"):
        raise HTTPException(status_code=400, detail="Invalid file path")

    if not os.path.exists(file):
        raise HTTPException(status_code=404, detail="File not found")
    logger.debug(f"File to download: {file}")
    return FileResponse(file, filename=os.path.basename(file))


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
