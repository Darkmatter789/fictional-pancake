# Use the official Python image as the base image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container and install the dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Expose port 5000
EXPOSE 5000

# Start the Flask application
CMD ["python", "main.py"]
