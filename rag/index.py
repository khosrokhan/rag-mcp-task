from __future__ import annotations

import argparse
import json
import os
import pickle
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from .chunk import chunk_documents
from .load import load_documents

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

SELECTED_FILES = {
    "Access_Control_Cheat_Sheet", "Authentication_Cheat_Sheet", "Authorization_Cheat_Sheet",
    "Cross_Site_Request_Forgery_Prevention_Cheat_Sheet", "Cross_Site_Scripting_Prevention_Cheat_Sheet",
    "Cryptographic_Storage_Cheat_Sheet", "Database_Security_Cheat_Sheet", "Django_REST_Framework_Cheat_Sheet",
    "Django_Security_Cheat_Sheet", "Error_Handling_Cheat_Sheet", "File_Upload_Cheat_Sheet",
    "Forgot_Password_Cheat_Sheet", "GraphQL_Cheat_Sheet", "HTTP_Headers_Cheat_Sheet",
    "Input_Validation_Cheat_Sheet", "Injection_Prevention_Cheat_Sheet", "Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet",
    "JSON_Web_Token_Cheat_Sheet", "LDAP_Injection_Prevention_Cheat_Sheet", "LLM_Prompt_Injection_Prevention_Cheat_Sheet",
    "Logging_Cheat_Sheet", "MCP_Security_Cheat_Sheet", "Mass_Assignment_Cheat_Sheet", "Microservices_Security_Cheat_Sheet",
    "OAuth2_Cheat_Sheet", "OS_Command_Injection_Defense_Cheat_Sheet", "Password_Storage_Cheat_Sheet",
    "Query_Parameterization_Cheat_Sheet", "RAG_Security_Cheat_Sheet", "REST_Security_Cheat_Sheet",
    "SQL_Injection_Prevention_Cheat_Sheet", "Secrets_Management_Cheat_Sheet", "Server_Side_Request_Forgery_Prevention_Cheat_Sheet",
    "Session_Management_Cheat_Sheet", "Software_Supply_Chain_Security_Cheat_Sheet", "Threat_Modeling_Cheat_Sheet",
    "Transport_Layer_Security_Cheat_Sheet", "Unvalidated_Redirects_and_Forwards_Cheat_Sheet", "User_Privacy_Protection_Cheat_Sheet",
    "XML_External_Entity_Prevention_Cheat_Sheet", "XSS_Filter_Evasion_Cheat_Sheet",
}


def build_index(docs_dir: str, output_dir: str, chunk_size: int, overlap: int, respect_headings: bool) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    docs = load_documents(docs_dir, SELECTED_FILES)
    if not docs:
        raise SystemExit("No documents found. Run `python scripts/fetch_data.py` first.")
    chunks = chunk_documents(docs, max_words=chunk_size, overlap=overlap, respect_headings=respect_headings)
    model = SentenceTransformer(MODEL_NAME)
    texts = [f"{c.title}\n{c.heading_path}\n{c.text}" for c in chunks]
    if hasattr(model, "encode_document"):
        vectors = model.encode_document(texts, normalize_embeddings=True, show_progress_bar=True)
    else:
        vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    np.save(out / "vectors.npy", np.asarray(vectors, dtype=np.float32))
    (out / "chunks.json").write_text(json.dumps([c.to_dict() for c in chunks], ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "documents.json").write_text(json.dumps([d.to_dict() for d in docs], ensure_ascii=False, indent=2), encoding="utf-8")
    bm25 = BM25Okapi([c.text.lower().split() for c in chunks])
    with (out / "bm25.pkl").open("wb") as f:
        pickle.dump(bm25, f)
    meta = {
        "model": MODEL_NAME,
        "chunk_size": chunk_size,
        "overlap": overlap,
        "respect_headings": respect_headings,
        "num_documents": len(docs),
        "num_chunks": len(chunks),
    }
    (out / "index_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--docs-dir", default="data/cheatsheets")
    p.add_argument("--output-dir", default="artifacts")
    p.add_argument("--chunk-size", type=int, default=700)
    p.add_argument("--overlap", type=int, default=120)
    p.add_argument("--respect-headings", action=argparse.BooleanOptionalAction, default=True)
    args = p.parse_args()
    build_index(args.docs_dir, args.output_dir, args.chunk_size, args.overlap, args.respect_headings)
