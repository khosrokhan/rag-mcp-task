# Learning notes

- **New concepts:** RAG retrieval/evaluation and the Model Context Protocol. I used the official Sentence Transformers documentation for asymmetric semantic search and the official MCP Python SDK documentation for server/tool concepts.
- **Where I got stuck:** The current MCP Python SDK has a v2 API while older examples use `FastMCP`. I resolved this by targeting the current `MCPServer` API and documenting the version choice in the README.
- **Still unclear:** I would like to understand how retrieval quality changes with a cross-encoder reranker and how an MCP host decides between multiple overlapping tools when tool descriptions are similar.
