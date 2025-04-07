# AI/ML Data Engineer Take-Home Assignment

## Overview
This repository contains a solution for an AI/ML Data Engineer role assignment, aimed at building a data ingestion pipeline for processing investor relations documents (PDFs and PPTs). The objective is to fetch, parse, and transform unstructured data into semantic chunks suitable for a Retrieval-Augmented Generation (RAG) system.

---

# Documentation
## 1. Predefined Categories (`CATEGORIES`)

This dictionary holds predefined categories used to classify the documents based on specific keywords. Each category has a list of keywords that help to identify the document type. These categories are primarily related to corporate documents like "Financial Reports", "Press Releases", and "Investor Presentations".

## 2. Imports

The script imports various libraries for:
- **File handling**: `os`, `shutil`, `json`, `uuid`, and `hashlib`.
- **Web requests**: `requests` for downloading files.
- **Text partitioning and processing**: `unstructured.partition` for PDF and PowerPoint parsing, `nltk` for text chunking, and `langchain` for document handling and embeddings.
- **Error handling**: `tenacity` for retrying failed requests.
- **Type hints**: `typing` for specifying types of function arguments and return values.

## 3. NLTK Setup

The script uses **NLTK** (Natural Language Toolkit) for text processing. The relevant data files (`punkt`, `punkt_tab`, `averaged_perceptron_tagger_eng`) are downloaded for tokenization and tagging. These are important for text segmentation and chunking.

### Core Functions

#### 4. `download_file(url: str, save_dir: str)`

This function downloads a file from a specified URL and saves it to a specified directory. It uses the `requests` library to fetch the content and stores it in a local file, retrying the download in case of failure (up to 5 times with a 2-second delay between attempts).

#### 5. `parse_data(file_path: str, url_source: Optional[str], type_file: Optional[str])`

This function parses different types of documents (`pptx`, `ppt`, `pdf`) into text chunks using respective partitioners (`partition_ppt`, `partition_pdf`, `partition_pptx`). It classifies the document based on the content, detects whether it's a table or plain text, and prepares it for further chunking.

#### 6. `clean_text(text: str)`

This helper function normalizes the text by removing extra spaces and newlines, ensuring the text is clean and standardized before further processing.

#### 7. `mark_sections(text: str)`

This function attempts to identify sections within the text by adding double newlines before headings or sections that appear to be in uppercase. This is done using a regular expression to look for uppercase lines, which are often indicative of headings.

#### 8. `chunk_text(text: str, chunk_size: int, overlap: int)`

The function chunks a large text into smaller segments using the **NLTK Text Splitter**. The chunk size is set to a specified value, and a small overlap is allowed between chunks to preserve the context. The text is first cleaned and sections are marked using the `clean_text` and `mark_sections` functions.

#### 9. `save_to_json(data: List[Dict], output_file: str)`

This function writes the processed data (text chunks and associated metadata) to a JSONL file. It ensures the target directory exists before writing and formats the data line-by-line in JSON.

#### 10. `detect_table_pattern(text: str)`

This function attempts to detect whether the provided text contains a table by analyzing the structure of the text. It looks for columns (indicated by the use of `|`), consistency in column counts, and the presence of numeric values to identify structured data.

#### 11. `load_cache()` and `save_cache(cache: Dict[str, Dict])`

These functions are used to load and save cached information about files that have already been processed. The cache helps avoid redundant processing of the same file in case of re-runs.

#### 12. `hash_url(url: str)`

This function generates a hash value for the given URL using MD5. The hash is used as a unique identifier for each URL, which can be stored in the cache.

#### 13. `fetch_documents(urls: List[str])`

This function accepts a list of URLs, checks if they have been processed before (using the cache), and downloads the documents if they haven’t been processed yet. It utilizes the `download_file` function and ensures retries are handled gracefully.

#### 14. `classify_document(text: str)`

The classification function checks the content of a document and classifies it into predefined categories based on keyword matching. This approach leverages the `CATEGORIES` dictionary to determine the appropriate category.

#### 15. `get_doc_type(file_path: str)`

This function determines the type of document (PDF, PowerPoint) based on its file extension.

#### 16. `process_file(file_path: str, url_source: str)`

This function processes each file by checking if it has already been parsed (using the cache). If not, it parses the document using `parse_data` and updates the cache to mark the file as processed.

#### 17. `chunk_data(elements: List[Dict[str, Union[int, str]]])`

This function chunks the content of the parsed documents into smaller text segments using the `chunk_text` function. It creates new chunks from the extracted text and associates them with metadata, including document source, page number, and category.

### Main Function (`main(args=None)`)

The `main` function orchestrates the entire workflow:
1. Downloads documents from the provided URLs.
2. Processes the files and extracts their content using `process_file`.
3. Chunks the content using `chunk_data`.
4. Saves the resulting chunks to a JSONL file.
5. Converts the chunks into `Document` objects and creates embeddings using **HuggingFaceEmbeddings** (or `OpenAIEmbeddings` if preferred).
6. Stores the documents in **ChromaDB**.

### Explanation of NLTK Text Chunking Approach

The script uses **NLTK** to chunk large text into smaller, manageable pieces. Here’s how it works:
- **Text Cleaning**: Before chunking, the text is cleaned to remove extra spaces and newline characters.
- **Section Marking**: The text is processed to mark sections by inserting extra newlines before heading-like structures (detected through uppercase text).
- **Chunking**: The cleaned and marked text is split into chunks of a predefined size (`chunk_size`) with some overlap between adjacent chunks (`overlap`). This ensures that the chunks retain enough context for further processing, such as text embeddings or semantic searches.

NLTK’s **TextSplitter** is used to split the text based on a specified separator (double newlines in this case), helping break down the document into logical, readable parts.

### Conclusion

This code processes corporate documents (like reports and presentations) by:
1. Downloading and parsing the files.
2. Classifying them based on keywords.
3. Chunking the content for further processing.
4. Saving the results to a storage medium (e.g., JSONL file or ChromaDB).

The use of **NLTK** for chunking helps maintain the context within each chunk, and the use of embeddings and ChromaDB aids in efficient searching and semantic analysis of the content.