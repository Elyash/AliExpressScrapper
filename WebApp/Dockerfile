# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    git \
    vim \
    --no-install-recommends

# Install Selenium and ipython
RUN pip install \
    pymongo \
    pika \
    ipython \
    flask \
    Flask-SQLAlchemy \
    flask-login

# Set up the working directory
WORKDIR /app

# Copy the app code to container
COPY ${HOME}/MyFullstackScrapper /app/

# Default command
# TODO: run flask app
CMD ["python", "./scrapper.py"]
