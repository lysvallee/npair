# Ethical 3D Content Generation 🌟

## Overview
A proof-of-concept web application demonstrating responsible AI-powered 3D object generation, built with a commitment to copyright respect and ethical AI practices.

## Key Features
- 🤖 Utilizes TripoSR model for 3D object generation
- 🖼️ Powered by Pixabay's royalty-free image database
- 🛡️ 100% legal AI workflow
- 🚀 Built with FastAPI and Docker for robust deployment

## The Ethical AI Approach
This project showcases how AI can generate 3D content while maintaining strict adherence to copyright principles:
- Model trained on CC-BY licensed Objaverse dataset
- Input images sourced from Pixabay's comprehensive royalty-free library

## Tech Stack
- FastAPI
- Docker
- TripoSR Model
- Pixabay API

The application consists of three main components:
1. **Data API (data_api):** Serves images and tabular data (color palettes, PBR materials) from Apache Cassandra and PostgreSQL databases.
2. **Model API (model_api):** Runs the TripoSR model to generate 3D objects from images received through the API.
3. **User API (user_api):** Receives user input, interacts with the data and model APIs, and provides the generated 3D object to the frontend.

It can be deployed in production and testing environments using Docker Compose. Monitoring for the user API is also integrated with Grafana.

## Setting Up the Project

**Prerequisites:**

* Docker: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)
* Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
* Python 3.x

**1. Clone the Repository:**

```bash
git clone https://github.com/lysvallee/npair.git
```


**2. Build Docker Images (Optional):**

You can build the Docker images for each component manually:

```bash
cd data/api
docker build -t data_api .

cd ../model/api
docker build -t model_api .

# ... Repeat for other services (user_api, tests, etc.)
```

**3. Run the Application (Development or Production Mode):**

Navigate to the root directory:

```bash
cd npair
```

Use Docker Compose to build the images (if necessary) and start the application in your desired mode:

```bash
docker-compose -f docker-compose.dev.yml up --build
or
docker-compose -f docker-compose.prod.yml up --build
or
docker-compose -f docker-compose.track.yml up --build
```

This will build the required images and bring up the concerned services. You can access the APIs at the following default ports:

* Data API: http://localhost:8000 (modify port if needed in the Docker Compose yml)
* Model API: http://localhost:8001
* User API: http://localhost:8002


## API Usage

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

## Monitoring

The user API is integrated with Grafana for monitoring. Please refer to the `user/monitoring` folder for configuration details.

## Model Tracking

To run experiments, set the hyperparameters with tracking_api.py, use docker-compose.track.yml, then start the process with:
```bash
curl -X POST http://localhost:5000/run_experiments
```
Logs are stored in logs/model_api_track.log.
The resulting metrics are also available in the model_metrics table of the database.


Full file structure:

```
├── data
│   ├── api
│   │   ├── clear_databases.py
│   │   ├── data_api.py
│   │   ├── data_collection.md
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
│       └── test_data
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── docker-compose.track.yml
├── grafana
│   ├── data
│   │   ├── csv
│   │   ├── grafana.db
│   │   ├── pdf
│   │   ├── plugins
│   │   └── png
│   ├── monitoring.md
│   └── provisioning
│       ├── alerting
│       ├── dashboards
│       ├── datasources
│       └── plugins
├── logs
│   ├── clear_databases.log
│   ├── create_movies_db.log
│   ├── create_shows_db.log
│   ├── data_api.log
│   ├── extract_movie_palettes.log
│   ├── model_api.log
│   ├── model_api_track.log
│   ├── tracking_api.log
│   └── user_api.log
├── model
│   ├── api
│   │   ├── Dockerfile.cpu
│   │   ├── Dockerfile.gpu
│   │   ├── logs
│   │   ├── model_api.py
│   │   ├── model_api_track.py
│   │   ├── model_configuration.md
│   │   ├── model_integration.md
│   │   ├── models.py
│   │   ├── pip_cache
│   │   ├── __pycache__
│   │   ├── pytest.ini
│   │   ├── requirements.txt
│   │   ├── services.py
│   │   ├── test_model_api.md
│   │   ├── test_model_api.py
│   │   ├── triposr
│   │   ├── unit_tests.md
│   │   └── unit_tests.py
│   ├── huggingface
│   │   └── hub
│   ├── tracking
│   │   ├── Dockerfile
│   │   ├── model_metrics1.csv
│   │   ├── model_metrics2.csv
│   │   ├── models.py
│   │   ├── pip_cache
│   │   ├── requirements.txt
│   │   ├── services.py
│   │   └── tracking_api.py
│   └── u2net
│       └── u2net.onnx
├── README.md
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
        ├── test_user_api.md
        ├── test_user_api.py
        └── user_api.py
```

## Attributions
- TripoSR Model: [VAST-AI-Research/TripoSR](https://github.com/VAST-AI-Research/TripoSR)
- Image Source: [Pixabay API](https://pixabay.com/service/about/api/)
