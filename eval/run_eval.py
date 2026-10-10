from __future__ import annotations

import argparse
import json
from pathlib import Path

from rag.search import SearchEngine


def evaluate(index_dir: str, questions_path: str, hybrid: bool = False) -> tuple[float, list[dict]]:
    engine = SearchEngine(index_dir)
    questions = json.loads(Path(questions_path).read_text(encoding="utf-8"))
    rows = []
    hits = 0
    for q in questions:
        results = engine.search(q["question"], k=3, hybrid=hybrid)
        ids = [r["doc_id"] for r in results]
        hit = q["expected_doc"] in ids
        hits += int(hit)
        rows.append({"id": q["id"], "expected": q["expected_doc"], "top3": ids, "hit": hit})
    return hits / len(questions), rows


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--index-dir", default="artifacts")
    p.add_argument("--questions", default="eval/questions.json")
    p.add_argument("--hybrid", action="store_true")
    args = p.parse_args()
    score, rows = evaluate(args.index_dir, args.questions, args.hybrid)
    lines = [f"# Evaluation results\n", f"Recall@3: **{sum(r['hit'] for r in rows)}/{len(rows)} = {score:.0%}**\n", "| # | Expected document | Top 3 | Hit |", "|---:|---|---|:---:|"]
    for r in rows:
        lines.append(f"| {r['id']} | `{r['expected']}` | {', '.join('`'+x+'`' for x in r['top3'])} | {'yes' if r['hit'] else 'NO'} |")
    Path(args.index_dir, "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Recall@3: {sum(r['hit'] for r in rows)}/{len(rows)} = {score:.0%}")


if __name__ == "__main__":
    main()
