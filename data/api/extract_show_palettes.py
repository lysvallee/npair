from sqlmodel import Session, select, create_engine, SQLModel
from models import Show, Tmdb
import logging
import os
import time
import json
import requests
from io import BytesIO
from colorthief import ColorThief
from services import create_db_and_tables

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="/app/logs/extract_show_palettes.log",
)
logger = logging.getLogger(__name__)

# Database URLs
NPAIR_DB_URL = os.environ.get("NPAIR_DB_URL")
engine = create_engine(NPAIR_DB_URL)

create_db_and_tables()


# Function to insert data into the npair_db database
def insert_data(data):
    with Session(engine) as session:
        session.add(data)
        session.commit()


# Function to get the color palette from a poster image
def get_color_palette(poster_path):
    logger.debug(f"Attempting to generate color palette for {poster_path}")
    try:
        image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        response = requests.get(image_url)
        img = BytesIO(response.content)
        color_thief = ColorThief(img)
        palette = color_thief.get_palette(color_count=5)
        logger.info(f"Successfully generated palette for {image_url}")
        return json.dumps(palette)
    except Exception as e:
        logger.error(f"Error generating palette for {image_url}: {str(e)}")
        return json.dumps([])  # Return empty JSON list on error


# Function to extract shows from the tmdb database and insert processed data into npair_db
def insert_shows():
    logger.debug("Attempting to retrieve shows from the tmdb table")

    max_retries = 20
    retry_interval = 40

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} to connect to the tmdb table")
            with Session(engine) as session:
                # Retrieve shows from the tmdb table
                query = select(Tmdb.name, Tmdb.poster_path).select_from(
                    SQLModel.metadata.tables["tmdb"]
                )
                shows = session.exec(query).all()

                logger.info(f"Retrieved {len(shows)} shows from PostgreSQL")

                # Insert show palettes into the show table
                for show in shows:
                    try:
                        name = show.name
                        poster_path = show.poster_path

                        logger.debug(f"Generating palette for show: {name}")
                        show_palette = get_color_palette(poster_path)

                        # Create a Show object with the title and palette
                        show_data = Show(show_title=name, show_palette=show_palette)
                        insert_data(show_data)

                    except Exception as e:
                        logger.error(f"Error generating palette for {name}: {str(e)}")
            break
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            logger.info(f"Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)


if __name__ == "__main__":
    insert_shows()
