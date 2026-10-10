# Evaluation results

Run `python -m rag.index` and then `python -m eval.run_eval` to populate measured results. Results are intentionally generated from the current OWASP corpus and local embedding model rather than fabricated in advance.

The primary metric is Recall@3 over the fixed 10-question set. Compare at least two chunking configurations before making a claim about retrieval quality.
