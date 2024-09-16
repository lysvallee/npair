# 3D Generation Model Performance Tracking API

This document describes the API for tracking the performance of our 3D generation model.

## Overview

The tracking API is implemented in `tracking_api.py`. It provides functionality to run experiments with various parameters and log the model metrics for each experiment. The API uses FastAPI for handling HTTP requests.

## API Endpoints

### POST /run_experiments

This endpoint initiates a series of experiments with different parameters for the 3D generation model.

#### Process

1. The API selects images from three categories: bicycle, car, and plane.
2. For each image, it runs experiments with different combinations of chunk sizes and marching cubes resolutions.
3. The model is called for each combination, and the results are logged.
4. The generated 3D objects and renders are saved with unique names.

#### Parameters

The experiments use the following parameter sets:

- Categories: ["bicycle", "car", "plane"]
- Chunk sizes: [8192, 12288, 14336]
- Marching cubes resolutions: [16, 128, 256]

#### Response

- Success: `{"status": "success", "message": "Experiments completed"}`
- Failure: HTTP 500 error with details of the failure

## Model Metrics Logging

The `log_model_metrics` function is used to log the metrics for each experiment. It takes the following parameters:

- `db`: Database session
- `object_name`: Name of the 3D object
- `chunk_size`: Chunk size used in the experiment
- `mc_resolution`: Marching cubes resolution used in the experiment
- Other metrics returned by the model API

## Model API Integration

The API communicates with the 3D generation model API at `http://model_api_track:8001/generate`. The `run_experiment` function handles this communication, sending the following parameters:

- `image_name`: Name of the input image
- `chunk_size`: Chunk size for the experiment
- `mc_resolution`: Marching cubes resolution for the experiment

## File Management

The API manages the following directories:

- `/data/storage/objects`: For storing generated 3D objects (.glb files)
- `/data/storage/renders`: For storing rendered 2D representations (.gif files)

Generated files are moved to these directories with unique names based on the object name, chunk size, and marching cubes resolution.

## Error Handling

The API includes error handling for various scenarios:

- HTTP errors when communicating with the model API
- Failures in model generation
- Missing output files
- Unexpected exceptions during the experiment process

All errors are logged and result in appropriate HTTP responses.

## Logging

The API uses a logger to record information about the experiment process, including:

- Start of each experiment with its parameters
- Successful completion of experiments
- Any errors or exceptions that occur during the process
