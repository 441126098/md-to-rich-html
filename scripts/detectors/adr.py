"""ADR (Architecture Decision Record) detector."""

from __future__ import annotations

import re
from pathlib import Path

from .base import Detector

ADR_HEADINGS = ("Status", "Context", "Decision", "Consequences")
HEADING_RE = re.compile(
    r"^##\s+(Status|Context|Decision|Consequences)\s*$", re.MULTILINE
)
STATUS_BLOCK_RE = re.compile(
    r"(^##\s+Status\s*$\n+)(?P<value>[^\n]+)", re.MULTILINE
)

STATUS_CLASSES = {
    "proposed": "status-proposed",
    "accepted": "status-accepted",
    "deprecated": "status-deprecated",
    "superseded": "status-superseded",
    "rejected": "status-rejected",
}


class ADRDetector(Detector):
    name = "adr"

    def detect(self, text: str, path: Path) -> float:
        hits = {m.group(1) for m in HEADING_RE.finditer(text)}
        if len(hits) >= 3:
            score = 0.5 + 0.15 * (len(hits) - 3)
        elif len(hits) == 2:
            score = 0.25
        else:
            score = 0.0
        if re.search(r"\badr\b", path.name, re.IGNORECASE):
            score += 0.2
        return min(score, 1.0)

    def transform(self, text: str) -> str:
        def repl(m: re.Match) -> str:
            value = m.group("value").strip()
            cls = STATUS_CLASSES.get(value.lower().split()[0], "status-other")
            badge = (
                f'<span class="adr-status {cls}">{value}</span>'
            )
            return f"{m.group(1)}{badge}\n"

        return STATUS_BLOCK_RE.sub(repl, text)
