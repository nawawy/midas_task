# Use the official Python image as the base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt (make sure you have this file with all dependencies listed)
COPY requirements.txt /app/

# Install system dependencies for libraries such as requests, unstructured, etc.
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libgl1-mesa-glx \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Install the Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install additional Python packages if needed
RUN pip install --upgrade transformers accelerate

# Copy the entire application code to the working directory in the container
COPY . /app/

# Set the command to run your application, change the file path if needed
CMD ["python", "pipeline.py"]
