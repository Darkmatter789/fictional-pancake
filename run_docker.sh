#!/bin/bash

# Build the Docker image
docker build -t rca-site .

# Run the Docker container
docker run -p 5000:5000 rca-site
