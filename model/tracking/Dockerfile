# Use the official Python image from the Docker Hub
FROM python:3.9

# Install git and C++ compiler for torchmcubes.git
RUN apt-get update && apt-get install -y git g++

# Install torch and its dependencies
RUN pip3 install --no-cache-dir torch torchvision torchaudio

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies
RUN pip install mlflow

EXPOSE 5000

CMD ["mlflow", "server", "--host", "0.0.0.0"]
