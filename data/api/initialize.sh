#!/bin/bash

# Uncomment to start afresh
rm -rf /data/storage/images/*

# Check if the images folder is empty before initialising the data collection
if [ -z "$(ls -A /data/storage/images )" ]; then
    echo -e "\e[32mCreating all the databases...\e[0m"
    python initial_setup.py
else
    echo -e "\e[33mData already exists, skipping initial setup.\e[0m"
fi

# Start the API
uvicorn data_api:app --host 0.0.0.0 --port 8000 
