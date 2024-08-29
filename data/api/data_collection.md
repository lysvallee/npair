## Image Extraction Process

The `extract_images.py` script is responsible for collecting and storing images from the Pixabay API. Here are the key aspects of the data collection process:

1. **Data Source**: The script fetches images from the Pixabay API, focusing on the "transportation" category.

2. **Query Parameters**: 
   - Categories: bicycle, bus, car, plane, truck
   - Color filter: transparent (to ensure images have transparent backgrounds)
   - Safe search: enabled
   - Number of images per page: 50
   - Image type: photo

3. **Filtering Criteria**:
   - The script checks that the image tags include the queried category.
   - It verifies that the image borders are transparent using the `check_image_borders` function.

4. **Data Storage**:
   - Images are saved in category-specific directories within `/data/storage/images/`.
   - Image metadata (name and category) is stored in a PostgreSQL database.

5. **Optimizations**:
   - The script uses a two-page request per category to minimize API calls.
   - It implements error handling and logging to manage potential issues during the extraction process.

6. **Database Operations**:
   - The script uses SQLModel for database interactions.
   - It employs session-based transactions to ensure data integrity when inserting records.

This extraction process ensures that only relevant, high-quality images with transparent backgrounds are collected and properly categorized in both the file system and the database.



## Movie Palette Extraction Process

The `extract_movie_palettes.py` script is responsible for retrieving movie data from the Cassandra database and generating color palettes for movie posters. Here are the key aspects of this data collection process:

1. **Data Source**: 
   - The script retrieves movie data (title and poster path) from the Cassandra database.
   - It uses the "tmdb" keyspace in Cassandra.

2. **Query**: 
   - A simple SELECT query is used to fetch all movies: `SELECT title, poster_path FROM movies`

3. **Connection Handling**:
   - The script implements a retry mechanism for connecting to Cassandra.
   - It attempts to connect up to 20 times, with a 40-second interval between attempts.

4. **Data Processing**:
   - For each movie, the script generates a color palette from the movie's poster.
   - The `get_color_palette()` function fetches the poster image and extracts a 5-color palette.

5. **Data Storage**:
   - Movie data (title and generated color palette) is inserted into the PostgreSQL database using SQLModel.

6. **Error Handling**:
   - The script logs errors for individual movie processing failures.
   - It also handles and logs any database connection errors.

7. **Optimizations**:
   - The script converts the Cassandra query result to a list for easier manipulation.
   - It uses a RoundRobinPolicy for load balancing in the Cassandra connection.



## TV Show Palette Extraction Process

The `extract_show_palettes.py` script is responsible for retrieving TV show data from a PostgreSQL database and generating color palettes for show posters. Here are the key aspects of this data collection process:

1. **Data Source**: 
   - The script retrieves TV show data (name and poster path) from a PostgreSQL database.
   - It specifically queries the "tmdb" table within the database.

2. **Query**: 
   - An SQLModel query is used to fetch all shows: `select(Tmdb.name, Tmdb.poster_path).select_from(SQLModel.metadata.tables["tmdb"])`

3. **Connection Handling**:
   - The script implements a retry mechanism for connecting to PostgreSQL.
   - It attempts to connect up to 20 times, with a 40-second interval between attempts.

4. **Data Processing**:
   - For each show, the script generates a color palette from the show's poster.
   - The `get_color_palette()` function is used to fetch the poster image and extract the color palette.

5. **Data Storage**:
   - Show data (title and generated color palette) is inserted into a separate table in the PostgreSQL database using SQLModel.
   - The `insert_data()` function is used to perform the insertion.

6. **Error Handling**:
   - The script logs errors for individual show processing failures.
   - It also handles and logs any database connection errors.

7. **Optimizations**:
   - The script uses SQLModel's `select()` function for efficient querying.
   - It processes shows in batches by fetching all results at once and then iterating over them.




## Brand Palette Extraction Process

The `extract_brand_palettes.py` script is responsible for reading brand data from a CSV file, processing it, and inserting it into a database. Here are the key aspects of this data collection process:

1. **Data Source**: 
   - The script reads brand data from a CSV file.
   - The CSV file is expected to contain columns for brand names and brand palettes.

2. **Data Processing**:
   - The script processes each row of the CSV file.
   - It uses a custom function `extract_english_characters()` to clean the brand names:
     - This function extracts only English characters, numbers, and hyphens from the brand names.
     - This ensures consistency and removes any potentially problematic characters.

