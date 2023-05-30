@echo off

rem Build the Docker image
docker build -t rca-site .

rem Run the Docker container
docker run -p 5000:5000 rca-site
