import hashlib
import os
import requests
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from typing import List, Dict
import json
import re
from typing import List, Dict, Optional, Union

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

# Helper fuction to hash URLs
def hash_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()

# Helper function to save data to a JSONL file
def save_to_json(data: List[Dict], output_file: str = "output/output.json") -> None:
    os.makedirs("output", exist_ok=True)
    with open(output_file, "w") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")
    print(f"Saved data to {output_file}")

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

# Helper function to save cache to a JSON file
def save_cache(cache : Dict[str, Dict]) -> None:
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

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
