---
name: md-to-rich-html
description: Convert one or more technical Markdown documents into a single self-contained HTML file optimized for human reading. Renders GFM (tables, fenced code, task lists), syntax-highlights code, renders Mermaid diagrams inline, and auto-detects common technical-doc patterns (OpenSpec proposals/specs/tasks with BDD WHEN/THEN scenarios, ADDED/MODIFIED/REMOVED delta sections, architecture decision records) to apply richer styling. Use when the user wants to "render", "preview", "publish", "share", or "visualize" technical Markdown — including READMEs, RFCs, ADRs, OpenSpec artifacts, design docs, or any .md file they want to make more readable. Outputs a single portable HTML file with dark/light mode and a table of contents; opens offline.
---

# Markdown → Rich HTML

A skill for turning technical Markdown into a polished, self-contained HTML file
optimized for human reading. Built around three layers:

1. **Standard Markdown → HTML** (GFM-complete: tables, fenced code, task lists, footnotes)
2. **Generic enhancements** (syntax highlighting, Mermaid, TOC, dark mode)
3. **Pattern detectors** (OpenSpec, ADR — opt-in, auto-detected, additive)

If a detector matches, you get richer styling. If none match, you still get a
clean, readable document.

## When to use

- User wants to share a `.md` file (or folder of `.md` files) as a webpage
- User mentions OpenSpec, ADR, RFC, design doc, technical specification
- User says "render", "preview", "make readable", "publish", "share"
- Output should be portable: emailable, openable offline, no server needed

## When NOT to use

- User wants a **multi-page** site → suggest MkDocs or Docusaurus instead
- User wants Markdown for a blog feed → use a static site generator
- The Markdown is non-technical prose without code/diagrams/specs

## Usage

```
python scripts/render.py <input> -o <output.html> [options]
```

Arguments:
- `<input>` — a `.md` file, or a directory of `.md` files (recursively concatenated
  in the order: alphabetical by path, with `README.md` first if present)
- `-o, --output` — output HTML path (default: `<input_stem>.html`)
- `--theme {auto,light,dark}` — initial theme (default: `auto`, follows OS)
- `--title TEXT` — document title (default: inferred from first `# heading`)
- `--no-mermaid` — skip inlining Mermaid runtime (saves ~200 KB)
- `--no-toc` — skip table of contents

## What gets auto-detected (Layer 3)

Each detector scans the input and reports a confidence score; high enough,
its transformations are applied. Detectors are additive — multiple can fire.

| Pattern | Trigger | Effect |
|---|---|---|
| **Mermaid** | ` ```mermaid` fences | Rendered as inline SVG diagrams |
| **Task lists** | `- [ ]` / `- [x]` items | Progress bar + clickable (session-persistent) |
| **OpenSpec BDD** | `### Requirement:` + `**WHEN**`/`**THEN**` | Side-by-side scenario cards |
| **OpenSpec delta** | `## ADDED` / `## MODIFIED` / `## REMOVED` | Green/amber/red section banners |
| **ADR** | `## Status`, `## Context`, `## Decision`, `## Consequences` | Status badge + structured layout |

## Workflow Claude follows

1. Read this SKILL.md (you're doing it now)
2. Look at the input — is it one file or a folder?
3. Run `python scripts/render.py <input> -o /mnt/user-data/outputs/<name>.html`
4. Call `present_files` with the output path

That's it. The script handles parsing, detection, enhancement, and template
rendering. Don't hand-write HTML.

## Extending — adding a new detector

1. Create `scripts/detectors/your_pattern.py` subclassing `Detector`
2. Implement `detect()` (returns 0–1 confidence) and `transform()` (rewrites AST)
3. Register it in `scripts/core/pipeline.py`'s `DETECTORS` list
4. Add a partial template in `templates/partials/` if you need custom rendering
5. Add CSS to `assets/style.css`, scoped under a `.detector-yourpattern` class

Detectors are deliberately independent: removing one never breaks the others.
