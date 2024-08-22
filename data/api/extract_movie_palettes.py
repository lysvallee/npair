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
    with Session(engine) as session:
        session.add(data)
        session.commit()


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


def insert_movies():
    logger.debug("Attempting to retrieve movies from Cassandra")
    cassandra_host = os.environ.get("CASSANDRA_HOST", "cassandra")

    max_retries = 20
    retry_interval = 40

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} to connect to Cassandra")
            cluster = Cluster(
                ["cassandra"],
                load_balancing_policy=RoundRobinPolicy(),
                protocol_version=5,
            )
            session = cluster.connect()

            # Connect to Cassandra
            cluster = Cluster([cassandra_host])
            session = cluster.connect()

            # Use the tmdb keyspace
            session.set_keyspace("tmdb")

            # Retrieve movies
            rows = session.execute("SELECT title, poster_path FROM movies")

            # Convert the ResultSet to a list to allow len() and indexing
            movies = list(rows)

            logger.info(f"Retrieved {len(movies)} movies from Cassandra")

            # Insert movie palettes into the database
            for movie in movies:
                try:
                    # Access tuple elements by index instead of string keys
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
            if "cluster" in locals():
                cluster.shutdown()
        return []


if __name__ == "__main__":
    insert_movies()
