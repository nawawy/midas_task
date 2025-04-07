from utils import get_doc_type, detect_table_pattern
from parse_data_utils import clean_text

def test_get_doc_type_pdf():
    assert get_doc_type("test.pdf") == "pdf"

def test_detect_table():
    table_text = "Name | Age | City\nJohn | 30 | NY"
    assert detect_table_pattern(table_text) == True

def test_clean_text():
    messy_text = "Some   text\n\n\nwith spaces"
    assert clean_text(messy_text) == "Some text with spaces"

