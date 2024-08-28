## 3D Generation App with TripoSR Model

This project provides a web application for generating 3D objects from input images using the TripoSR model ([https://github.com/VAST-AI-Research/TripoSR](https://github.com/VAST-AI-Research/TripoSR)). It leverages FastAPI for building APIs and Docker for containerization.

### Project Overview

The application consists of three main components:

1. **Data API (data_api):** Serves images and tabular data (color palettes, PBR materials) from Apache Cassandra and PostgreSQL databases.
2. **Model API (model_api):** Runs the TripoSR model to generate 3D objects from images received through the API.
3. **User API (user_api):** Receives user input, interacts with the data and model APIs, and provides the generated 3D object to the frontend.

The application can be deployed in production and testing environments using Docker Compose. Monitoring for the user API is also integrated with Grafana.

### Setting Up the Project

**Prerequisites:**

* Docker: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)
* Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
* Python 3.x

**1. Clone the Repository:**

```bash
git clone https://github.com/lysvallee/npair.git
```



**3. Build Docker Images (Optional):**

You can build the Docker images for each component manually:

```bash
cd data/
docker build -t data_api .

cd ../model/
docker build -t model_api .

# ... Repeat for other services (user_api, tests, etc.)
```

**4. Run the Application (Development or Production Mode):**

Navigate to the project directory:

```bash
cd npair
```

Use Docker Compose to build the images and start the application in your desired mode:

```bash
docker-compose -f docker-compose-monitoring.yml up --build
or
docker-compose -f docker-compose-tracking.yml up --build

```

This will build the required images and bring up the concerned services. You can access the APIs at the following default ports:

* Data API: http://localhost:8000 (modify port if needed in the Docker Compose yml)
* Model API: http://localhost:8001
* User API: http://localhost:8002

**5. Run Tests:**

```bash
docker-compose run --rm tests pytest
```

**6. Production Deployment:**

Refer to the `docker-compose-prod.yml` file for configuration details specific to a production environment.

### API Usage

**1. Data API:**

The Data API provides endpoints for accessing images and tabular data. Refer to `data/api/data_api.py` for detailed documentation and available endpoints.

**2. Model API:**

The Model API takes an image as input and generates a 3D object using the TripoSR model. Documentation and endpoint details are available in `model/api/model_api.py`.

**3. User API:**

The User API serves as the primary entry point for users. It interacts with the Data and Model APIs to provide a combined functionality:

* Users can choose an image through a POST request to a specific endpoint.
* The service then calls the Model API with the image path and receives the generated 3D object.
* It retrieves additional data (color palettes, materials) from the Data API that allow further enhancement.
* It returns the final 3D object to the user.

Please refer to `user/api/user_api.py` for specific endpoint details and usage instructions.

**Note:** This is a general overview. Specific API endpoints, request/response formats, and authentication mechanisms might require further exploration within the relevant API code files.

### Monitoring

The user API is integrated with Grafana for monitoring. Please refer to the `user/monitoring` folder for configuration details.


Full file structure:

├── data
│   ├── api
│   │   ├── clear_databases.py
│   │   ├── data_aggregation.py
│   │   ├── data_api.py
│   │   ├── Dockerfile
│   │   ├── extract_brand_palettes.py
│   │   ├── extract_images.py
│   │   ├── extract_materials.py
│   │   ├── extract_movie_palettes.py
│   │   ├── extract_show_palettes.py
│   │   ├── initialize.sh
│   │   ├── initial_setup.py
│   │   ├── models.py
│   │   ├── pip_cache
│   │   ├── requirements.txt
│   │   └── services.py
│   └── storage
│       ├── cdb
│       ├── db
│       ├── images
│       ├── materials
│       ├── objects
│       ├── palettes
│       ├── renders
│       └── tmp
├── docker-compose-data-user.yml
├── docker-compose-monitoring.yml
├── docker-compose-poc.yml
├── docker-compose-prod_add.yml
├── docker-compose-prod.yml
├── docker-compose-shows.yml
├── docker-compose-test.yml
├── docker-compose-tracking.yml
├── grafana
│   ├── data
│   │   ├── csv
│   │   ├── grafana.db
│   │   ├── pdf
│   │   ├── plugins
│   │   └── png
│   └── provisioning
├── logs
│   ├── clear_databases.log
│   ├── create_movies_db.log
│   ├── create_shows_db.log
│   ├── data_api.log
│   ├── extract_movie_palettes.log
│   ├── model_api.log
│   ├── user_api.log
├── model
│   ├── api
│   │   ├── Dockerfile
│   │   ├── model_api.py
│   │   ├── models.py
│   │   ├── pip_cache
│   │   ├── requirements.txt
│   │   ├── services.py
│   │   ├── td.org
│   │   └── triposr
│   ├── huggingface
│   │   └── hub
│   ├── tracking
│   │   ├── Dockerfile
│   │   ├── pip_cache
│   │   └── requirements.txt
│   └── u2net
│       └── u2net.onnx
├── README.md
├── tests
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── test_data_api.py
│   ├── test_model.py
│   └── test_user_api.py
├── tracking
│   └── api
│       └── pip_cache
└── user
    └── api
        ├── Dockerfile
        ├── favicon.ico
        ├── models.py
        ├── pip_cache
        ├── requirements.txt
        ├── services.py
        ├── static
        ├── templates
        └── user_api.py
