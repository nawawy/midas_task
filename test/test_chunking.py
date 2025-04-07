from parse_data_utils import chunk_text

def test_chunking_overlap():
    text = " ".join(["This is sentence {}".format(i) for i in range(50)])
    chunks = chunk_text(text, chunk_size=50, overlap=10)
    assert len(chunks) >= 1
    assert "sentence 0" in chunks[0]

