# Security RAG + MCP Server

A small, reproducible implementation of the interview task: semantic retrieval over 30–50 OWASP Cheat Sheet Series Markdown documents, measured with a 10-question evaluation set, and exposed through an MCP server.

## What this project does

1. Downloads/clones the official OWASP CheatSheetSeries repository and selects 40 security-focused cheat sheets.
2. Parses Markdown while preserving document title, text, code blocks, and heading paths.
3. Creates two chunking configurations so retrieval can be measured rather than assumed.
4. Embeds chunks locally with Sentence Transformers and stores vectors as NumPy plus metadata JSON.
5. Retrieves top-k chunks with cosine similarity.
6. Optionally combines semantic retrieval with BM25 for the +10 point hybrid-search section.
7. Runs a fixed 10-question evaluation and reports Recall@3.
8. Exposes `docs_search(query, k)` and `doc_get(doc_id)` through MCP.
9. Protects `doc_get` against path traversal and limits untrusted inputs.

## Requirements

- Python 3.10+
- Git
- Internet access only for the one-time OWASP clone and model download

## Quick start

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
python scripts/fetch_data.py
python -m rag.index --chunk-size 700 --overlap 120 --respect-headings
python -m eval.run_eval --config artifacts/index_meta.json
python -m mcp_server.server
```

The first index build downloads `sentence-transformers/all-MiniLM-L6-v2` automatically. The model and vector files are intentionally not committed.

## Chunking decision

Default: approximately 700 whitespace-token words with 120-word overlap, while flushing at heading boundaries. Security cheat sheets contain short sections and code examples; preserving the heading path gives the retriever useful context such as `SQL Injection Prevention > Defense Option 1` rather than an anonymous text fragment. Code blocks are retained because secure coding guidance often appears directly in examples. The parser also marks code blocks separately in metadata.

Run the alternative configuration for evaluation:

```bash
python -m rag.index --chunk-size 350 --overlap 60 --no-respect-headings --output-dir artifacts/index_small
python -m eval.run_eval --index-dir artifacts/index_small
```

## Evaluation

`eval/questions.json` contains 10 security questions and expected document IDs. At least three questions deliberately avoid repeating the expected document title words. The metric is Recall@3: whether the expected document appears in the first three retrieved documents. `results.md` compares two chunking configurations and, when requested, semantic vs hybrid retrieval.

A small evaluation is intentionally fixed and reproducible; it is not a claim of production-grade RAG quality.

## MCP

The server exposes exactly two required tools:

- `docs_search(query, k)`: semantic/hybrid retrieval; returns chunk text, document title, heading path, and score.
- `doc_get(doc_id)`: returns the full text of an allow-listed document.

Use MCP Inspector during development:

```bash
mcp dev mcp_server/server.py
```

The official Python MCP SDK currently uses the v2 API (`MCPServer`). If your environment is intentionally pinned to MCP v1, adapt the import/API to the v1 SDK rather than mixing versions.

## Security notes

- `doc_get` accepts only a document ID from the generated allow-list; it never joins arbitrary user input onto a filesystem root.
- `k`, query length, and output length are capped.
- Retrieval is read-only.
- No secrets are committed; use `.env.example` for optional configuration.
- Retrieved document text is **data**, not instructions. If an indexed document contains prompt-injection text, an LLM consuming the result could mistake it for instructions. A production system should delimit retrieved content, make source trust explicit, and instruct the model to treat retrieved text as untrusted reference material.

## Scaling note

NumPy brute-force cosine search is ideal for this small task and keeps the implementation understandable. At 100x the corpus size, loading/scanning every vector for each query becomes the bottleneck; an ANN/vector database such as Qdrant, pgvector, or FAISS would be a better next step.

## Tests

```bash
pytest -q
```

The tests include a traversal attack against `doc_get` and retrieval behavior using a tiny fake index.

## Sources

- OWASP Cheat Sheet Series: https://github.com/OWASP/CheatSheetSeries
- Model Context Protocol Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Sentence Transformers: https://sbert.net/

