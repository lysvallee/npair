import os
import requests
from PIL import Image as PILImage
from io import BytesIO
from sqlmodel import Session, create_engine
from models import Image
from datetime import datetime
import csv
from collections import Counter
from services import create_db_and_tables
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# PostgreSQL connection
NPAIR_DB_URL = os.environ.get("NPAIR_DB_URL")
engine = create_engine(NPAIR_DB_URL)

create_db_and_tables()


def insert_data(data):
    """
    Insert data into the database.
    Use a session to ensure data integrity and proper transaction handling.
    """
    with Session(engine) as session:
        session.add(data)
        session.commit()


def check_image_borders(image, image_category, p, s):
    """
    Check the alpha values of the border pixels.
    Discard the image if any border pixel has an alpha value different than 0.
    Return the image if it passes the check.
    """
    # Ensure the image has an alpha channel
    if image.mode != "RGBA":
        print(
            f"Category={image_category} - Page={p} - Image={s} No alpha channel. Discarded."
        )
        return None

    # Load pixel data
    pixels = image.load()

    # Get image dimensions
    width, height = image.size

    # Check top row
    for x in range(width):
        if pixels[x, 0][3] != 0:  # [3] accesses the alpha value in RGBA
            print(
                f"Category={image_category} - Page={p} - Image={s} Non-zero alpha at the top border. Discarded."
            )
            return None

    # Check bottom row
    for x in range(width):
        if pixels[x, height - 1][3] != 0:
            print(
                f"Category={image_category} - Page={p} - Image={s} Non-zero alpha at the bottom border. Discarded."
            )
            return None

    # Check left column
    for y in range(height):
        if pixels[0, y][3] != 0:
            print(
                f"Category={image_category} - Page={p} - Image={s} Non-zero alpha at the left border. Discarded."
            )
            return None

    # Check right column
    for y in range(height):
        if pixels[width - 1, y][3] != 0:
            print(
                f"Category={image_category} - Page={p} - Image={s} Non-zero alpha at the right border. Discarded."
            )
            return None

    # If all checks passed, return the image
    return image


def insert_images():
    """
    Main function to fetch and insert images from Pixabay API.
    Implements filtering by category, color (transparent), and tags.
    Optimizes API usage by limiting requests to 50 images per page.
    """
    # API key and query parameters
    key = "9831243-d1ff87804d4b3508285497c61"
    editors_choice = "false"
    colors = "transparent"
    pixabay_category = "transportation"
    queries = [
        "bicycle",
        "bus",
        "car",
        "plane",
        "truck",
    ]

    for image_category in queries:
        # Create directory for each category
        os.makedirs(f"/data/storage/images/{image_category}", exist_ok=True)
        for p in range(1, 3):
            try:
                # Construct API URL with query parameters
                page_url = f"https://pixabay.com/api/?key={key}&category={pixabay_category}&q={image_category}&safesearch=true&page={p}&per_page=50&editors_choice={editors_choice}&colors={colors}&image_type=photo"
                rp = requests.get(page_url)
                rp.raise_for_status()  # Raise an error for bad HTTP status codes

                if "hits" in rp.json():
                    sources = rp.json()["hits"]
                    for s, source in enumerate(sources):
                        # Filter images by checking tags
                        tags = source["tags"].replace(", ", "_")
                        if image_category in tags:
                            logging.info(
                                f"Category={image_category} - Page={p} - Image={s} - Tags={tags}"
                            )

                            try:
                                # Download and process image
                                im_url = source["webformatURL"]
                                im_req = requests.get(im_url)
                                im_req.raise_for_status()
                                image = PILImage.open(BytesIO(im_req.content))

                                # Check image borders for transparency
                                result = check_image_borders(
                                    image, image_category, p, s
                                )
                                if result:
                                    # Save image and insert data into database
                                    image_name = f'{image_category}/{s:06d}_{tags}{os.path.splitext(source["webformatURL"])[1]}'
                                    image_path = f"/data/storage/images/{image_name}"
                                    image.save(image_path)

                                    image_data = Image(
                                        image_name=image_name,
                                        image_category=image_category,
                                    )
                                    insert_data(image_data)

                            except Exception as e:
                                logging.error(
                                    f"Failed to process image from {im_url}: {str(e)}"
                                )
            except Exception as e:
                logging.error(
                    f"Failed to fetch data from Pixabay API for query {image_category}, page {p}: {str(e)}"
                )


if __name__ == "__main__":
    insert_images()
