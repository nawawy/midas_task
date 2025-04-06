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
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError

from unstructured.partition.pdf import partition_pdf
from unstructured.partition.ppt import partition_ppt
from unstructured.partition.pptx import partition_pptx

from langchain.text_splitter import NLTKTextSplitter
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

import json
import uuid
from collections import defaultdict
import shutil
shutil.rmtree("chroma_db", ignore_errors=True)

import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

# Helper function to download files from URLs and save them to a specified directory
@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))  # Retry 5 times with 2 seconds wait
def download_file(url, save_dir="downloads"):
    
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
        return None

# Helper function to extract text from PDF files
def parse_pdf(file_path, url_source=None):
    text_data = []
    
    elements = partition_pdf(filename=file_path)
    
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
        text_type = "table" if detect_table_pattern(text) else "text"
        text_data.append({"page_num": page_num, "content": text, "category": category, "text_type": text_type ,"url": url_source, "doc_type": "pdf"})

    return text_data

# Helper function to extract text from PPTX files using python-pptx
def parse_ppt(file_path, url_source=None, pptx=False):
    text_data = []

    if pptx:
        elements = partition_pptx(filename=file_path)
    else:
        elements = partition_ppt(filename=file_path)

    full_text = "\n".join([str(el) for el in elements])

    # Extract text from all slides
    category = classify_document(full_text)

    # Extract text from each slide and store it in a structured format with page number, content, category, and source URL
    for element in elements:
        slide_num = element.metadata.page_number
        slide_text = "\n".join([str(shape) for shape in element.shapes if hasattr(shape, "text")])
        text_type = "table" if detect_table_pattern(slide_text) else "text"

        text_data.append({"page_num": slide_num, "content": slide_text, "text_type": text_type ,"category": category, "url": url_source, "doc_type": "ppt"})
    
    return text_data

# Helper function to clean text by removing extra spaces and newlines
def clean_text(text):
    # Normalize multiple newlines and spaces
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    return text

# Helper function to mark sections in the text
def mark_sections(text):
    # Insert double newlines before all-caps or heading-like lines
    text = re.sub(r"(?<!\n)\n(?=[A-Z][^\n]{2,50}\n)", r"\n\n", text)
    return text

# Helper function to chunk text into smaller segments
def chunk_text(text, chunk_size=1000, overlap=100):
    splitter = NLTKTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap, separator="\n\n")
    clean_text_out = mark_sections(text)
    clean_text_out = clean_text(clean_text_out)
    return splitter.split_text(clean_text_out)

# Helper function to save data to a JSONL file
def save_to_json(data, output_file="output/output.json"):
    os.makedirs("output", exist_ok=True)
    with open(output_file, "w") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")

# Helper function to detect table-like patterns in text
def detect_table_pattern(text):
    # Check for common table patterns like pipes, commas, or multiple spaces
    lines = text.strip().split("\n")
    if len(lines) >= 2:
        num_tabular_lines = sum(1 for line in lines if len(line.split()) >= 3 and "|" in line or line.count(" ") > 10)
        return num_tabular_lines / len(lines) > 0.5
    return False

def fetch_documents(urls):
    files = []

    # Implement HTTP client with retry logic
    for url in urls:
        try:
            file_path = download_file(url)
        except RetryError:
            print("Failed to download the file after several attempts.")
        
        if file_path:
            files.append((file_path, url))

    return files

def classify_document(text):
    # Rule-based classification using keyword matching
    for category, keywords in CATEGORIES.items():
        if any(keyword.lower() in text.lower() for keyword in keywords):
            return category
    return "Unknown"

def process_file(file_path, url_source=None):
    
    # Determine the file type based on extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext == ".pdf":
        doc_type = "pdf" 
        extracted_data = parse_pdf(file_path, url_source)
    elif ext == ".ppt":
        doc_type = "ppt"
        extracted_data = parse_ppt(file_path, url_source, pptx=False)
    elif ext == ".pptx":
        doc_type = "pptx"
        extracted_data = parse_ppt(file_path, url_source, pptx=True)
    else:
        doc_type = None
    
    if doc_type is None:
        print(f"Unsupported file type: {ext}")
        return None
    

    return extracted_data
    
def chunk_data(elements):
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

def main():

    urls = [
       "https://view.officeapps.live.com/op/view.aspx?src=https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/SlidesFY25Q2",
       "https://digitalassets.tesla.com/tesla-contents/image/upload/IR/TSLA-Q4-2024-Update.pdf",
       "https://s2.q4cdn.com/470004039/files/doc_earnings/2025/q1/filing/10Q-Q1-2025-as-filed.pdf",
       "https://www.apple.com/newsroom/pdfs/fy2025-q1/FY25_Q1_Consolidated_Financial_Statements.pdf",
       "https://s2.q4cdn.com/470004039/files/doc_financials/2021/q4/_10-K-2021-(As-Filed).pdf"
    ]

    # Fetch and download documents
    raw_files = fetch_documents(urls)

    # Process each file ad parse text
    processed_data = [process_file(f[0],f[1]) for f in raw_files]

    # Chunk the processed data
    chunks = chunk_data(processed_data)
    
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

    # Save to disk
    db.persist()

    print("Data processing and storage complete.")

if __name__ == "__main__":
    main()
