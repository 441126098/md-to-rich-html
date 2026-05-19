---
name: md-to-rich-html
description: Convert technical Markdown files or folders into a polished, self-contained HTML document with GFM rendering, syntax highlighting, Mermaid, task lists, TOC, dark mode, and light auto-detection for OpenSpec/ADR patterns.
---

# Markdown to Rich HTML

Use this skill when the user wants to render, preview, publish, share, or make technical Markdown easier to read. It supports a single `.md` file or a folder of `.md` files.

## Run

```bash
python scripts/render.py <input> -o <output.html>
```

Useful options:

- `--theme {auto,light,dark}` sets the initial theme.
- `--layout {article,report}` chooses classic long-form output or a structured report layout.
- `--title TEXT` overrides the inferred first `#` heading.
- `--no-mermaid` skips Mermaid runtime injection.
- `--no-toc` skips the table of contents.

## Behavior

- Renders GFM-style tables, fenced code, footnotes, task lists, and headings.
- Adds syntax highlighting, Mermaid diagrams, a TOC, and a theme toggle.
- Auto-enhances OpenSpec deltas/scenarios and ADR status sections when detected.
- Keeps output portable as a single offline HTML file.

## Workflow

1. Inspect whether the input is a file or folder.
2. Run `python scripts/render.py <input> -o <output.html>`.
3. Return the generated HTML path to the user.

## Maintenance

- Add detectors under `scripts/detectors/` and register them in `scripts/core/pipeline.py`.
- Keep visual changes in `assets/style.css`.
- Keep template structure in `templates/base.html.j2`.
