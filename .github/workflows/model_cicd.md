# Model CI/CD Workflow Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) workflow for the model, as defined in the `docker-publish-model.yml` GitHub Actions workflow file.

## Workflow Overview

The workflow is designed to build, test, and push a Docker image for the model API to the GitHub Container Registry (GHCR). It is triggered on pushes to the `main` branch or can be manually dispatched.

## Workflow Steps

### 1. Trigger Events

The workflow is triggered by:
- Pushes to the `main` branch
- Manual dispatch (workflow_dispatch)

```yaml
on:
  push:
    branches:
      - main
  workflow_dispatch:
```

### 2. Job: build-and-push

This job runs on the latest Ubuntu runner and consists of several steps:

#### 2.1 Checkout code

```yaml
- name: Checkout code
  uses: actions/checkout@v2
```
This step checks out the repository code, making it available for the subsequent steps.

#### 2.2 Set up Docker Buildx

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v2
```
This step sets up Docker Buildx, which is used for building and pushing multi-platform Docker images.

#### 2.3 Log in to GitHub Container Registry

```yaml
- name: Log in to GitHub Container Registry
  uses: docker/login-action@v2
  with:
    registry: ghcr.io
    username: ${{ secrets.GHCR_USERNAME }}
    password: ${{ secrets.GHCR_TOKEN }}
```
This step authenticates with the GitHub Container Registry using the provided secrets.

#### 2.4 Build and push npair_model_api image

```yaml
- name: Build and push npair_model_api image
  uses: docker/build-push-action@v3
  with:
    push: true
    tags: ghcr.io/${{ secrets.GHCR_USERNAME }}/npair_model_api:cpu
    context: ./model/api
    file: ./model/api/Dockerfile.cpu
```
This step builds the Docker image for the model API using the specified Dockerfile and pushes it to GHCR with the tag `cpu`.

#### 2.5 Install Docker Compose

```yaml
- name: Install Docker Compose
  run: |
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
```
This step installs Docker Compose, which is needed for running the tests.

#### 2.6 Run model API tests

```yaml
- name: Run model API tests with docker-compose
  run: docker-compose -f docker-compose.prod.yml run --rm model_api pytest test_model_api.py
```
This step runs the model API tests using Docker Compose and pytest.

## Workflow Execution

1. When triggered, the workflow checks out the code and sets up the Docker build environment.
2. It then logs in to the GitHub Container Registry using the provided credentials.
3. The Docker image for the model API is built and pushed to GHCR.
4. Docker Compose is installed on the runner.
5. Finally, the model API tests are run using Docker Compose and pytest.

## Security Considerations

- The workflow uses secrets (`GHCR_USERNAME` and `GHCR_TOKEN`) for authentication with GHCR. These should be securely stored in the repository's secrets.

## Maintenance and Troubleshooting

- Ensure that the `GHCR_USERNAME` and `GHCR_TOKEN` secrets are up-to-date and have the necessary permissions.
- If the tests fail, check the Docker Compose configuration and the test files.
- Keep the Docker Compose version updated in the installation step.

This CI/CD workflow ensures that the model API is automatically built, tested, and deployed whenever changes are pushed to the main branch, maintaining code quality and streamlining the deployment process.
