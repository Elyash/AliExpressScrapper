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

# Set up the working directory
WORKDIR /app/

CMD [ "python", "-c", "import time; time.sleep(10000)"]
