# AI/ML Data Engineer Take-Home Assignment

## Overview
This repository contains a solution for an AI/ML Data Engineer role assignment, aimed at building a data ingestion pipeline for processing investor relations documents (PDFs and PPTs). The objective is to fetch, parse, and transform unstructured data into semantic chunks suitable for a Retrieval-Augmented Generation (RAG) system.

---

## Table of Contents

- [Functions Documentation](#functions-documentation)


### Functions Documentation

#### download_file(url, save_dir="downloads")
Downloads a file from the provided URL and saves it to the specified directory.

    Parameters:

        url (str): The URL to fetch the document from.

        save_dir (str): Directory to save the downloaded file.

    Returns:

        str: The path to the saved file, or None if the download failed.

#### parse_data(file_path, url_source=None, type_file=None)
Extracts text and metadata from the provided document.

    Parameters:

        file_path (str): Path to the file to parse.

        url_source (str): The URL source of the document.

        type_file (str): The type of document (pdf, ppt, or pptx).

    Returns:

        list: A list of extracted content with metadata.

#### clean_text(text)
Cleans the provided text by removing extra spaces and newlines.

    Parameters:

        text (str): The text to clean.

    Returns:

        str: The cleaned text.

#### mark_sections(text)
Marks sections in the text by adding newlines before capitalized headings.

    Parameters:

        text (str): The text to process.

    Returns:

        str: The processed text with marked sections.

#### chunk_text(text, chunk_size=1000, overlap=100)
Chunks the provided text into smaller pieces based on the specified chunk size and overlap.

    Parameters:

        text (str): The text to chunk.

        chunk_size (int): The maximum chunk size (default is 1000 tokens).

        overlap (int): The overlap between consecutive chunks (default is 100).

    Returns:

        list: A list of chunks.

#### save_to_json(data, output_file="output/output.json")
Saves the provided data to a JSONL file.

    Parameters:

        data (list): The data to save.

        output_file (str): The file path to save the data to.

#### detect_table_pattern(text)
Detects if the provided text contains table-like patterns.

    Parameters:

        text (str): The text to check.

    Returns:

        bool: True if a table-like pattern is detected, False otherwise.

#### classify_document(text)
Classifies the provided document based on predefined categories using keyword matching.

    Parameters:

        text (str): The document text to classify.

    Returns:

        str: The category of the document.

#### get_doc_type(file_path)
Determines the type of document based on its file extension.

    Parameters:

        file_path (str): The path to the file.

    Returns:

        str: The type of document (pdf, ppt, or pptx).

#### process_file(file_path, url_source=None)
Processes a file by extracting its content and metadata.

    Parameters:

        file_path (str): The path to the file.

        url_source (str): The URL source of the file.

    Returns:

        list: A list of extracted content with metadata.

#### chunk_data(elements)
Chunks the extracted data into smaller semantic chunks.

    Parameters:

        elements (list): The extracted elements.

    Returns:

        list: A list of chunked data with metadata.


