from pipeline import classify_document

def test_classify_financial_report():
    text = "This is our annual report for Q4 earnings"
    assert classify_document(text) == "Financial Reports"

def test_classify_unknown():
    text = "Nothing in here matches"
    assert classify_document(text) == "Unknown"

def test_classify_press_releases():
    text = "Press Release: We are excited to announce our new product launch"
    assert classify_document(text) == "Press Releases"