# AI/ML Data Engineer Take-Home Assignment

## Overview
This repository contains a solution for an AI/ML Data Engineer role assignment, aimed at building a data ingestion pipeline for processing investor relations documents (PDFs and PPTs). The objective is to fetch, parse, and transform unstructured data into semantic chunks suitable for a Retrieval-Augmented Generation (RAG) system.

---

# Documentation

## 1. Code Structure

This code is divided into the mainn python file "pipeline.py" and other python files containing helper fuctions like:
    
    classifier.py : uses opennai to classify documents into categories ad if it fails it uses keyword matching.
    
    utils.py : contains all helper functions like downloading file, hashing, saving json, detecting whether text is table or simple text, caching parsed files and getting document type like pdf or ppt.

    parse_data_utils : have the function to parse the files into elements and then chunking them into small chunks.

    processed_files.json : contains list of processed files in order not to process them again. 

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

The classification function checks the content of a document and classifies it into predefined categories based on using GPT for classification or keyword matching. This approach leverages the `CATEGORIES` dictionary to determine the appropriate category.

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


# Future Improvements:


# 1. **Enhanced Document Classification**:
    - Implement machine learning models for more accurate and dynamic document classification based on content. This could be achieved by training classifiers on labeled datasets and replacing the current rule-based classification system.
    - Add support for multi-class classification to improve the precision of category assignments.

# 2. **Table Extraction and Analysis**:
    - Improve the `detect_table_pattern` function to handle more complex table structures, including nested tables and tables with dynamic row/column patterns.
    - Allow extraction of table data into structured formats like CSV, Excel, or database entries for easier analysis and reporting.

# 3. **Support for Additional File Formats**:
    - Extend support to handle other file formats like DOCX, XLSX, or HTML documents.
    - Investigate integration with cloud-based APIs (e.g., Google Docs API) to fetch and process documents from online sources.

# 4. **Optimized Text Chunking**:
    - Use more sophisticated NLP models for text chunking, such as transformer-based models, to better understand content context and break text into meaningful chunks.
    - Implement adaptive chunk sizes based on document length or content type to optimize for document processing efficiency.

# 5. **Error Handling and Retry Strategies**:
    - Improve the error handling system to provide more robust responses to failures (e.g., network issues, file corruption, unsupported document types).
    - Expand the retry strategy to allow for exponential backoff, helping to manage rate limits when downloading large volumes of data from external sources.

# 6. **Metadata Enhancement**:
    - Enrich document metadata with additional details, such as the document's author, creation date, and version.
    - Introduce more advanced document parsing techniques to extract and include richer metadata, like keywords, entities, or sentiment scores.

# 7. **Improved Caching Mechanism**:
    - Consider using a more advanced caching mechanism (e.g., a distributed cache or an in-memory database) for faster retrieval and processing of previously downloaded or processed files.
    - Implement versioning for cached files to ensure that documents are reprocessed only when necessary (e.g., after updates).

# 8. **Parallel and Distributed Processing**:
    - Introduce parallel processing or distributed computing frameworks (e.g., Dask, Ray) to handle large batches of documents concurrently, reducing processing time for large datasets.
    - Allow for processing in a cloud-native way, using platforms like AWS Lambda or Google Cloud Functions, to scale the system dynamically based on the load.

# 9. **Database Integration**:
    - Enhance the storage mechanism to support integration with databases (e.g., PostgreSQL, MongoDB) for efficient querying and analysis of the processed data.
    - Support indexing of documents to facilitate faster searches across large datasets.

# 10. **User Interface (UI)**:
    - Develop a user-friendly interface to allow users to interact with the tool more easily, manage files, and visualize processed data.
    - Consider adding support for drag-and-drop document uploads and providing real-time feedback on processing status.
