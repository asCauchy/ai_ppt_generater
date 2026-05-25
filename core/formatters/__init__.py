from .base import BaseFormatter
from .markdown import MarkdownFormatter
from .html import HTMLFormatter
from .pptx import PPTXFormatter

FORMATTERS = {
    "md": MarkdownFormatter,
    "html": HTMLFormatter,
    "pptx": PPTXFormatter,
}

EXTENSIONS = {
    "md": ".md",
    "html": ".html",
    "pptx": ".pptx",
}


def get_formatter(format_type):
    cls = FORMATTERS.get(format_type)
    if cls is None:
        raise ValueError(f"不支持的输出格式: {format_type}，可选: {list(FORMATTERS.keys())}")
    return cls()
