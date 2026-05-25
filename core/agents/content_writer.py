"""ContentWriter Agent — Fills content into the narrative skeleton.

Reads: slides (skeleton), narrative_arc, rhythm_map.
Writes: content.points, emotional_role, presentation_role, speaker_notes.
"""

import json

from .base import BaseAgent


class ContentWriter(BaseAgent):
    name = "content_writer"
    temperature = 0.35  # slightly higher for creative content

    def _build_user_prompt(self, state: dict, feedback: list = None) -> str:
        slides = state.get("slides", [])
        arc = state.get("narrative_arc", {})
        ctx = state.get("context", {})

        # Build a compact skeleton view for the prompt
        skeleton_lines = ["## 叙事骨架（请在此基础上填充内容）\n"]
        skeleton_lines.append(f"叙事结构：{arc.get('structure', '')}")
        skeleton_lines.append(f"Sections：{len(arc.get('sections', []))} 个\n")

        for s in slides:
            idx = s.get("index", "?")
            title = s.get("title", "")
            lead = (s.get("content") or {}).get("lead", "")
            n_role = s.get("narrative_role", "")
            s_role = s.get("structural_role", "")
            rel_prev = s.get("relation_to_prev", "")
            rel_next = s.get("relation_to_next", "")
            rhythm = s.get("rhythm", {})
            intensity = rhythm.get("intensity", 3)
            pace = rhythm.get("pace", "moderate")
            density = (s.get("design") or {}).get("density", "comfortable")

            # Point count hint based on intensity + density
            if density == "sparse" or intensity <= 2:
                pt_hint = "2-3条"
            elif density == "dense" or intensity >= 4:
                pt_hint = "5-7条"
            else:
                pt_hint = "3-5条"

            skeleton_lines.append(
                f"[{idx}] {title} | structural={s_role} narrative={n_role} | "
                f"intensity={intensity} pace={pace} density={density} | "
                f"prev={rel_prev or 'null'} next={rel_next or 'null'} | "
                f"要点数≈{pt_hint}"
            )
            if lead:
                skeleton_lines.append(f"    lead: {lead}")

        skeleton_text = "\n".join(skeleton_lines)

        prompt = f"""{skeleton_text}

## 听众与场合
- 听众：{ctx.get('audience', {}).get('profile', '通用')}
- 场合：{ctx.get('occasion', {}).get('type', '通用')}
- 正式度：{ctx.get('occasion', {}).get('formality', 'semi_formal')}

## 任务
为以上每一页填充：
1. content.points（要点列表，条数参照各页的"要点数≈"标注）
2. emotional_role（情感定位，须与 narrative_role 协调）
3. presentation_role（信息呈现形式，可选 null）
4. content.visual_description（配图语义描述）
5. notes.speaker_notes（演讲建议，可选）

## 约束
- 保持叙事连贯：每页要点服务于其 narrative_role
- 保持情感连续：不剧烈跳变
- 保持节奏：intensity 高的页内容更密集，低的更从容
- 只输出你要修改的字段（content.points、emotional_role、presentation_role 等）
- 不要覆盖 content.lead
- 用 index 标识页面

## 输出格式
{{ "slides": [{{ "index": 0, "content": {{ "points": [...] }}, "emotional_role": "...", "presentation_role": "..." }}] }}
"""

        if feedback:
            prompt += f"\n\n## 上次校验反馈\n" + "\n".join(
                f"- [{f.get('rule', '')}] {f.get('message', '')}" for f in feedback
            )

        return prompt

    def _stage_name(self) -> str:
        return "content_written"

    def _history_summary(self, diff: dict) -> str:
        slides = diff.get("slides", [])
        roles = set()
        for s in slides:
            if s.get("emotional_role"):
                roles.add(s["emotional_role"])
        return f"Filled content for {len(slides)} slides, emotional range: {sorted(roles)}"
