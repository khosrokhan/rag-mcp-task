# Architecture

```text
OWASP Markdown files
        |
        v
  load.py (metadata + headings)
        |
        v
  chunk.py (heading-aware chunks)
        |
        +--------------------+
        |                    |
        v                    v
SentenceTransformer       BM25
        |                    |
        +---------+----------+
                  v
            SearchEngine
                  |
          +-------+-------+
          |               |
      CLI eval         MCP server
                          |
                  +-------+-------+
                  |               |
             docs_search      doc_get
```

The key design choice is separation: parsing/chunking/indexing/search are ordinary Python modules; MCP is a thin adapter. This makes retrieval testable without starting an MCP process.
