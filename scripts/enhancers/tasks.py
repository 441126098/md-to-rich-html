"""Task-list enhancer: count - [ ] / - [x] across the doc, return summary."""

from __future__ import annotations

import re
from dataclasses import dataclass

TASK_PATTERN = re.compile(r"^\s*[-*]\s+\[( |x|X)\]\s+", re.MULTILINE)


@dataclass
class TasksSummary:
    total: int
    done: int

    @property
    def pct(self) -> int:
        return int(round(100 * self.done / self.total)) if self.total else 0

    @property
    def has_tasks(self) -> bool:
        return self.total > 0


def extract_tasks_summary(markdown_source: str) -> TasksSummary:
    matches = TASK_PATTERN.findall(markdown_source)
    total = len(matches)
    done = sum(1 for m in matches if m.lower() == "x")
    return TasksSummary(total=total, done=done)
