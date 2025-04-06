# AI/ML Data Engineer Take-Home Assignment

## Overview
This repository contains a solution for an AI/ML Data Engineer role assignment, aimed at building a data ingestion pipeline for processing investor relations documents (PDFs and PPTs). The objective is to fetch, parse, and transform unstructured data into semantic chunks suitable for a Retrieval-Augmented Generation (RAG) system.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Pipeline Overview](#pipeline-overview)
---

## Project Structure
app/ 

 ├── pipeline.py # Main script for the data ingestion pipeline 
 ├── requirements.txt 
 Python dependencies 
    ├── Dockerfile # Docker configuration for building the container 
    ├── output/ # Directory for processed JSONL files 
    ├── DOCUMENTATION.md # Project documentation 
    ├── README.md # Project instructions and details 
    ├── .gitignore # Files to ignore in GitHub commits


---

## Setup Instructions

### Prerequisites
Ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package manager)
- Docker (for containerized setup)

### Installation
1. Clone this repository:

```bash
git clone https://github.com/nawawy/midas_task.git
```
2. Create a virtual environment (optional, but recommended):

```bash

python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Docker (optional)
If you prefer to run the application in a Docker container, follow these steps:

Build the Docker image:
```bash
docker build -t midas_task .
```
Run the Docker container:
```bash
docker run -it midas_task
```

### Usage
#### Running the Pipeline
Run the script:
```bash
python pipeline.py "https:/example.com/documents/file.pdf"
```
The processed chunks will be saved as a JSONL file in the output/ directory.

### Pipeline Overview
#### The pipeline performs the following steps:

1. Fetch Documents: Downloads PDFs or PPTs from provided URLs.

2. Parse Data: Extracts text, tables, and metadata from the documents.

3. Classify Documents: Categorizes each document into predefined categories (e.g., Financial Reports, Investor Presentations).

4. Chunk Data: Divides the extracted text into smaller, semantically meaningful chunks.

5. Save Output: Stores the chunks in a JSONL file for further processing.

6. Embeddings: Optionally stores the chunks in ChromaDB for efficient retrieval.
