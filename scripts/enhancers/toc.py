"""Build a flat table of contents from rendered docs."""

from __future__ import annotations

import re
from dataclasses import dataclass

HEADING_PATTERN = re.compile(
    r'<h([1-3])\s+id="([^"]+)"[^>]*>(.*?)</h\1>', re.DOTALL
)
TAG_STRIP = re.compile(r"<[^>]+>")


@dataclass
class TocEntry:
    level: int
    anchor: str
    text: str


def build_toc(docs) -> list[TocEntry]:
    entries: list[TocEntry] = []
    for doc in docs:
        for m in HEADING_PATTERN.finditer(doc.html):
            level = int(m.group(1))
            anchor = m.group(2)
            text = TAG_STRIP.sub("", m.group(3)).strip()
            entries.append(TocEntry(level=level, anchor=anchor, text=text))
    return entries
