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


# Set the project name
ARG PROJECT="MyFullstackProject"
ARG PACKAGE="WebApp"

# Set up the working directory
WORKDIR /app/${PROJECT}

# Install python requirements
COPY ${PACKAGE}/requirements.txt .
RUN pip install -r requirements.txt
RUN rm -rf requirements.txt

# TODO: This dockerfile is for development.
#       In the future we'll add deployment version so the code will be locally on the container.