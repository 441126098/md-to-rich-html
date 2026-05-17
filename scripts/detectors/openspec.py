"""OpenSpec detector: BDD scenarios, delta sections, requirement cards.

Implementation note on ordering:
--------------------------------
The two transformations are applied in this order:

1. Scenario conversion (#### Scenario: ... → <article class="scenario">)
2. Delta section wrapping (## ADDED/MODIFIED/REMOVED Requirements → <section>)

Order matters because #1 emits HTML that the regex in #2 must skip past
correctly. We use a line-based scanner for #2 to avoid the regex-eats-html
hazard that a single big DOTALL pattern would create.
"""

from __future__ import annotations

import re
from pathlib import Path

from .base import Detector

# Detection patterns
REQUIREMENT_RE = re.compile(r"^### Requirement:", re.MULTILINE)
SCENARIO_RE = re.compile(r"^#### Scenario:", re.MULTILINE)
WHEN_RE = re.compile(r"\*\*WHEN\*\*", re.MULTILINE)
THEN_RE = re.compile(r"\*\*THEN\*\*", re.MULTILINE)
DELTA_RE = re.compile(r"^## (ADDED|MODIFIED|REMOVED) Requirements", re.MULTILINE)

# Transform: scenario block matcher. The body extends until the next ####
# heading, the next ### or ## heading, or end-of-file.
SCENARIO_BLOCK_RE = re.compile(
    r"^#### Scenario:\s*(?P<title>[^\n]+)\n"
    r"(?P<body>(?:(?!^#### )(?!^### )(?!^## )(?!^# ).)*?)"
    r"(?=^#### |^### |^## |^# |\Z)",
    re.MULTILINE | re.DOTALL,
)

DELTA_HEADING_RE = re.compile(r"^## (ADDED|MODIFIED|REMOVED) Requirements\s*$")
ANY_H2_RE = re.compile(r"^## ")
DELTA_LABELS = {"ADDED": "Added", "MODIFIED": "Modified", "REMOVED": "Removed"}


class OpenSpecDetector(Detector):
    name = "openspec"

    def detect(self, text: str, path: Path) -> float:
        score = 0.0
        if REQUIREMENT_RE.search(text):
            score += 0.35
        if SCENARIO_RE.search(text) and WHEN_RE.search(text) and THEN_RE.search(text):
            score += 0.45
        if DELTA_RE.search(text):
            score += 0.30
        lname = path.name.lower()
        if lname in {"proposal.md", "tasks.md", "design.md"}:
            score += 0.15
        if "specs" in path.parts or "changes" in path.parts:
            score += 0.10
        return min(score, 1.0)

    def transform(self, text: str) -> str:
        # Phase 1: scenarios → HTML cards
        text = self._convert_scenarios(text)
        # Phase 2: delta sections → wrapping <section> tags (line-based scan)
        text = self._wrap_delta_sections(text)
        return text

    # -- Phase 1: BDD scenarios -------------------------------------------

    def _convert_scenarios(self, text: str) -> str:
        def repl(m: re.Match) -> str:
            title = m.group("title").strip()
            body = m.group("body")
            given_items, when_items, then_items = self._parse_scenario_body(body)
            cols_html = "".join([
                self._render_col("Given", given_items, "given"),
                self._render_col("When", when_items, "when"),
                self._render_col("Then", then_items, "then"),
            ])
            return (
                f'\n<article class="scenario">\n'
                f'<header class="scenario-title">{title}</header>\n'
                f'<div class="scenario-body">{cols_html}</div>\n'
                f'</article>\n\n'
            )

        return SCENARIO_BLOCK_RE.sub(repl, text)

    @staticmethod
    def _parse_scenario_body(body: str) -> tuple[list[str], list[str], list[str]]:
        given: list[str] = []
        when: list[str] = []
        then: list[str] = []
        current: list[str] | None = None

        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            is_bullet = line.startswith(("- ", "* "))
            content = line[2:].strip() if is_bullet else line

            upper = content.upper()
            kw = None
            for k in ("**GIVEN**", "**WHEN**", "**THEN**", "**AND**", "**BUT**"):
                if upper.startswith(k):
                    kw = k
                    break

            if kw:
                stripped = content[len(kw):].strip()
                if kw == "**GIVEN**":
                    current = given
                    current.append(stripped)
                elif kw == "**WHEN**":
                    current = when
                    current.append(stripped)
                elif kw == "**THEN**":
                    current = then
                    current.append(stripped)
                elif kw in ("**AND**", "**BUT**") and current is not None:
                    current.append(stripped)
            elif is_bullet and current is not None:
                current.append(content)
            elif current and not is_bullet:
                current[-1] += " " + content
        return given, when, then

    @staticmethod
    def _render_col(label: str, items: list[str], cls: str) -> str:
        if not items:
            return ""
        lis = "\n".join(f"<li>{i}</li>" for i in items)
        return (
            f'<div class="scenario-col {cls}">'
            f'<div class="scenario-label">{label}</div>'
            f'<ul>{lis}</ul></div>'
        )

    # -- Phase 2: Delta sections (line-based) -----------------------------

    def _wrap_delta_sections(self, text: str) -> str:
        """Wrap ## ADDED/MODIFIED/REMOVED Requirements ... blocks.

        Walk lines top-to-bottom. When we hit a delta heading, open a
        section. When we hit any other ## heading or EOF, close it.
        """
        out: list[str] = []
        in_delta: str | None = None

        for line in text.splitlines():
            m = DELTA_HEADING_RE.match(line)
            if m:
                if in_delta is not None:
                    out.append("\n</section>\n")
                in_delta = m.group(1).lower()
                label = DELTA_LABELS[m.group(1)]
                out.append(
                    f'\n<section class="delta delta-{in_delta}">\n\n'
                    f'<header class="delta-header">'
                    f'<span class="delta-icon" aria-hidden="true"></span>'
                    f'<span class="delta-label">{label} Requirements</span>'
                    f'</header>\n'
                )
                continue

            if in_delta is not None and ANY_H2_RE.match(line):
                out.append("\n</section>\n")
                in_delta = None
                out.append(line)
                continue

            out.append(line)

        if in_delta is not None:
            out.append("\n</section>\n")

        return "\n".join(out)
