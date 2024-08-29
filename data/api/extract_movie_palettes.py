import os
import json
import logging
import requests
import time
from sqlmodel import Session, create_engine
from io import BytesIO
from colorthief import ColorThief
from cassandra.cluster import Cluster
from cassandra.policies import RoundRobinPolicy
from models import Movie
from services import create_db_and_tables

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="/app/logs/extract_movie_palettes.log",
)
logger = logging.getLogger(__name__)

# PostgreSQL connection
NPAIR_DB_URL = os.environ.get("NPAIR_DB_URL")
engine = create_engine(NPAIR_DB_URL)

create_db_and_tables()


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


def insert_movies():
    """
    Retrieves movie data from Cassandra database and inserts color palettes into PostgreSQL.
    Implements retry logic for Cassandra connection and error handling for each movie.
    """
    logger.debug("Attempting to retrieve movies from Cassandra")
    cassandra_host = os.environ.get("CASSANDRA_HOST", "cassandra")

    max_retries = 20
    retry_interval = 40

    for attempt in range(max_retries):
        try:
            # Attempt to connect to Cassandra with retry logic
            logger.info(f"Attempt {attempt + 1} to connect to Cassandra")
            cluster = Cluster(
                ["cassandra"],
                load_balancing_policy=RoundRobinPolicy(),
                protocol_version=5,
            )
            session = cluster.connect()

            # Set keyspace for the session
            session.set_keyspace("tmdb")

            # Execute query to retrieve all movies
            rows = session.execute("SELECT title, poster_path FROM movies")

            # Convert ResultSet to list for easier manipulation
            movies = list(rows)

            logger.info(f"Retrieved {len(movies)} movies from Cassandra")

            # Process each movie and insert palette into PostgreSQL
            for movie in movies:
                try:
                    title = movie[0]
                    poster_path = movie[1]

                    logger.debug(f"Generating palette for movie: {title}")
                    movie_palette = get_color_palette(poster_path)
                    movie_data = Movie(movie_title=title, movie_palette=movie_palette)
                    insert_data(movie_data)

                except Exception as e:
                    logger.error(f"Error generating palette for {title}: {str(e)}")
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            logger.info(f"Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
        finally:
            # Ensure cluster connection is closed
            if "cluster" in locals():
                cluster.shutdown()
        return []


if __name__ == "__main__":
    insert_movies()
