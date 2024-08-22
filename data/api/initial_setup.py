from extract_images import insert_images
from extract_movie_palettes import insert_movies
from extract_show_palettes import insert_shows
from extract_brand_palettes import insert_brands
from extract_materials import insert_materials
from clear_databases import clear_postgresql_db, clear_cassandra_db

if __name__ == "__main__":
    # Clear previous definitions
    #    clear_postgresql_db()
    #    clear_cassandra_db()

    # Extract images from querying the Pixabay API
    insert_images()

    # Extract movie palettes from the Cassandra database
    # insert_movies()

    # Extract show palettes from the postgresSQL database
    # insert_shows()

    # Extract brand palettes from the CSV fle
    # insert_brands()

    # Extract materials from parsing the html file
    # insert_materials()

    print("Initial setup complete.")
