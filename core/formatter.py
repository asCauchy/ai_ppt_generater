from .formatters import get_formatter, FORMATTERS, EXTENSIONS  # noqa: F401


class PPTFormatter:
    """向后兼容的包装器，默认使用 Markdown 格式。"""

    def __init__(self, fmt="md"):
        self._fmt = get_formatter(fmt)

    def format(self, ppt_data):
        return self._fmt.format(ppt_data)

    def save(self, content, output_dir):
        return self._fmt.save(content, output_dir)
