import os
from os import makedirs, path
import requests
from PIL import Image as PILImage
from io import BytesIO
from sqlmodel import Session, create_engine
from models import Image, Movie, Material, Usage
from datetime import datetime
import csv
from collections import Counter
from services import create_db_and_tables
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
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


# API source: Pixabay data collection
def collect_pixabay_data():
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
        makedirs(f"/data/storage/images/{image_category}", exist_ok=True)
        for p in range(1, 2):
            page_url = f"https://pixabay.com/api/?key={key}&category={pixabay_category}&q={image_category}&safesearch=true&page={p}&per_page=2&editors_choice={editors_choice}&colors={colors}&image_type=photo"
            rp = requests.get(page_url)
            if "hits" in rp.text:
                sources = rp.json()["hits"]
                for s, source in enumerate(sources):
                    im_url = source["webformatURL"]
                    im_req = requests.get(im_url)
                    image = PILImage.open(BytesIO(im_req.content))
                    tags = source["tags"].replace(", ", "_")
                    print(p, s, tags)
                    image_name = f'{image_category}/{s:06d}_{tags}{path.splitext(source["webformatURL"])[1]}'
                    image_path = f"/data/storage/images/{image_name}"
                    image.save(image_path)
                    # Insert image data into database
                    image_data = Image(
                        image_name=image_name, image_category=image_category
                    )
                    insert_data(image_data)


collect_pixabay_data()

# CSV and MongoDB source
# Dictionary to store movie data
movie_data = {}
# Read CSV file and process data
with open("/data/storage/sources/IMDB_Movies_Poster_Color.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        movie_title = row["Movie"]
        hex_code = row["Hex Code"]
        count = int(row["Count"])

        # If this is a new movie title, initialize its data
        if movie_title not in movie_data:
            movie_data[movie_title] = {"hex_codes": []}

        # Append the hex code and its count
        movie_data[movie_title]["hex_codes"].append((hex_code, count))

# Process each movie
for title, data in movie_data.items():
    # Get top 5 hex codes
    color_counts = Counter(dict(data["hex_codes"]))
    top_5_colors = color_counts.most_common(5)

    # Query MongoDB for the movie
    movie = movies_collection.find_one({"title": title})

    if movie:
        # Extract required fields from MongoDB
        movie_data = {
            "movie_title": title,  # From the CSv file
            "movie_poster": movie.get("poster", ""),
            "imdb_rating": movie.get("imdb", {}).get("rating"),
            "palette_color1": top_5_colors[0][0] if len(top_5_colors) > 0 else None,
            "palette_color2": top_5_colors[1][0] if len(top_5_colors) > 1 else None,
            "palette_color3": top_5_colors[2][0] if len(top_5_colors) > 2 else None,
            "palette_color4": top_5_colors[3][0] if len(top_5_colors) > 3 else None,
            "palette_color5": top_5_colors[4][0] if len(top_5_colors) > 4 else None,
        }

        # Create Movie object
        movie_obj = Movie(**movie_data)

        # Insert into PostgreSQL
        insert_data(movie_obj)

        print(f"Inserted data for movie: {title}")
    else:
        print(f"Movie not found in MongoDB: {title}")

# Close MongoDB connection
mongo_client.close()
print("Data processing and insertion completed.")


# Generate default data for other tables
def generate_default_data():
    # Default material data
    materials = [
        ("Metal", 0.1, 0.9),
        ("Wood", 0.8, 0.1),
        ("Plastic", 0.5, 0.2),
        ("Glass", 0.1, 0.1),
        ("Fabric", 0.9, 0.0),
    ]
    for name, roughness, metalness in materials:
        material_data = Material(
            material_name=name,
            material_roughness=roughness,
            material_metalness=metalness,
        )
        insert_data(material_data)

    # Default usage data
    for i in range(1, 11):
        usage_data = Usage(
            selection_time=datetime.now(),
            selected_category=["bicycle"],
            selected_image_path="/data/storage/images/bicycle/000017_bicycle_transportation_bike.png",
            selected_movie=i,
            selected_material=i,
            object_3d=f"default_object_{i}.glb",
            object_2d=f"default_render_{i}.mp4",
        )
        insert_data(usage_data)
