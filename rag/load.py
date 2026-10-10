from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Document:
    doc_id: str
    title: str
    text: str
    headings: list[str]
    source_path: str

    def to_dict(self) -> dict:
        return asdict(self)


def parse_markdown(path: Path) -> Document:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    headings: list[str] = []
    heading_stack: list[str] = []
    body: list[str] = []
    in_code = False
    fence = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_code:
                in_code, fence = True, marker
            elif marker == fence:
                in_code, fence = False, None
            body.append(line)
            continue

        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if m and not in_code:
            level = len(m.group(1))
            heading = m.group(2).strip().strip("#").strip()
            while len(heading_stack) >= level:
                heading_stack.pop()
            heading_stack.append(heading)
            headings.append(" > ".join(heading_stack))
        body.append(line)

    title = next((h.split(" > ")[-1] for h in headings if h), path.stem.replace("-", " ").title())
    text = "\n".join(body).strip()
    return Document(path.stem, title, text, headings, str(path.as_posix()))


def load_documents(root: str | Path, selected_ids: set[str] | None = None) -> list[Document]:
    root = Path(root)
    docs = []
    for path in sorted(root.glob("*.md")):
        if selected_ids and path.stem not in selected_ids:
            continue
        docs.append(parse_markdown(path))
    return docs
