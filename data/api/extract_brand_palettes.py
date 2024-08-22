import re
import os
import csv
import time
import logging
from sqlmodel import SQLModel, Field, create_engine, Session
from models import Brand
from services import create_db_and_tables

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL
NPAIR_DB_URL = os.environ.get("NPAIR_DB_URL")
engine = create_engine(NPAIR_DB_URL)

create_db_and_tables()

# Path to the CSV file
csv_file = "/data/storage/palettes/brand_palettes.csv"


def insert_data(data):
    """Insert a single data entry into the database."""
    with Session(engine) as session:
        session.add(data)
        session.commit()


def extract_english_characters(brand_name):
    # Use regular expression to match English characters (a-zA-Z), numbers (0-9), and the '-' character
    characters = re.findall(r"[a-zA-Z0-9-]", brand_name)
    return "".join(characters)


def insert_brands():
    max_retries = 20
    retry_interval = 40

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} to insert brands into the database")

            # Open and read the CSV file
            with open(csv_file, "r", encoding="utf-8") as file:
                csv_reader = csv.DictReader(file)

                count = 0  # Counter for inserted rows

                for row in csv_reader:
                    # Extract English characters from brand_name
                    brand_name = extract_english_characters(row["brand_name"])

                    # Check if brand_name is not empty
                    if brand_name:
                        # Create a Brand instance for the row
                        brand = Brand(
                            brand_name=brand_name,
                            brand_palette=row["brand_palette"],
                        )
                        # Insert the brand instance using the insert_data function
                        insert_data(brand)
                        count += 1

                logger.info(f"Inserted {count} rows into the 'Brand' table.")

            # Break out of the retry loop if successful
            break

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            logger.exception("Full traceback:")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                logger.error(
                    "Max retries reached. Failed to insert brands into the database."
                )


if __name__ == "__main__":
    insert_brands()
