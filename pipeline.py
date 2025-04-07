# Predefined categories 
CATEGORIES = {
    "Financial Reports": ["annual report", "quarterly report", "earnings"],
    "Investor Presentations": ["presentation", "conference", "slides"],
    "Corporate Governance Documents": ["policy", "charter", "governance"],
    "Press Releases": ["announcement", "merger", "leadership"],
    "Stock Market Information": ["stock price", "dividend", "shareholder"],
    "Corporate Social Responsibility (CSR) Reports": ["sustainability", "ESG", "community"]
}

# Import necessary libraries
import os
import requests
import re
import sys
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from typing import List, Dict, Optional, Union

from unstructured.partition.pdf import partition_pdf
from unstructured.partition.ppt import partition_ppt
from unstructured.partition.pptx import partition_pptx

from langchain.text_splitter import NLTKTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.globals import set_verbose, set_debug


import json
import uuid
from collections import defaultdict
import shutil
import hashlib

import nltk

# Download necessary NLTK data files
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

# Set up logging and verbosity
set_verbose(False)
set_debug(False)

# Remove existing ChromaDB directory if it exists to avoid conflicts
# shutil.rmtree("chroma_db", ignore_errors=True)

# Set the cache file name
CACHE_FILE = "processed_files.json"

# Helper function to download files from URLs and save them to a specified directory
@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))  # Retry 5 times with 2 seconds wait
def download_file(url: str, save_dir: str = "downloads") -> str: 
    # Make sure the directory exists
    os.makedirs(save_dir, exist_ok=True)
    # Extract the filename from the URL and create the full path
    filename = os.path.join(save_dir, url.split("/")[-1])
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded: {filename}")
        return filename
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")
        raise e  # Raise the exception to trigger retry

# Helper function to extract text from PDF files
def parse_data(file_path: str, url_source: Optional[str] = None, type_file: Optional[str] = None) -> Optional[List[Dict[str, Union[int, str]]]]:
    text_data = []
    
    if type_file == "pptx":
        elements = partition_pptx(filename=file_path)
    elif type_file == "ppt":
        elements = partition_ppt(filename=file_path)
    elif type_file == "pdf":
        elements = partition_pdf(filename=file_path)
    else:
        print("Unsupported file type")
        return None
    
    # Combining full text for classification 
    full_text = "\n".join([str(el) for el in elements])
    category = classify_document(full_text)
    
    # Divide text accordig to page number
    pages = defaultdict(list)
  
    for element in elements:
        page_num = element.metadata.page_number
        if hasattr(element, "metadata") and page_num is not None:
            if page_num not in pages:
                pages[page_num] = element.text
            else:
                pages[page_num] += " " + element.text  # Add space between chunks
    
    for page_num, text in pages.items():
        # Detecting whether text is table or simple text
        text_type = "table" if detect_table_pattern(text) else "text"
        # Creatig text data for chunking
        text_data.append({"page_num": page_num, "content": text, "category": category, "text_type": text_type ,"url": url_source, "doc_type": type_file})

    return text_data

# Helper function to clean text by removing extra spaces and newlines
def clean_text(text: str) -> str:
    # Normalize multiple newlines and spaces
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    return text

# Helper function to mark sections in the text
def mark_sections(text: str) -> str:
    # Insert double newlines before all-caps or heading-like lines
    text = re.sub(r"(?<!\n)\n(?=[A-Z][^\n]{2,50}\n)", r"\n\n", text)
    return text

# Helper function to chunk text into smaller segments
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    splitter = NLTKTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap, separator="\n\n")
    clean_text_out = mark_sections(text)
    clean_text_out = clean_text(clean_text_out)
    return splitter.split_text(clean_text_out)

# Helper function to save data to a JSONL file
def save_to_json(data: List[Dict], output_file: str = "output/output.json") -> None:
    os.makedirs("output", exist_ok=True)
    with open(output_file, "w") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")

# Helper function to detect table-like patterns in text
def detect_table_pattern(text : str) -> bool:
    # Split the text into lines
    lines = text.strip().split("\n")

    table_line_count = 0
    columns_count = None

    for line in lines:
        # Split by pipe `|`, strip spaces to avoid leading/trailing whitespaces
        parts = [part.strip() for part in line.split("|")]

        # Condition 1: Check for a significant number of columns
        if len(parts) >= 2:
            # Check if there's at least one numeric value (indicating structured data)
            has_numbers = any(re.search(r'\d+', part) for part in parts)
            
            # Skip lines that don't have numeric data or don't look like they belong in a table
            if not has_numbers:
                continue
            
            # Condition 2: Check column consistency
            if columns_count is None:
                columns_count = len(parts)
            elif len(parts) != columns_count:
                # If the number of columns changes from line to line, it's not a table
                return False
            
            table_line_count += 1
    
    # If there are more than 50% table-like lines with consistent columns, classify as a table
    if table_line_count / len(lines) > 0.5:
        return True
    
    return False

# Helper function to load cache from a JSON file
def load_cache() -> Dict[str, Dict]:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

