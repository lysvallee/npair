import os
import logging
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, create_engine, Session
from statistics import mean
from models import Material

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="/app/logs/extract_materials.log",
)
logger = logging.getLogger(__name__)

# Database connection
NPAIR_DB_URL = os.environ.get("NPAIR_DB_URL")
engine = create_engine(NPAIR_DB_URL)

# Create the material table in the database if it doesn't exist
SQLModel.metadata.create_all(engine)


def add_row(material_name, roughness, metalness):
    """
    Adds a single row of material data to the database.

    Args:
        material_name (str): The name of the material.
        roughness (float): The roughness value of the material.
        metalness (float): The metalness value of the material.
    """
    try:
        with Session(engine) as session:
            material = Material(
                material_name=material_name,
                material_roughness=roughness,
                material_metalness=metalness,
            )
            session.add(material)
            session.commit()
            logger.info(f"Inserted material: {material_name}")
    except Exception as e:
        logger.error(f"Failed to insert material {material_name}: {str(e)}")


# HTML file to be parsed
html_file = "/data/storage/materials/Material References Documentation - Roblox Creator Hub.html"


def insert_materials():
    """
    Parses an HTML file containing material information and inserts the data into the database.
    """
    try:
        # Open and parse the HTML file
        with open(html_file, "r", encoding="utf-8") as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # Find all material sections in the HTML
        material_sections = soup.find_all(
            "div",
            class_="MuiGrid-root web-blox-css-tss-spvy06-Grid-root MuiGrid-item MuiGrid-grid-xs-6 MuiGrid-grid-lg-3 web-blox-css-mui-1y5f5z7",
        )

        # Loop through each section and extract data
        for section in material_sections:
            try:
                figcaption = section.find("figcaption")
                material_name = figcaption.find("b").text.strip()

                # Extract roughness and metalness values
                info_lines = figcaption.text.split(material_name)[1].split("  ")
                material_info = {}
                for info_line in info_lines:
                    key, value = info_line.split(": ")
                    if "-" in value:
                        # If value is a range, take the average
                        value_low, value_high = map(float, value.split("-"))
                        value = mean([value_low, value_high])
                        material_info[key] = round(float(value), 2)

                roughness = material_info.get("Roughness")
                metalness = material_info.get("Metalness")

                # Add the extracted data into the database
                add_row(material_name, roughness, metalness)

            except Exception as section_error:
                logger.error(f"Failed to process section: {str(section_error)}")

    except Exception as file_error:
        logger.error(f"Failed to open or parse the HTML file: {str(file_error)}")


if __name__ == "__main__":
    insert_materials()
