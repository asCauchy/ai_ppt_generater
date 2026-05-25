from .base import BaseFormatter

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:"Microsoft YaHei",sans-serif;background:#f0f2f5;color:#333;line-height:1.8}}
.container{{max-width:900px;margin:40px auto;padding:0 20px}}
.cover{{background:linear-gradient(135deg,#1a3a5c,#2d6aa0);color:#fff;padding:80px 40px;text-align:center;border-radius:12px;margin-bottom:30px}}
.cover h1{{font-size:2.4em;margin-bottom:16px}}
.cover p{{font-size:1.1em;opacity:.85}}
.slide{{background:#fff;border-radius:10px;padding:40px;margin-bottom:24px;box-shadow:0 2px 12px rgba(0,0,0,.08)}}
.slide h2{{color:#1a3a5c;border-bottom:3px solid #2d6aa0;padding-bottom:10px;margin-bottom:20px}}
.slide .type{{font-size:.8em;color:#888;font-weight:normal}}
.slide h3{{color:#555;font-size:1em;margin:16px 0 8px}}
.slide ul{{padding-left:20px}}
.slide li{{margin-bottom:6px}}
.suggestion{{background:#f8f9fa;border-left:3px solid #2d6aa0;padding:10px 16px;margin-top:12px;font-size:.9em;color:#666}}
.summary{{background:#f0f7ff;border:2px solid #2d6aa0;border-radius:10px;padding:40px;margin-bottom:24px}}
.thanks{{text-align:center;padding:60px 40px;background:#fff;border-radius:10px}}
.thanks h2{{color:#1a3a5c;font-size:2em}}
</style>
</head>
<body>
<div class="container">
{body}
</div>
</body>
</html>"""


class HTMLFormatter(BaseFormatter):

    file_extension = ".html"

    def format(self, ppt_data):
        meta = ppt_data.get("meta", {})
        title = meta.get("title", "PPT")
        slides = ppt_data.get("slides", [])

        body_parts = []
        for i, slide in enumerate(slides):
            slide_html = self._render_slide(slide, is_first=(i == 0), is_last=(i == len(slides) - 1))
            body_parts.append(slide_html)

        return TEMPLATE.format(title=title, body="\n".join(body_parts))

    def _render_slide(self, slide, is_first=False, is_last=False):
        slide_type = slide.get("type", "")
        title = slide.get("title", "")
        subtitle = slide.get("subtitle", "")
        n_role = slide.get("narrative_role", "")
        content = slide.get("content", {})
        img_sug = slide.get("image_suggestion", "")
        vis_notes = slide.get("visual_notes", "")

        # Convert dict content to displayable parts
        lead = ""
        points = []
        vis_desc = ""
        if isinstance(content, dict):
            lead = content.get("lead", "")
            points = content.get("points", [])
            vis_desc = content.get("visual_description", "")
            content_str = lead
        elif isinstance(content, str):
            content_str = content
        else:
            content_str = ""

        if is_first:
            html = f'<div class="cover"><h1>{title}</h1>'
            if subtitle:
                html += f'<p>{subtitle}</p>'
            if lead:
                html += f"<p>{lead}</p>"
            elif content_str:
                html += f"<p>{content_str.replace(chr(10), '<br>')}</p>"
            html += "</div>"
            return html

        if is_last:
            body = lead or content_str
            return f'<div class="thanks"><h2>{title}</h2><p>{body.replace(chr(10), "<br>") if isinstance(body, str) else ""}</p></div>'

        css_class = "summary" if slide_type == "summary" else "slide"
        html = f'<div class="{css_class}"><h2>{title} <span class="type">[{n_role or slide_type}]</span></h2>'

        if subtitle:
            html += f'<p style="color:#888;margin-bottom:12px">{subtitle}</p>'

        if points:
            html += "<ul>"
            for p in points:
                html += f"<li>{p}</li>"
            html += "</ul>"
        elif isinstance(content_str, str) and content_str:
            html += "<ul>"
            for line in content_str.split("\n"):
                line = line.strip()
                if line:
                    html += f"<li>{line}</li>"
            html += "</ul>"

        if vis_desc:
            html += f'<div class="suggestion">🎬 {vis_desc}</div>'
        if img_sug:
            html += f'<div class="suggestion">配图建议：{img_sug}</div>'
        if vis_notes:
            html += f'<div class="suggestion">视觉建议：{vis_notes}</div>'

        html += "</div>"
        return html
