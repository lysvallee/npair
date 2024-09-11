# Import functions from individual extraction scripts
from extract_images import insert_images
from extract_movie_palettes import insert_movies
from extract_show_palettes import insert_shows
from extract_brand_palettes import insert_brands
from extract_materials import insert_materials

if __name__ == "__main__":
    # Data Aggregation and Import Process

    # Step 1: Extract and import images from Pixabay API
    insert_images()

    # Step 2: Extract movie palettes from Cassandra database and import
    #    insert_movies()

    # Step 3: Extract show palettes from PostgreSQL database and import
    #    insert_shows()

    # Step 4: Extract brand palettes from CSV file and import
    #    insert_brands()

    # Step 5: Extract material properties from HTML file and import
    #    insert_materials()

    print("Initial setup complete: Data aggregation and import finished.")
