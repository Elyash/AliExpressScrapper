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

# Set Google Chrome and Google Chrome driver versions. they must be in compatible versions
ARG CHROME_DRIVER_VERSION="114.0.5735.90"
ARG CHROME_VERSION="114.0.5735.90-1"

# Download and install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    wget -O /tmp/google-chrome-stable_${CHROME_VERSION}.deb https://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb && \
    cd /tmp && \
    apt-get install -y --allow-downgrades ./google-chrome-stable_${CHROME_VERSION}.deb --no-install-recommends && \
    cd - && \
    rm -rf /var/lib/apt/lists/*

# Download and install ChromeDriver
RUN wget -O /tmp/chromedriver_linux64.zip https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

# Install Selenium and ipython
RUN pip install selenium webdriver-manager pymongo ipython

# Set up the working directory
WORKDIR /app

# Set environment variable to disable Chrome sandbox (needed when running in Docker)
ENV CHROME_DRIVER_PATH=/usr/local/bin/chromedriver
ENV DISPLAY=:99

# Copy the scrapper code to container
COPY scrapper.py /app/

# Default command
CMD ["python", "./scrapper.py"]
