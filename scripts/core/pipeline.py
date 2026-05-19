"""Pipeline: orchestrates parsing, detection, enhancement, and rendering."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from core.markdown import build_md, render_to_html
from detectors.base import Detector
from detectors.openspec import OpenSpecDetector
from detectors.adr import ADRDetector
from enhancers.tasks import extract_tasks_summary
from enhancers.toc import build_toc

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
ASSETS_DIR = PROJECT_ROOT / "assets"

DETECTORS: list[type[Detector]] = [OpenSpecDetector, ADRDetector]
CONFIDENCE_THRESHOLD = 0.4


@dataclass
class PipelineOptions:
    title: str | None = None
    theme: str = "auto"
    layout: str = "article"
    inline_mermaid: bool = True
    include_toc: bool = True
    base_dir: Path = field(default_factory=Path.cwd)


@dataclass
class ReportSection:
    index: int
    title: str
    anchor: str
    heading_html: str
    body_html: str
    kind: str


@dataclass
class RenderedDoc:
    """One source .md file after parsing + detection + html rendering."""

    path: Path
    raw: str
    html: str
    intro_html: str
    sections: list[ReportSection]
    detectors: list[str]
    has_mermaid: bool


class Pipeline:
    def __init__(self, opts: PipelineOptions):
        self.opts = opts
        self.md = build_md()
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def run(self, files: list[Path]) -> str:
        docs = [self._process_file(f) for f in files]

        combined_raw = "\n\n".join(d.raw for d in docs)
        all_detectors = sorted({name for d in docs for name in d.detectors})
        any_mermaid = any(d.has_mermaid for d in docs)
        tasks = extract_tasks_summary(combined_raw)
        toc = build_toc(docs) if self.opts.include_toc else []
        title = self._infer_title(docs)

        style_css = (ASSETS_DIR / "style.css").read_text(encoding="utf-8")
        theme_js = (ASSETS_DIR / "theme-toggle.js").read_text(encoding="utf-8")
        mermaid_js = ""
        if any_mermaid and self.opts.inline_mermaid:
            mermaid_path = ASSETS_DIR / "mermaid.min.js"
            if mermaid_path.exists():
                mermaid_js = mermaid_path.read_text(encoding="utf-8")

        template = self.env.get_template("base.html.j2")
        return template.render(
            title=title,
            theme=self.opts.theme,
            layout=self.opts.layout,
            docs=docs,
            toc=toc,
            tasks=tasks,
            detectors=all_detectors,
            has_mermaid=any_mermaid,
            style_css=style_css,
            theme_js=theme_js,
            mermaid_js=mermaid_js,
        )

    def _process_file(self, path: Path) -> RenderedDoc:
        raw = path.read_text(encoding="utf-8")

        # Layer 3: which detectors fire?
        active: list[Detector] = []
        for cls in DETECTORS:
            d = cls()
            if d.detect(raw, path) >= CONFIDENCE_THRESHOLD:
                active.append(d)

        # Detectors can rewrite the markdown source before parsing.
        # Order matters: OpenSpec first (most specific), then ADR.
        transformed = raw
        for d in active:
            transformed = d.transform(transformed)

        html = render_to_html(self.md, transformed)
        has_mermaid = bool(re.search(r'<div class="mermaid">', html))
        intro_html, sections = self._build_report_sections(html)

        return RenderedDoc(
            path=path,
            raw=raw,
            html=html,
            intro_html=intro_html,
            sections=sections,
            detectors=[d.name for d in active],
            has_mermaid=has_mermaid,
        )

    def _infer_title(self, docs: list[RenderedDoc]) -> str:
        if self.opts.title:
            return self.opts.title
        for d in docs:
            m = re.search(r"^#\s+(.+)$", d.raw, re.MULTILINE)
            if m:
                return m.group(1).strip()
        return "Document"

    def _build_report_sections(self, html: str) -> tuple[str, list[ReportSection]]:
        html = re.sub(r"<h1\b[^>]*>.*?</h1>", "", html, count=1, flags=re.DOTALL)
        parts = re.split(r"(<h2\s+id=\"([^\"]+)\"[^>]*>.*?</h2>)", html, flags=re.DOTALL)
        intro_html = parts[0].strip()
        sections: list[ReportSection] = []

        for i in range(1, len(parts), 3):
            heading_html = parts[i]
            anchor = parts[i + 1]
            body_html = parts[i + 2].strip() if i + 2 < len(parts) else ""
            title = re.sub(r"<[^>]+>", "", heading_html).strip()
            sections.append(
                ReportSection(
                    index=len(sections) + 1,
                    title=title,
                    anchor=anchor,
                    heading_html=heading_html,
                    body_html=body_html,
                    kind=self._section_kind(body_html),
                )
            )

        if not sections and intro_html:
            sections.append(
                ReportSection(
                    index=1,
                    title="Overview",
                    anchor="overview",
                    heading_html='<h2 id="overview">Overview</h2>',
                    body_html=intro_html,
                    kind=self._section_kind(intro_html),
                )
            )
            intro_html = ""

        return intro_html, sections

    def _section_kind(self, html: str) -> str:
        if 'class="mermaid"' in html:
            return "diagram"
        if "<table" in html:
            return "data"
        if 'class="hl"' in html or "<pre" in html:
            return "code"
        if "task-list-item" in html:
            return "checklist"
        if "<blockquote" in html:
            return "callout"
        return "text"
