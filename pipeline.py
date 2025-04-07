# Import necessary libraries
import re
import sys
from typing import List, Dict, Optional, Union
from tenacity import RetryError
import uuid

from langchain.schema import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.globals import set_verbose, set_debug

from utils import download_file, hash_url, save_to_json, load_cache, save_cache, get_doc_type
from parse_data_utils import parse_data, chunk_text

import nltk

# Download necessary NLTK data files
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

# Set up logging and verbosity
set_verbose(False)
set_debug(False)

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
    processed_data = [process_file(f[0],f[1]) for f in raw_files] # f[0] = file_path, f[1] = url source

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
