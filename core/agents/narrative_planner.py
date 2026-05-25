"""NarrativePlanner Agent — Plans the narrative skeleton.

Writes: narrative_arc, slides (skeleton only), rhythm_map.
Does NOT write: content.points, content.data, emotional_role, presentation_role.
"""

import json

from .base import BaseAgent


class NarrativePlanner(BaseAgent):
    name = "narrative_planner"
    temperature = 0.15  # lower temp for structural decisions

    def load_base_prompts(self, prompts_dir: str):
        """Optionally load shared prompt fragments (styles, rules) for context."""
        import os
        extras = []
        for fname in ["styles.txt", "rules.txt"]:
            path = os.path.join(prompts_dir, fname)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    extras.append(f.read())
        if extras:
            self._system_prompt = self._system_prompt + "\n\n## 参考风格与规则\n\n" + "\n\n".join(extras)

    def _build_user_prompt(self, state: dict, feedback: list = None) -> str:
        meta = state.get("meta", {})
        ctx = state.get("context", {})
        audience = ctx.get("audience", {})
        occasion = ctx.get("occasion", {})
        intent = ctx.get("intent", {})
        duration = ctx.get("duration", {})

        pages = len(state.get("slides", []))
        # If state has no slides yet, infer from duration (1 slide per ~2 min)
        if pages == 0:
            pages = max(5, (duration.get("total_minutes", 20) // 2))

        prompt = f"""请为以下演示设计叙事骨架。

## 用户需求
- 主题：{meta.get('title', '')}
- 风格：{meta.get('style', '')}
- 页数：{pages}

## 听众
- 画像：{audience.get('profile', '通用听众')}
- 认知水平：{audience.get('knowledge_level', 'mixed')}
- 角色：{audience.get('role', '')}

## 场合
- 类型：{occasion.get('type', 'classroom_lecture')}
- 正式度：{occasion.get('formality', 'semi_formal')}

## 意图
- 主要目标：{intent.get('primary_goal', 'inform')}
- 期望结果：{intent.get('desired_outcome', '')}

## 时长
- 总时长：{duration.get('total_minutes', 20)} 分钟

## 要求
- 生成恰好 {pages} 页的完整骨架
- narrative_arc.sections 的 slide_range 必须覆盖 0-{pages - 1}，无重叠无遗漏
- 不要填写 content.points、content.data、content.quote、emotional_role、presentation_role
"""

        if feedback:
            prompt += f"\n\n## 上次校验反馈（请修正）\n" + "\n".join(
                f"- [{f.get('rule', '')}] {f.get('message', '')}" for f in feedback
            )

        return prompt

    def _stage_name(self) -> str:
        return "narrative_planned"

    def _history_summary(self, diff: dict) -> str:
        arc = diff.get("narrative_arc", {})
        structure = arc.get("structure", "unknown")
        sections = len(arc.get("sections", []))
        slides = len(diff.get("slides", []))
        return f"Planned {slides} slides in {sections} sections ({structure})"
