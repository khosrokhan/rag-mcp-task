import json
from pathlib import Path

import pytest

from rag.store import DocumentStore


def make_store(tmp_path: Path) -> DocumentStore:
    (tmp_path / "documents.json").write_text(json.dumps([
        {"doc_id": "Safe_Doc", "title": "Safe", "text": "hello"}
    ]), encoding="utf-8")
    return DocumentStore(tmp_path)


def test_doc_get_allows_exact_id(tmp_path):
    store = make_store(tmp_path)
    assert store.get("Safe_Doc")["text"] == "hello"


def test_doc_get_blocks_path_traversal(tmp_path):
    store = make_store(tmp_path)
    with pytest.raises(KeyError):
        store.get("../../etc/passwd")
