from __future__ import annotations

import json
import os
import pickle
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
MAX_QUERY_CHARS = int(os.getenv("MAX_QUERY_CHARS", "1000"))
MAX_K = int(os.getenv("MAX_K", "10"))


class SearchEngine:
    def __init__(self, index_dir: str | Path = "artifacts"):
        self.index_dir = Path(index_dir)
        self.vectors = np.load(self.index_dir / "vectors.npy", mmap_mode="r")
        self.chunks = json.loads((self.index_dir / "chunks.json").read_text(encoding="utf-8"))
        self.documents = {d["doc_id"]: d for d in json.loads((self.index_dir / "documents.json").read_text(encoding="utf-8"))}
        with (self.index_dir / "bm25.pkl").open("rb") as f:
            self.bm25 = pickle.load(f)
        self.model = SentenceTransformer(MODEL_NAME)

    def _validate(self, query: str, k: int) -> tuple[str, int]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        query = query.strip()
        if len(query) > MAX_QUERY_CHARS:
            raise ValueError(f"query is too long; maximum is {MAX_QUERY_CHARS} characters")
        if not isinstance(k, int) or k < 1:
            raise ValueError("k must be a positive integer")
        return query, min(k, MAX_K)

    def search(self, query: str, k: int = 5, hybrid: bool = False) -> list[dict]:
        query, k = self._validate(query, k)
        if hasattr(self.model, "encode_query"):
            q = self.model.encode_query([query], normalize_embeddings=True)[0]
        else:
            q = self.model.encode([query], normalize_embeddings=True)[0]
        semantic = np.asarray(self.vectors) @ np.asarray(q)

        if hybrid:
            tokens = query.lower().split()
            bm25_scores = np.asarray(self.bm25.get_scores(tokens), dtype=np.float32)
            # Min-max normalization makes the two ranking signals comparable.
            sem = _minmax(semantic)
            bm = _minmax(bm25_scores)
            scores = 0.75 * sem + 0.25 * bm
        else:
            scores = semantic

        top = np.argsort(-scores)[:k]
        return [{**self.chunks[int(i)], "score": float(scores[int(i)])} for i in top]


def _minmax(values: np.ndarray) -> np.ndarray:
    lo, hi = float(values.min()), float(values.max())
    if hi - lo < 1e-9:
        return np.zeros_like(values)
    return (values - lo) / (hi - lo)