# Helper fuction to hash URLs
def hash_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()

# Helper function to save cache to a JSON file
def save_cache(cache : Dict[str, Dict]) -> None:
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def fetch_documents(urls : List[str]) -> List[tuple[str, str]]:
    files = []
    cache = load_cache()

    # Implement HTTP client with retry logic
    for url in urls:
        try:
            # Generate a hash for the URL to use as a cache key
            url_hash = hash_url(url)
            if url_hash in cache:
                print(f"Skipping already processed file: {url}")
                continue
            file_path = download_file(url)
        except RetryError:
            print("Failed to download the file after several attempts.")
        
        if file_path:
            cache[url_hash] = {
                "url": url,
                "file_path": file_path,
                "parsed": False
            }
            files.append((file_path, url))

    # Save the cache after processing all URLs
    save_cache(cache)

    return files

def classify_document(text : str) -> str:
    # Rule-based classification using keyword matching
    for category, keywords in CATEGORIES.items():
        if any(keyword.lower() in text.lower() for keyword in keywords):
            return category
    return "Unknown"

# Determine the file type based on extension
def get_doc_type(file_path: str) -> Optional[str]:
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext == ".pdf":
        doc_type = "pdf" 
    elif ext == ".ppt":
        doc_type = "ppt"
    elif ext == ".pptx":
        doc_type = "pptx"
    else:
        doc_type = None
    
    if doc_type is None:
        print(f"Unsupported file type: {ext}")
        return None
    
    return doc_type

def process_file(file_path: str, url_source: str) -> Optional[List[Dict[str, Union[int, str]]]]:
    
    url_hash = hash_url(url_source)
    cache = load_cache()
    
    # Check if the file is already parsed
    if cache.get(url_hash, {}).get("parsed"):
        print(f"Skipping already parsed file from URL: {url_source}")
        return None
        
    doc_type = get_doc_type(file_path)
    extracted_data = parse_data(file_path, url_source, type_file=doc_type)

    cache[url_hash] = {
        "url": url_source,
        "file_path": file_path,
        "parsed": True
    }

    save_cache(cache)
    return extracted_data
    
def chunk_data(elements: List[Dict[str, Union[int, str]]]) -> Optional[List[Dict[str, Union[str, int]]]]:
    # Implement semantic chunking logic
    final_data = []

    for entry in elements:
        
        if entry is None:
            continue

        for item in entry:
            chunks = chunk_text(item["content"])

            for chunk in chunks:
                final_data.append({
                    "chunk_id": str(uuid.uuid4()),
                    "content": chunk,
                    "metadata": {
                        "source": item["url"],
                        "page_num": item["page_num"],
                        "doc_type": item["doc_type"],
                        "content_type": item["text_type"],
                        "category": item["category"]
                    }
                })
    
    return final_data

def main(args=None):

    urls = [
       "https://view.officeapps.live.com/op/view.aspx?src=https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/SlidesFY25Q2",
       "https://digitalassets.tesla.com/tesla-contents/image/upload/IR/TSLA-Q4-2024-Update.pdf",
       "https://s2.q4cdn.com/470004039/files/doc_earnings/2025/q1/filing/10Q-Q1-2025-as-filed.pdf",
       "https://www.apple.com/newsroom/pdfs/fy2025-q1/FY25_Q1_Consolidated_Financial_Statements.pdf",
       "https://s2.q4cdn.com/470004039/files/doc_financials/2021/q4/_10-K-2021-(As-Filed).pdf",
       "https://www.apple.com/newsroom/pdfs/fy2024-q1/FY24_Q1_Consolidated_Financial_Statements.pdf",
       "https://conferences.infotoday.com/documents/451/0930_Jain.pptx",
       "https://conferences.infotoday.com/documents/451/B105_Steinkamp.pptx",
       "https://conferences.infotoday.com/documents/451/AI105_Oad.pptx",
    ]

    urls += args
    if not urls:
        print("No URLs provided. Please provide URLs as command line arguments.")
        return
    
    # Fetch and download documents
    raw_files = fetch_documents(urls)

    # Process each file ad parse text
    processed_data = [process_file(f[0],f[1]) for f in raw_files] # f[0] = file_path, f[1] = url

    # Chunk the processed data
    chunks = chunk_data(processed_data)

    if chunks is None or not chunks:
        print("No data to process.")
        return
    
    # Write data to a JSONL file
    out_json_file = "output/" + str(uuid.uuid4()) + ".jsonl"
    save_to_json(chunks, out_json_file)
    print("Data processing complete. Chunks saved to JSONL file.")
    
    # Save final chunks to a database or file system (output)
    documents = [Document(page_content=chunk['content'], metadata=chunk['metadata']) for chunk in chunks]
    
    # Initialize embeddings 
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")  # or OpenAIEmbeddings()

    # Create ChromaDB from the documents
    db = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory="chroma_db"
    )

    print("Data processing and storage complete.")

if __name__ == "__main__":
    main(sys.argv[1:])
