"""Generate 5 realistic debug snapshot runs with mock data."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state_manager import init_presentation_state, deep_merge
from core.debug_snapshot import DebugSnapshot

# 5 topics x styles
RUNS = [
    ("人工智能在医学教育中的应用", "学术风", 10),
    ("企业数字化转型战略与实施路径", "商务风", 8),
    ("区块链技术原理与产业落地实践", "科技风", 6),
    ("学习贯彻党的二十大精神——推进高质量发展", "党政风", 7),
    ("毕业论文答辩：基于深度学习的医学图像分割研究", "学术风", 12),
]

AUDIENCES = [
    "医学教育专业教师与教学管理人员",
    "企业CXO与数字化转型负责人",
    "技术开发者与系统架构师",
    "全体党员与干部",
    "学位论文评审专家委员会",
]

def build_narrative(topic, style, n_pages):
    """Build a plausible narrative_arc for the given params."""
    if n_pages <= 6:
        sections = [
            {"id":"sec_01","label":"问题概述","arc_role":"起","function":"context_building","slide_range":[0,0],"goal":"引入主题"},
            {"id":"sec_02","label":"核心内容","arc_role":"承","function":"analysis","slide_range":[1,n_pages-3],"goal":"展开论述"},
            {"id":"sec_03","label":"总结展望","arc_role":"合","function":"call_to_action","slide_range":[n_pages-2,n_pages-1],"goal":"收束"},
        ]
        structure = "总-分-总"
    elif n_pages <= 8:
        sections = [
            {"id":"sec_01","label":"背景与问题","arc_role":"起","function":"problem_statement","slide_range":[0,1],"goal":"建立认知"},
            {"id":"sec_02","label":"分析与证据","arc_role":"承","function":"analysis","slide_range":[2,n_pages-3],"goal":"展开论证"},
            {"id":"sec_03","label":"方案与行动","arc_role":"合","function":"solution_proposal","slide_range":[n_pages-2,n_pages-1],"goal":"收束号召"},
        ]
        structure = "问题-分析-方案"
    else:
        sections = [
            {"id":"sec_01","label":"研究概述","arc_role":"起","function":"context_building","slide_range":[0,2],"goal":"建立背景与问题"},
            {"id":"sec_02","label":"展开论述","arc_role":"承","function":"analysis","slide_range":[3,n_pages-5],"goal":"系统阐述"},
            {"id":"sec_03","label":"核心突破","arc_role":"转","function":"solution_proposal","slide_range":[n_pages-4,n_pages-3],"goal":"突出创新"},
            {"id":"sec_04","label":"总结展望","arc_role":"合","function":"recap","slide_range":[n_pages-2,n_pages-1],"goal":"收束"},
        ]
        structure = "起承转合"
    return {"structure": structure, "sections": sections}

ROLE_CHAIN = [
    ("cover", "hook", None),
    ("toc", "context", "progression"),
    ("content", "context", "progression"),
    ("content", "evidence", "deepening"),
    ("section_header", "transition", "progression"),
    ("content", "conflict", "progression"),
    ("content", "insight", "deepening"),
    ("content", "evidence", "progression"),
    ("content", "release", "progression"),
    ("content", "insight", "progression"),
    ("summary", "recap", "progression"),
    ("thanks", "call_to_action", "progression"),
]

TITLES_BY_POS = {
    0: ["封面标题", "主标题", "演示主标题", "主题名称", "××× 研究报告"],
    1: ["目录", "汇报提纲", "内容概览", "今日议程", "答辩提纲"],
    3: ["研究背景", "行业现状", "问题提出", "核心挑战", "背景与动机"],
    4: ["技术路线", "方法论", "解决方案", "关键方法", "实验设计"],
    5: ["核心发现", "数据支撑", "关键指标", "实验结果", "突破性进展"],
    6: ["案例分析", "深度解析", "实践验证", "应用场景", "落地实践"],
    7: ["创新贡献", "核心优势", "方案对比", "价值分析", "创新点总结"],
}

DESIGNS_BY_POS = {
    0: {"layout_mode":"centered","color_role":"brand","density":"sparse","media_weight":"text_only","emphasis_level":"hero"},
    1: {"layout_mode":"title_content","color_role":"primary","density":"sparse","media_weight":"text_only","emphasis_level":"normal"},
    2: {"layout_mode":"two_column","color_role":"primary","density":"comfortable","media_weight":"balanced","emphasis_level":"normal"},
    3: {"layout_mode":"title_content","color_role":"accent","density":"dense","media_weight":"balanced","emphasis_level":"highlighted"},
    4: {"layout_mode":"data_focus","color_role":"accent","density":"dense","media_weight":"visual_heavy","emphasis_level":"hero"},
    5: {"layout_mode":"grid_2x2","color_role":"secondary","density":"comfortable","media_weight":"visual_heavy","emphasis_level":"highlighted"},
}

RHYTHMS_BY_POS = {
    0: (2, "slow", 25),
    1: (2, "moderate", 15),
    3: (3, "moderate", 60),
    4: (4, "fast", 90),
    5: (5, "fast", 75),
    6: (4, "moderate", 70),
    7: (3, "moderate", 60),
    8: (2, "slow", 30),
}

# ---- Generate ----
base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "debug")
snapshot = DebugSnapshot(base_dir)

for run_idx, (topic, style, n_pages) in enumerate(RUNS, 1):
    state = init_presentation_state(topic, style, n_pages)
    state["context"]["audience"]["profile"] = AUDIENCES[run_idx - 1]
    state["context"]["duration"]["total_minutes"] = n_pages * 2

    snapshot.start_run()
    snapshot.snap_initial(state)

    # --- Agent 1: NarrativePlanner ---
    slides = []
    for i in range(n_pages):
        idx_in_chain = min(i, len(ROLE_CHAIN) - 1)
        s_role, n_role, rel = ROLE_CHAIN[idx_in_chain]
        if i == n_pages - 1:
            s_role, n_role = "thanks", "call_to_action"
        title_key = i if i < 8 else 7
        titles = TITLES_BY_POS.get(title_key, ["核心内容"])
        design = DESIGNS_BY_POS.get(i % 6, {"layout_mode":"title_content","color_role":"primary","density":"comfortable","media_weight":"balanced","emphasis_level":"normal"})
        rhythm = RHYTHMS_BY_POS.get(i % 7, (3, "moderate", 45))

        slide = {
            "id": f"slide_{i:02d}",
            "index": i,
            "structural_role": s_role,
            "narrative_role": n_role,
            "title": f"{titles[i % len(titles)]}",
            "content": {"lead": f"第{i+1}页核心陈述——{topic}的关键论点"},
            "relation_to_prev": None if i == 0 else rel,
            "relation_to_next": "progression" if i < n_pages - 1 else None,
            "rhythm": {"intensity": rhythm[0], "pace": rhythm[1], "emotional_state": "curious", "estimated_seconds": rhythm[2]},
            "design": design,
            "semantic_tags": [s_role, n_role],
            "provenance": {"generated_by": "narrative_planner_v1", "generated_at": "2026-05-20T14:30:00Z", "revised_by": []},
        }
        slides.append(slide)

    narrative = build_narrative(topic, style, n_pages)
    rhythm_map = [{"slide_index": s["index"], "intensity": s["rhythm"]["intensity"],
                   "pace": s["rhythm"]["pace"], "emotional_state": s["rhythm"].get("emotional_state", "curious")}
                  for s in slides]

    diff1 = {
        "narrative_arc": narrative,
        "slides": slides,
        "rhythm_map": rhythm_map,
        "runtime": {"generation_stage": "narrative_planned", "history": [
            {"action":"narrative_planned","agent":"narrative_planner_v1","timestamp":"2026-05-20T14:30:00Z",
             "summary": f"Planned {n_pages} slides in {len(narrative['sections'])} sections ({narrative['structure']})"}
        ]}
    }
    state = deep_merge(state, diff1)
    snapshot.snap_after_agent("narrative_planner", state)

    # --- Agent 2: ContentWriter ---
    EMOTIONS = ["curious","engaged","concerned","excited","surprised","convinced","determined","reflective","inspired"]
    content_diffs = []
    for s in slides:
        idx = s["index"]
        n_role = s["narrative_role"]
        intensity = s["rhythm"]["intensity"]
        n_pts = min(2 + intensity, 6)

        emotion_map = {"hook":"curious","context":"engaged","conflict":"concerned","evidence":"convinced",
                       "insight":"surprised","release":"determined","vision":"inspired","call_to_action":"inspired",
                       "breathing_page":"reflective","transition":"engaged","recap":"reflective","echo":"reflective"}
        emotional = emotion_map.get(n_role, "engaged")
        pres_role = "data_viz" if n_role in ("evidence","insight","conflict") else ("process" if n_role == "release" else None)

        pts = [f"要点 {j+1}：关于" + topic[:8] + f"的第{idx+1}页核心论据——{n_role}" for j in range(n_pts)]

        cdiff = {
            "index": idx,
            "content": {"points": pts, "visual_description": f"建议配图：与{n_role}语义匹配的视觉元素"},
            "emotional_role": emotional,
            "presentation_role": pres_role,
            "notes": {"speaker_notes": f"演讲提示：本页为{n_role}类型，节奏{intensity}级，注意语速控制"},
            "provenance": {"revised_by": ["content_writer_v1"]},
        }
        if pres_role == "data_viz":
            cdiff["content"]["data"] = {"metric": f"指标{idx+1}", "value": f"{50 + idx * 7}%", "source": "研究数据"}
        content_diffs.append(cdiff)

    diff2 = {
        "slides": content_diffs,
        "runtime": {"generation_stage": "content_written", "history": [
            {"action":"content_written","agent":"content_writer_v1","timestamp":"2026-05-20T14:31:00Z",
             "summary": f"Filled content for {len(content_diffs)} slides, emotional range: {len(set(c['emotional_role'] for c in content_diffs))} states"}
        ]}
    }
    state = deep_merge(state, diff2)
    snapshot.snap_after_agent("content_writer", state)

    # --- Final ---
    state["runtime"]["generation_stage"] = "complete"
    snapshot.snap_final(state)
    snapshot.write_summary([
        {"agent":"narrative_planner","errors":0,"warnings":run_idx%2,"suggestions":run_idx+1},
        {"agent":"content_writer","errors":0,"warnings":(run_idx+1)%3,"suggestions":run_idx*2},
    ])
    print(f"run_{run_idx:02d}: {topic[:20]}... ({n_pages} pages) [OK]")

print(f"\nDone: {base_dir}/")
