# Model Integration Documentation

This document describes how the 3D model generation is integrated into our web application through the `model_api.py` file.

## Overview

The `model_api.py` file sets up a FastAPI application that provides an endpoint for generating 3D models from images. It includes authentication, input validation, model execution, and file management.

## Key Components

### 1. FastAPI Setup and Authentication

```python
app = FastAPI()

API_KEY = os.getenv("API_KEY")

@app.middleware("http")
async def validate_api_key(request: Request, call_next):
    if request.headers.get("Authorization") != f"Bearer {API_KEY}":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return await call_next(request)
```

- The FastAPI application is initialized.
- An API key is retrieved from environment variables.
- A middleware function is set up to validate the API key for all incoming requests.

### 2. Directory Configuration

```python
OBJECTS_DIR = "/data/storage/objects"
RENDERS_DIR = "/data/storage/renders"
```

- Directories for storing 3D objects and 2D renders are defined.

### 3. Model Generation Endpoint

```python
@app.post("/generate")
async def generate_3d_model(model_parameters: dict):
    # ... (implementation details below)
```

- A POST endpoint `/generate` is defined to handle 3D model generation requests.

### 4. Input Validation

```python
if "image_path" not in model_parameters:
    raise HTTPException(status_code=422, detail="image_path is required")
image_path = model_parameters["image_path"]
if not image_path:
    raise HTTPException(status_code=422, detail="Image path cannot be empty")
if not os.path.exists(image_path):
    raise HTTPException(status_code=404, detail="Image not found")
```

- The function checks if the `image_path` is provided, not empty, and exists.

### 5. Model Execution

```python
result = subprocess.run(
    [
        "python3",
        "/app/triposr/run.py",
        image_path,
        "--model-save-format", "glb",
        "--render",
        "--chunk-size", chunk_size,
        "--mc-resolution", mc_resolution,
        "--output-dir", OBJECTS_DIR,
    ],
    check=True,
    capture_output=True,
    text=True,
)
```

- The 3D model generation script is executed as a subprocess.
- Various parameters are passed to the script, including the image path, output format, and rendering options.

### 6. Output Processing

```python
generated_object = os.path.join(OBJECTS_DIR, "mesh.glb")
if not os.path.exists(generated_object):
    raise HTTPException(status_code=500, detail="Model generation did not produce expected output files")

render_gif = os.path.join(OBJECTS_DIR, "render.gif")

base_name = os.path.basename(image_path)
base_name = os.path.splitext(base_name)[0]
object_3d_name = f"{base_name}.glb"
object_2d_name = f"{base_name}.gif"
object_3d_path = os.path.join(OBJECTS_DIR, object_3d_name)
object_2d_path = os.path.join(RENDERS_DIR, object_2d_name)
```

- The function checks if the expected output files were generated.
- Unique names are created for the 3D object and 2D render based on the input image name.

### 7. File Management

```python
shutil.move(generated_object, object_3d_path)
shutil.move(render_gif, object_2d_path)
png_files = glob(os.path.join(OBJECTS_DIR, "*.png"))
for png_file in png_files:
    os.remove(png_file)
```

- The generated 3D object and 2D render are moved to their respective directories.
- Any intermediate PNG files are removed.

### 8. Response

```python
model_data = {"object_3d": object_3d_path, "object_2d": object_2d_path}
return model_data
```

- The function returns a dictionary containing the paths to the generated 3D object and 2D render.

## Usage

To use this API:

1. Ensure the API key is set in the environment.
2. Send a POST request to the `/generate` endpoint with the following:
   - Headers: `Authorization: Bearer <API_KEY>`
   - JSON body: `{"image_path": "<path_to_image>"}`
3. The API will return the paths to the generated 3D object and 2D render.

## Error Handling

The API includes error handling for:
- Invalid API keys
- Missing or invalid image paths
- Failed model generation

Each error case will return an appropriate HTTP status code and error message.
```
