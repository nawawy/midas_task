from unittest.mock import patch
from parse_data_utils import parse_data

@patch("parse_data_utils.partition_pdf")
def test_parse_pdf(mock_partition):
    mock_partition.return_value = [
        type("obj", (object,), {"text": "Some content", "metadata": type("meta", (object,), {"page_number": 1})})()
    ]
    result = parse_data("dummy.pdf", "http://url", type_file="pdf")
    assert result[0]["page_num"] == 1
    assert "Some content" in result[0]["content"]