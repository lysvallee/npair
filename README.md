## 3D Generation App with TripoSR Model

This project provides a web application for generating 3D objects from input images using the TripoSR model ([https://github.com/VAST-AI-Research/TripoSR](https://github.com/VAST-AI-Research/TripoSR)). It leverages FastAPI for building APIs and Docker for containerization.

### Project Overview

The application consists of three main components:

1. **Data API (data_api):** Serves images and tabular data (color palettes, PBR materials) from a PostgreSQL database.
2. **Model API (model_api):** Runs the TripoSR model to generate 3D objects from images received through the API.
3. **User API (user_api):** Receives user input (image data), interacts with the data and model APIs, and provides the generated 3D object to the frontend.

The application can be deployed in production and testing environments using Docker Compose. Monitoring for the user API is also integrated with Prometheus and Grafana.

### Setting Up the Project

**Prerequisites:**

* Docker: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)
* Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
* Python 3.x

**1. Clone the Repository:**

```bash
git clone https://your-repository-url.git
```

**2. Install Dependencies:**

Navigate to the project directory and install dependencies using pip:

```bash
cd 3d-generation-app
pip install -r requirements.txt
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

**4. Run the Application (Development Mode):**

Use Docker Compose to start the application in development mode:

```bash
docker-compose up -d
```

This will bring up all services in detached mode. You can access the APIs at the following default ports:

* Data API: http://localhost:8000 (modify port if needed in docker-compose.yml)
* Model API: http://localhost:8001 (modify port if needed in docker-compose.yml)
* User API: http://localhost:8002 (modify port if needed in docker-compose.yml)

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

* Users can send an image through a POST request to a specific endpoint.
* The User API retrieves additional data (color palettes, materials) from the Data API.
* It then calls the Model API with the image and retrieved data.
* Finally, the User API receives the generated 3D object and returns it to the user.

Refer to `user/api/user_api.py` for specific endpoint details and usage instructions.

**Note:** This is a general overview. Specific API endpoints, request/response formats, and authentication mechanisms might require further exploration within the relevant API code files.

### Monitoring

The user API is integrated with Prometheus and Grafana for monitoring. Refer to the `user/monitoring` folder for configuration details.


Full file structure:

├── data
│   ├── api
│   │   ├── data_api.py
│   │   ├── Dockerfile
│   │   ├── models.py
│   │   ├── requirements.txt
│   │   └── services.py
│   ├── init
│   │   ├── Dockerfile
│   │   └── init.sql
│   └── storage
│       └── young_boy.png
├── docker-compose-prod.yml
├── docker-compose-test.yml
├── model
│   ├── api
│   │   ├── Dockerfile
│   │   ├── model_api.py
│   │   └── requirements.txt
│   ├── tracking
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── triposr
│       ├── examples
│       ├── figures
│       ├── gradio_app.py
│       ├── LICENSE
│       ├── README.md
│       ├── run.py
│       └── tsr
├── README.md
├── tests
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── test_data_api.py
│   ├── test_model.py
│   └── test_user_api.py
└── user
    ├── api
    │   ├── Dockerfile
    │   ├── favicon.ico
    │   ├── requirements.txt
    │   ├── services.py
    │   ├── static
    │   ├── td.py
    │   ├── templates
    │   └── user_api.py
    └── monitoring
        ├── grafana
        └── prometeus
