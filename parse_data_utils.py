from unstructured.partition.pdf import partition_pdf
from unstructured.partition.ppt import partition_ppt
from unstructured.partition.pptx import partition_pptx

from typing import List, Dict, Optional, Union
from collections import defaultdict
import re
from classifier import classify_document
from utils import detect_table_pattern
from langchain.text_splitter import NLTKTextSplitter

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
