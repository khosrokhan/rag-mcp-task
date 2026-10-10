from __future__ import annotations

import json
from pathlib import Path


class DocumentStore:
    """Allow-listed document store; never resolves arbitrary paths from user input."""
    def __init__(self, index_dir: str | Path = "artifacts"):
        self.index_dir = Path(index_dir)
        self.docs = {d["doc_id"]: d for d in json.loads((self.index_dir / "documents.json").read_text(encoding="utf-8"))}

    def get(self, doc_id: str) -> dict:
        if not isinstance(doc_id, str) or not doc_id:
            raise ValueError("doc_id must be a non-empty string")
        # Exact allow-list lookup is the traversal defense: ../ cannot become a path.
        doc = self.docs.get(doc_id)
        if doc is None:
            raise KeyError("document not found")
        return doc
