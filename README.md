# Midas AI AI/ML Data Engineer Take-Home Assignment

## Overview
This repository contains a solution for an AI/ML Data Engineer role assignment, aimed at building a data ingestion pipeline for processing investor relations documents (PDFs and PPTs). The objective is to fetch, parse, and transform unstructured data into semantic chunks suitable for a Retrieval-Augmented Generation (RAG) system.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Pipeline Overview](#pipeline-overview)
- [Documetation](#documentation)

---

## Project Structure
```
📦 
├─ .gitignore
├─ .vscode
│  └─ launch.json
├─ Documentation.md
├─ README.md
├─ dockerfile
├─ downloads
│  ├─ 10Q-Q1-2025-as-filed.pdf
│  ├─ FY25_Q1_Consolidated_Financial_Statements.pdf
│  ├─ SlidesFY25Q2
│  ├─ TSLA-Q4-2024-Update.pdf
│  └─ _10-K-2021-(As-Filed).pdf
├─ output
│  ├─ 5233be31-4868-44a4-b08a-b17a42c67582.jsonl
│  ├─ 5f19a0b1-21d3-4cbd-8616-3a1590fd97c2.jsonl
│  └─ 879955c3-4a2d-44ff-a3c8-12e8bbe38f46.jsonl
├─ pipeline.py
└─ requirements.txt
```
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
#### Choose Your Setup Method:
You can use either a virtual environment or Docker.

Option 1: Virtual Environment
  
            * Create a virtual environment (optional, but recommended):
                        
              cd midas_task
              python3 -m venv venv
              source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
            
            
            * Install dependencies:
            
              pip install -r requirements.txt
            
Option 2: Docker

        * Build the Docker image:

              cd midas_task
              docker build -t midas .
---

### Usage
#### Running the Pipeline
##### Option 1: Using Python

  Run the script:
  ```bash

  Put your openai API key in classifier.py line 4
    openai.api_key = "your-openai-api-key"

  python pipeline.py "https:/example.com/documents/file.pdf"
  ```
  The processed chunks will be saved as a JSONL file in the output/ directory.

  
##### Option 2: Using Docker

  ```bash
    Put your openai API key in classifier.py line 4
      openai.api_key = "your-openai-api-key"

    docker run --name my_midas -v $(pwd)/output:/app/output midas python pipeline.py "https://conferences.infotoday.com/documents/451/C204_Hedden.pdf"
  ```
<br>

  Command Details:<br>
    
    "--name my_midas": Names the container for reuse.<br>
    "-v $(pwd)/output:/app/output": Maps the container's output directory to your local output/ folder.<br>
    "midas": The name of the Docker image.<br>
    "https://www.example.com/example.pdf": The URL of the document to process.<br>

  ```bash
  docker start -a my_midas
  ```
  To run the same container again, if you want to check the avoiding processing existing files feature

---

### Pipeline Overview
#### The pipeline performs the following steps:

1. Fetch Documents: Downloads PDFs or PPTs from provided URLs.

2. Parse Data: Extracts text, tables, and metadata from the documents.

3. Classify Documents: Categorizes each document into predefined categories (e.g., Financial Reports, Investor Presentations).

4. Chunk Data: Divides the extracted text into smaller, semantically meaningful chunks.

5. Save Output: Stores the chunks in a JSONL file for further processing.

6. Embeddings: Optionally stores the chunks in ChromaDB for efficient retrieval.

---

### Documentation
#### You can find a file named Documentation.md that contains all of the code documentation and explaination