3. **Data Insertion**:
   - For each valid brand (with a non-empty name after processing), a Brand object is created.
   - The Brand object includes the processed brand name and the brand palette.
   - Each Brand object is inserted into the database using an `insert_data()` function.

4. **Error Handling and Retry Logic**:
   - The script implements a retry mechanism for database insertion.
   - It attempts to process and insert the data up to 20 times, with a 40-second interval between attempts.
   - Detailed error logging is implemented, including full tracebacks for debugging.

5. **Logging**:
   - The script logs various information throughout the process:
     - Attempt numbers for database insertion
     - Number of successfully inserted rows
     - Error messages and tracebacks in case of failures

6. **Data Validation**:
   - The script only inserts brands with non-empty names after character extraction.
   - This helps to ensure data quality in the database.

This extraction process ensures that brand data is cleaned, validated, and safely inserted into the database.




## Material Properties Extraction Process

The `extract_materials.py` script is responsible for parsing an HTML file containing material information and inserting this data into a database. Here are the key aspects of this data collection process:

1. **Data Source**: 
   - The script reads material data from an HTML file: "Material References Documentation - Roblox Creator Hub.html".
   - This file contains structured information about various materials and their properties.

2. **HTML Parsing**:
   - The script uses BeautifulSoup to parse the HTML content.
   - It specifically looks for div elements with a particular class that represents individual material sections.

3. **Data Extraction**:
   - For each material section, the script extracts:
     - Material name
     - Roughness value
     - Metalness value
   - If a property value is given as a range (e.g., "0.2-0.4"), the script calculates the average.

4. **Data Processing**:
   - The extracted numerical values (roughness and metalness) are rounded to two decimal places.

5. **Database Insertion**:
   - For each material, a Material object is created with the extracted data.
   - This object is then inserted into the database using SQLModel.

6. **Error Handling**:
   - The script implements error handling at multiple levels:
     - For the overall file parsing process
     - For individual material section processing
     - For database insertion of each material
   - Detailed error messages are logged for debugging purposes.

7. **Logging**:
   - The script logs various information throughout the process:
     - Successful insertion of each material
     - Errors encountered during file parsing, section processing, or database insertion

The error handling at multiple levels makes the script robust against various potential issues, such as unexpected HTML structure. The use of logging aids in troubleshooting any issues that may arise.




## Data Aggregation and Import Process

The `initial_setup.py` script serves as the main entry point for the data aggregation and import process. This script orchestrates the extraction of data from various sources and its subsequent import into the final database. It combines both the aggregation of diverse data types and the import functionality into a single, streamlined process.

### Script Overview

The script performs the following steps in sequence:

1. **Image Data**: Extracts images by querying the Pixabay API and imports them.
2. **Movie Palettes**: Retrieves movie palette data from a Cassandra database and imports it.
3. **TV Show Palettes**: Extracts TV show palette data from a PostgreSQL database and imports it.
4. **Brand Palettes**: Reads brand palette information from a CSV file and imports it.
5. **Material Properties**: Parses material property data from an HTML file and imports it.

### Dependencies

The script relies on the following custom modules:

- `extract_images`
- `extract_movie_palettes`
- `extract_show_palettes`
- `extract_brand_palettes`
- `extract_materials`

Each of these modules contains a specific `insert_*()` function that handles both the extraction and import of its respective data type.

### Execution

To run the data aggregation and import process:

```
python initial_setup.py
```

### Logical Flow

1. The script first imports all necessary functions from the individual extraction modules.
2. It then executes each `insert_*()` function in a specific order, ensuring that all data types are processed sequentially.
3. After all data has been aggregated and imported, a completion message is printed.

### Data Cleaning and Homogenization

Each individual extraction module (`extract_*.py`) is responsible for its own data cleaning and format homogenization. Please refer to the documentation of each module for specific details on how data is processed before import.

### Best Practices

- **Modularity**: Each data type is handled by a separate module, allowing for easy maintenance and updates.
- **Sequential Processing**: Data is processed in a defined order, preventing potential conflicts or dependencies.
- **Error Handling**: Each `insert_*()` function includes its own error handling, ensuring that issues with one data type don't affect the entire process.
- **Logging**: Detailed logging is implemented in each module, facilitating debugging and monitoring of the aggregation and import process.

These practices ensure that data from multiple sources and in various formats is safely aggregated and imported into our final database.
