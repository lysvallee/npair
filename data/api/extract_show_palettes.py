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
    """
    Insert data into the database.
    Uses a session to ensure data integrity and proper transaction handling.
    """
    with Session(engine) as session:
        session.add(data)
        session.commit()


def get_color_palette(poster_path):
    """
    This function retrieves a color palette from a movie poster image URL.

    Args:
        poster_path (str): The path to the movie poster image on TMDB.

    Returns:
        str (JSON): A JSON-formatted string representing the color palette as a list.
            - On success: Contains a list of 5 RGB color values (e.g., [ [255, 0, 0], ... ]).
            - On error: Returns an empty JSON list ( `[]` ).
    """

    logger.debug(f"Attempting to generate color palette for {poster_path}")

    try:
        # Construct the full image URL based on TMDB's poster path format
        image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"

        # Download the image content as a byte stream
        response = requests.get(image_url)
        img = BytesIO(response.content)

        # Use ColorThief library to extract a 5-color palette from the image
        color_thief = ColorThief(img)
        palette = color_thief.get_palette(color_count=5)

        logger.info(f"Successfully generated palette for {image_url}")
        return json.dumps(palette)  # Return the palette as JSON

    except Exception as e:
        logger.error(f"Error generating palette for {image_url}: {str(e)}")
        return json.dumps([])  # Return empty JSON list on any exception


def insert_shows():
    """
    Retrieves show data from the tmdb table in PostgreSQL and inserts color palettes into the show table.
    Implements retry logic for database connection and error handling for each show.
    """
    logger.debug("Attempting to retrieve shows from the tmdb table")

    max_retries = 20
    retry_interval = 40

    for attempt in range(max_retries):
        try:
            # Attempt to connect to PostgreSQL with retry logic
            logger.info(f"Attempt {attempt + 1} to connect to the tmdb table")
            with Session(engine) as session:
                # Construct query to select name and poster_path from tmdb table
                query = select(Tmdb.name, Tmdb.poster_path).select_from(
                    SQLModel.metadata.tables["tmdb"]
                )
                # Execute query and fetch all results
                shows = session.exec(query).all()

                logger.info(f"Retrieved {len(shows)} shows from PostgreSQL")

                # Process each show and insert palette into the show table
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
                        # Break the retry loop if successful
            break
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            logger.info(f"Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)


if __name__ == "__main__":
    insert_shows()
