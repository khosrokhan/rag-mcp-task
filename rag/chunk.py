from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from .load import Document


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    heading_path: str
    text: str
    has_code: bool

    def to_dict(self) -> dict:
        return asdict(self)


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def chunk_document(doc: Document, max_words: int = 700, overlap: int = 120, respect_headings: bool = True) -> list[Chunk]:
    # Keep fenced code blocks intact as much as possible and carry the current heading path.
    lines = doc.text.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_heading = ""
    current: list[str] = []
    in_code = False

    for line in lines:
        if line.strip().startswith(("```", "~~~")):
            in_code = not in_code
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line) if not in_code else None
        if m and respect_headings:
            if current:
                sections.append((current_heading, current))
            current_heading = m.group(2).strip().strip("#").strip()
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append((current_heading, current))

    chunks: list[Chunk] = []
    seq = 0
    for heading, section_lines in sections:
        words = " ".join(section_lines).split()
        if not words:
            continue
        start = 0
        while start < len(words):
            end = min(start + max_words, len(words))
            text = " ".join(words[start:end]).strip()
            if text:
                chunks.append(Chunk(
                    chunk_id=f"{doc.doc_id}:{seq}",
                    doc_id=doc.doc_id,
                    title=doc.title,
                    heading_path=heading or doc.title,
                    text=text,
                    has_code="```" in text or "~~~" in text,
                ))
                seq += 1
            if end >= len(words):
                break
            start = max(0, end - overlap)

    return chunks


def chunk_documents(docs: list[Document], **kwargs) -> list[Chunk]:
    result: list[Chunk] = []
    for doc in docs:
        result.extend(chunk_document(doc, **kwargs))
    return result
