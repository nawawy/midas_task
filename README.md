# AI/ML Data Engineer Take-Home Assignment

This repository contains a take-home assignment for an AI/ML Data Engineer role. The task involves building a data ingestion pipeline to fetch, parse, and process unstructured data (PDFs and PPTs) from investor relations websites. The processed data will be transformed into semantic chunks with metadata, suitable for use in a Retrieval-Augmented Generation (RAG) system.

---

## 📋 Assignment Overview

### Objective

The goal is to:

1. **Fetch** investor relations documents (PDFs/PPTs/..) from the web.
2. **Classify** each document into one of the predefined categories.
3. **Parse** and extract relevant content (text, tables, etc.).
4. **Chunk** the extracted content into smaller pieces with metadata.
5. **Output** the processed data in JSONL format.

### Key Features

- Extract unstructured data from PDF and PPT files.
- Classify documents into categories using rule-based or machine learning approaches.
- Perform semantic chunking with token limits.
- Include metadata such as source URL, document type, page numbers, etc.
- Optionally store the chunks in a vector database like ChromaDB.

---

## 🛠️ Getting Started

Follow these instructions to set up the project and run the pipeline.

### Prerequisites

Make sure you have the following installed:

- Python 3.8 or higher
- `pip` (Python package manager)

### Installation

1. Clone this repository:


2. Create a virtual environment (optional):
   python3 -m venv venv
   source venv/bin/activate # On Windows (Command Prompt): venv\Scripts\activate or (PowerShell): .\venv\Scripts\Activate.ps1

3. Install dependencies:
   pip install -r requirements.txt

---

## 🚀 Usage

### Running the Pipeline

1. Open `pipeline.py` and locate the `urls` list inside the `main()` function. For example:

   ```python
   urls = [
       "https://example.com/investor-report.pdf",
       "https://example.com/presentation.ppt"
   ]
   ```

2. Implement and run the script:
```
python pipeline.py
```
3. The processed chunks will be saved as a JSONL file in the `output/` directory.

---

## 📂 Project Structure

ai-ml-data-engineer-assignment/
│
├── pipeline.py # Main script for the data ingestion pipeline
├── requirements.txt # Python dependencies
├── output/ # Directory for processed JSONL files
├── README.md # Project instructions and details
└── .gitignore # Files to ignore in GitHub commits

---

## 📝 Output Format

The pipeline generates a JSONL file with the following schema:

```
{
  "chunk_id": "uuid4",
  "content": "extracted text",
  "metadata": {
    "source": "url",
    "page_num": int,
    "doc_type": "pdf/ppt",
    "content_type": "text/table",
    "category": "Category"
  }
}
```
Example entry:
```
{
  "chunk_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "This is an example chunk of text.",
  "metadata": {
    "source": "https://example.com/investor-presentation.pdf",
    "page_num": 5,
    "doc_type": "pdf",
    "content_type": "text",
    "category": "Investor Presentations"
  }
}
```
---

## ✅ Evaluation Criteria

Your submission will be evaluated based on:

1. **Code Quality** (40%)

   - Modular design with clear functions.
   - Error handling for network and parsing failures.
   - Use of type hints and comments.

2. **Functionality** (40%)

   - Accurate PDF/PPT parsing and classification.
   - Effective semantic chunking strategy.
   - Metadata completeness.

3. **Documentation** (20%)
   - Clear setup instructions.
   - Explanation of design decisions.
   - Suggestions for future improvements.

---

## 🌟 Bonus Points

You can earn bonus points by implementing any of the following:

- Dockerizing the pipeline for easy deployment.
- Adding unit tests to validate functionality.
- Implementing incremental processing to avoid re-parsing existing files.

---

## 📖 Resources

Here are some libraries and tools you may find helpful:

- [Unstructured.io](https://github.com/Unstructured-IO/unstructured) for parsing PDFs and PPTs.
- [LangChain](https://langchain.readthedocs.io/) for text splitting and embeddings.
- [ChromaDB](https://www.trychroma.com/) for storing vectorized chunks.

---

## 📨 Submission Instructions

1. Push your code to a public GitHub repository or send us a zip file.
2. Include sample output (`output.jsonl`) in your submission by placing it in the `output/` directory.
3. Add a brief explanation of your approach in a DOCUMENTATION.md file.

Good luck! 🚀
