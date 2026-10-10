from rag.chunk import chunk_document
from rag.load import Document


def test_heading_path_and_code_are_preserved():
    doc = Document("x", "Title", "# Title\nIntro\n## Defense\n```python\nSELECT * FROM users\n```", [], "x.md")
    chunks = chunk_document(doc, max_words=100, overlap=10, respect_headings=True)
    assert any(c.heading_path == "Defense" for c in chunks)
    assert any(c.has_code for c in chunks)
