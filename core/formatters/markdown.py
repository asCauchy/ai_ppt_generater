from .base import BaseFormatter


class MarkdownFormatter(BaseFormatter):

    file_extension = ".md"

    def format(self, ppt_data):
        meta = ppt_data.get("meta", {})
        lines = [
            f"# {meta.get('title', 'PPT 结构')}",
            "",
        ]

        subtitle = meta.get("subtitle", "")
        style = meta.get("style", "")
        if subtitle or style:
            parts = []
            if subtitle:
                parts.append(subtitle)
            if style:
                parts.append(f"风格：{style}")
            lines.append(f"> {'  |  '.join(parts)}")
            lines.append("")

        for slide in ppt_data.get("slides", []):
            idx = slide.get("index", "")
            n_role = slide.get("narrative_role", "")
            title = slide.get("title", "")
            subtitle = slide.get("subtitle", "")

            role_badge = f"[{n_role}]" if n_role else ""
            lines.append(f"## 第{idx}页：{title} {role_badge}")
            lines.append("")
            if subtitle:
                lines.append(f"> {subtitle}")
                lines.append("")

            content = slide.get("content", {})
            if isinstance(content, dict):
                lead = content.get("lead", "")
                points = content.get("points", [])
                vis_desc = content.get("visual_description", "")
                if lead:
                    lines.append(f"**{lead}**")
                    lines.append("")
                if points:
                    for p in points:
                        lines.append(f"- {p}")
                    lines.append("")
                if vis_desc:
                    lines.append(f"*配图：{vis_desc}*")
                    lines.append("")
            elif isinstance(content, str) and content:
                lines.append("### 核心内容")
                for line in content.split("\n"):
                    line = line.strip()
                    if line:
                        lines.append(f"- {line}")
                lines.append("")

            notes = slide.get("notes", {})
            if isinstance(notes, dict):
                speaker = notes.get("speaker_notes", "")
                if speaker:
                    lines.append(f"> 演讲提示：{speaker}")
                    lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)
