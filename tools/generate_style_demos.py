"""P5 Demo Generator — Same state, different style packs.

Generates two HTML outputs from the same presentation state:
  - apple_runtime_demo.html  (Apple Minimal style)
  - chinese_macro_demo.html  (Chinese Macro style)

Proves that the style system is fully decoupled from the renderer.
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, ROOT)

from core.rendering import render_to_file
from core.style_system.style_pack_loader import StylePackLoader


def create_demo_state() -> dict:
    """Create a representative presentation state for demo purposes."""
    return {
        "meta": {
            "title": "The Future of AI",
            "style": "cinematic",
            "uuid": "demo_p5_001",
            "version": "0.1.0",
            "language": "zh-CN",
        },
        "context": {
            "audience": {"profile": "技术决策者", "knowledge_level": "advanced"},
            "occasion": {"type": "tech_conference", "formality": "semi_formal"},
            "intent": {"primary_goal": "persuade"},
            "duration": {"total_minutes": 20},
        },
        "narrative_arc": {
            "structure": "起承转合",
            "sections": [
                {"id": "s1", "label": "起：觉醒", "function": "context_building",
                 "slide_range": [0, 1], "goal": "建立认知"},
                {"id": "s2", "label": "承：证据", "function": "evidence",
                 "slide_range": [2, 3], "goal": "数据证明"},
                {"id": "s3", "label": "转：洞察", "function": "insight",
                 "slide_range": [4, 5], "goal": "认知跃迁"},
                {"id": "s4", "label": "合：号召", "function": "call_to_action",
                 "slide_range": [6, 6], "goal": "行动号召"},
            ],
        },
        "slides": [
            {
                "index": 0, "id": "slide_00",
                "narrative_role": "hook", "emotional_role": "curious",
                "structural_role": "cover", "title": "AI 的下一个十年",
                "subtitle": "从工具到伙伴",
                "content": {
                    "lead": "人工智能正在经历范式级的转变。这不仅仅是技术演进，而是文明基础设施的重构。",
                    "points": ["大模型重新定义可能性边界", "多模态融合创造新交互范式", "AI 原生应用时代已经到来"],
                    "visual_description": "深空背景，一颗光点从中心扩散为网状结构",
                },
                "rhythm": {"intensity": 3, "pace": "moderate"},
                "design": {"layout_mode": "centered", "emphasis_level": "hero"},
                "relation_to_next": "progression",
            },
            {
                "index": 1, "id": "slide_01",
                "narrative_role": "context", "emotional_role": "engaged",
                "structural_role": "overview", "title": "我们站在哪里",
                "subtitle": "2024-2026 关键转折",
                "content": {
                    "lead": "过去两年，三个关键突破重塑了整个行业格局。",
                    "points": ["Scaling Laws 持续有效，模型能力指数级增长",
                               "推理成本下降 90%，部署门槛大幅降低",
                               "开源生态繁荣，创新从实验室走向生产环境",
                               "多模态能力从实验走向产品化"],
                    "visual_description": "时间线图，标注关键里程碑节点",
                },
                "rhythm": {"intensity": 2, "pace": "slow"},
                "design": {"layout_mode": "grid", "emphasis_level": "normal"},
                "relation_to_next": "deepening",
            },
            {
                "index": 2, "id": "slide_02",
                "narrative_role": "evidence", "emotional_role": "confident",
                "structural_role": "evidence", "title": "数据不会说谎",
                "subtitle": "关键指标概览",
                "content": {
                    "lead": "让我们看看支撑这一判断的核心数据。",
                    "points": ["GPT-4 级别模型推理成本：$60/M → $0.60/M tokens",
                               "开源模型在 MMLU 基准上超越 GPT-4 (2023)",
                               "AI 编程助手采用率从 12% 升至 67%",
                               "企业 AI 支出同比增长 340%"],
                    "data": {"type": "chart", "headline": "AI 关键指标变化趋势 (2023-2025)"},
                    "visual_description": "四条上升曲线的对比图，重点标注 2024 Q3 拐点",
                },
                "rhythm": {"intensity": 3, "pace": "moderate"},
                "design": {"layout_mode": "split", "emphasis_level": "normal"},
                "relation_to_next": "elaboration",
            },
            {
                "index": 3, "id": "slide_03",
                "narrative_role": "insight", "emotional_role": "surprised",
                "structural_role": "insight", "title": "被忽视的真相",
                "subtitle": "AI 不是替代人类，而是放大人类",
                "content": {
                    "lead": "大多数讨论都聚焦在「AI 会取代什么」，但真正重要的指标是「AI 能放大什么」。",
                    "points": ["研究表明：AI 对新手生产力的提升幅度是专家的 2-3 倍",
                               "这意味着 AI 不是零和博弈，而是能力平权工具",
                               "组织最大的机会不是裁员，而是重新定义每个人的能力边界"],
                    "visual_description": "放大镜聚焦效果，左侧模糊，右侧清晰",
                },
                "rhythm": {"intensity": 4, "pace": "moderate"},
                "design": {"layout_mode": "centered", "emphasis_level": "hero"},
                "relation_to_next": "escalation",
            },
            {
                "index": 4, "id": "slide_04",
                "narrative_role": "conflict", "emotional_role": "concerned",
                "structural_role": "conflict", "title": "暗流涌动",
                "subtitle": "繁荣背后的结构性风险",
                "content": {
                    "lead": "快速发展的背后，三个风险正在累积。如果不加以应对，今天的优势可能成为明天的陷阱。",
                    "points": ["算力垄断：90% 的高端 GPU 训练能力集中在 3 家公司",
                               "数据枯竭：高质量公开文本将在 2026 年耗尽",
                               "人才虹吸：学术界向工业界的人才流失速度达到历史峰值",
                               "对齐危机：更强大的模型伴随着更复杂的对齐挑战"],
                    "visual_description": "暗色背景，三条红色裂缝从中扩散",
                },
                "rhythm": {"intensity": 4, "pace": "fast"},
                "design": {"layout_mode": "split", "emphasis_level": "normal"},
                "relation_to_next": "escalation",
            },
            {
                "index": 5, "id": "slide_05",
                "narrative_role": "escalation", "emotional_role": "determined",
                "structural_role": "escalation", "title": "不进则退",
                "subtitle": "历史的窗口期正在关闭",
                "content": {
                    "lead": "每一个技术范式转移窗口期大约为 3-5 年。我们正处于这个窗口的中段。",
                    "points": ["2025-2027 是决定未来十年 AI 格局的关键期",
                               "错过这一窗口的组织将在下一个周期被迫追赶",
                               "先行者优势在平台型技术中具有复利效应",
                               "窗口不会等待完美策略"],
                    "visual_description": "沙漏效果，上半部分沙粒正在加速流失",
                },
                "rhythm": {"intensity": 5, "pace": "fast"},
                "design": {"layout_mode": "split", "emphasis_level": "hero"},
                "relation_to_next": "emotional_shift",
            },
            {
                "index": 6, "id": "slide_06",
                "narrative_role": "call_to_action", "emotional_role": "inspired",
                "structural_role": "cta", "title": "未来由建设者定义",
                "subtitle": "你现在做的每一个选择，都在塑造十年后的世界",
                "content": {
                    "lead": "技术不会自动创造更好的未来。未来属于那些在今天就开始行动的人。",
                    "points": ["开始用 AI 重新思考你的核心业务", "投资于团队而非工具"],
                    "visual_description": "明亮背景，中心一个光点向外辐射",
                },
                "rhythm": {"intensity": 5, "pace": "slow"},
                "design": {"layout_mode": "centered", "emphasis_level": "hero"},
                "relation_to_next": "",
            },
        ],
        "design_system": {
            "palette": {"colors": {}},
            "typography": {"title_font": "system-ui", "body_font": "system-ui", "scale": []},
            "spacing_unit": 8, "corner_style": "rounded", "grid_columns": 12,
        },
        "runtime": {"generation_stage": "demo", "pipeline_version": "P5"},
    }


def main():
    output_dir = os.path.join(ROOT, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    state = create_demo_state()
    print(f"Demo state: {len(state['slides'])} slides, '{state['meta']['title']}'")

    # Verify style packs are discoverable
    loader = StylePackLoader()
    available = loader.list_packs()
    print(f"Available style packs: {available}")

    for style_name in ["apple_minimal", "chinese_macro"]:
        pack = loader.load(style_name)
        print(f"\nLoaded: {pack.name} v{pack.version}")
        print(f"  Description: {pack.description}")
        print(f"  Primary: {pack.color_system.primary}")
        print(f"  Title font: {pack.typography_system.title_font}")

        output_path = os.path.join(output_dir, f"{style_name}_runtime_demo.html")
        path = render_to_file(state, output_path, style_pack_name=style_name)
        size_kb = os.path.getsize(path) / 1024
        print(f"  Output: {path} ({size_kb:.1f} KB)")

    print(f"\nDone. Open the files to compare visual languages.")
    print(f"  apple_minimal:  {os.path.join(output_dir, 'apple_minimal_runtime_demo.html')}")
    print(f"  chinese_macro:  {os.path.join(output_dir, 'chinese_macro_runtime_demo.html')}")


if __name__ == "__main__":
    main()
