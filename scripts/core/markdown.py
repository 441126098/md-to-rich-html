"""Markdown parser configuration with code highlighting and Mermaid hook."""

from __future__ import annotations

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound


def _highlight_code(code: str, lang: str | None, _attrs) -> str:
    """Highlight a fenced code block. Returns the *full* <pre><code>...</code></pre>."""
    if lang == "mermaid":
        # Defer to fence renderer override below.
        return ""
    try:
        lexer = get_lexer_by_name(lang) if lang else guess_lexer(code)
    except ClassNotFound:
        lexer = None
    formatter = HtmlFormatter(nowrap=False, cssclass="hl")
    if lexer is None:
        # Plain text fallback that still gets the surrounding wrapper.
        from html import escape
        return f'<pre class="hl plain"><code>{escape(code)}</code></pre>'
    return highlight(code, lexer, formatter)


def build_md() -> MarkdownIt:
    md = (
        MarkdownIt("commonmark", {"html": True, "linkify": True, "typographer": True})
        .enable(["table", "strikethrough"])
        .use(footnote_plugin)
        .use(tasklists_plugin, enabled=True)
        .use(anchors_plugin, min_level=1, max_level=4, permalink=False)
    )
    md.options["highlight"] = _highlight_code

    # Override fence renderer to special-case mermaid.
    default_fence = md.renderer.rules.get("fence")

    def fence_rule(tokens, idx, options, env):
        token: Token = tokens[idx]
        info = (token.info or "").strip()
        if info == "mermaid":
            from html import escape
            return f'<div class="mermaid">{escape(token.content)}</div>\n'
        if default_fence is not None:
            return default_fence(tokens, idx, options, env)
        # markdown-it default behavior would call highlight; we did already.
        return _highlight_code(token.content, info, None)

    md.renderer.rules["fence"] = fence_rule
    return md


def render_to_html(md: MarkdownIt, source: str) -> str:
    return md.render(source)


def get_pygments_css() -> str:
    """Return the CSS for the Pygments default style, scoped to .hl."""
    return HtmlFormatter(cssclass="hl").get_style_defs(".hl")
