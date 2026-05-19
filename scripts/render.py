#!/usr/bin/env python3
"""md-to-rich-html: turn technical Markdown into a single portable HTML file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make sibling packages importable when invoked as `python scripts/render.py`
sys.path.insert(0, str(Path(__file__).parent))

from core.pipeline import Pipeline, PipelineOptions  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="md-to-rich-html",
        description="Convert technical Markdown to a self-contained HTML file.",
    )
    p.add_argument("input", type=Path, help=".md file or directory of .md files")
    p.add_argument("-o", "--output", type=Path, default=None, help="output HTML path")
    p.add_argument(
        "--theme",
        choices=("auto", "light", "dark"),
        default="auto",
        help="initial color theme (default: auto)",
    )
    p.add_argument(
        "--layout",
        choices=("article", "report"),
        default="article",
        help="page layout (default: article)",
    )
    p.add_argument("--title", default=None, help="document title")
    p.add_argument("--no-mermaid", action="store_true", help="don't inline Mermaid")
    p.add_argument("--no-toc", action="store_true", help="skip table of contents")
    return p.parse_args()


def collect_input(path: Path) -> list[Path]:
    """Return ordered list of .md files. README.md first, then alphabetical."""
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(f"input not found: {path}")
    files = sorted(path.rglob("*.md"))
    readmes = [f for f in files if f.name.lower() == "readme.md"]
    others = [f for f in files if f.name.lower() != "readme.md"]
    return readmes + others


def main() -> int:
    args = parse_args()
    files = collect_input(args.input)
    if not files:
        print(f"error: no .md files found in {args.input}", file=sys.stderr)
        return 1

    output = args.output or Path(f"{args.input.stem}.html")
    output.parent.mkdir(parents=True, exist_ok=True)

    opts = PipelineOptions(
        title=args.title,
        theme=args.theme,
        layout=args.layout,
        inline_mermaid=not args.no_mermaid,
        include_toc=not args.no_toc,
        base_dir=args.input if args.input.is_dir() else args.input.parent,
    )

    html = Pipeline(opts).run(files)
    output.write_text(html, encoding="utf-8")

    size_kb = len(html.encode("utf-8")) / 1024
    print(f"✓ wrote {output} ({size_kb:.1f} KB, {len(files)} source file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
