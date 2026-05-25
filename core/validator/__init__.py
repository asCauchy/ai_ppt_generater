"""Presentation State Machine Validator — Kernel Constraint Layer.

Validates a Presentation State (not a PPT JSON) across 5 orthogonal layers:
  L1 - Structure    : narrative arc coverage, section ordering, slide continuity
  L2 - Semantic     : role compatibility, placement constraints, type coherence,
                      narrative role presence checks, emotional alignment checks
  L3 - Relation     : bidirectional consistency, transition legality
  L4 - Rhythm       : intensity curve smoothness, timing, emotional arc
  L5 - Design       : density/layout/media compatibility, token coherence

Outputs structured ValidationResult with hard-errors / soft-warnings / suggestions.
"""

from __future__ import annotations

import json

# Shared types
from .types import ValidationIssue, ValidationResult

# New semantic validation modules (rule-based, no NLP)
from .semantic_rules import run_all_semantic_content_checks
from .emotional_rules import run_all_emotional_checks


# ---------------------------------------------------------------------------
# Agent scope map — what each agent writes, and what must be validated after
# ---------------------------------------------------------------------------

AGENT_SCOPES = {
    "narrative_planner": ["structure", "semantic"],
    "content_writer": ["semantic"],
    "rhythm_adjuster": ["rhythm"],
    "design_stylist": ["design"],
}


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class PresentationValidator:
    """Validates a Presentation State across 5 constraint layers.

    Usage:
        v = PresentationValidator("schemas/presentation_schema.json")
        result = v.validate(state)

        # Multi-agent partial validation
        result = v.validate_for_agent(state, "rhythm_adjuster")

        # Incremental (slide range only)
        result = v.validate(state, slide_range=(0, 5))
    """

    # Pre-computed compatibility knowledge
    ARC_ORDER_RULES = {
        "起承转合": ["起", "承", "转", "合"],
        "总-分-总": ["序", "承", "合"],   # 总=序→承, 分=承, 总=合
        "问题-分析-方案": ["起", "承", "合"],
        "SCQA": ["起", "承", "转", "合"],
        "金字塔": ["序", "承", "合"],
        "英雄之旅": ["起", "承", "转", "合"],
        "对比递进": ["起", "承", "转", "合"],
    }

    # narrative_role placements that are suspicious in certain sections
    ROLE_SECTION_VIOLATIONS = {
        "hook": {"forbidden_in_last": True},        # hook 不应在最后 section
        "call_to_action": {"forbidden_in_first": True},  # CTA 不应在第一 section
        "conflict": {"forbidden_in_last": True},     # 冲突不应在结尾
        "vision": {"forbidden_in_first": True},      # 愿景不应开场就出现
    }

    # narrative_role × emotional_role rough compatibility
    # "compatible" / "neutral" / "suspect" — we warn on suspect
    NARRATIVE_EMOTIONAL_SUSPECT = {
        ("hook", "solemn"),
        ("hook", "relieved"),
        ("breathing_page", "shocked"),
        ("breathing_page", "excited"),
        ("call_to_action", "reflective"),
        ("call_to_action", "skeptical"),
        ("conflict", "relieved"),
        ("conflict", "excited"),
        ("vision", "skeptical"),
        ("vision", "concerned"),
        ("evidence", "shocked"),
    }

    # layout_mode + media_weight compatibility
    LAYOUT_MEDIA_SUSPECT = {
        ("title_content", "visual_only"),
        ("full_image", "text_only"),
        ("full_image", "text_heavy"),
        ("quote_centered", "visual_heavy"),
        ("data_focus", "visual_only"),
    }

    # Max allowed intensity jump between adjacent slides
    MAX_INTENSITY_JUMP = 2

    def __init__(self, schema_path: str):
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    # ---- public API ----

    def validate(
        self,
        state: dict,
        layers: Optional[list[str]] = None,
        slide_range: Optional[tuple[int, int]] = None,
        score: bool = True,
    ) -> ValidationResult:
        """Full or filtered validation.

        Args:
            state: Presentation State dict.
            layers: Subset of ["structure","semantic","relation","rhythm","design"].
            slide_range: (start_index, end_index) for incremental validation.
            score: If True, attach quality_score to result (Phase P2).
        """
        result = ValidationResult()
        all_layers = layers or ["structure", "semantic", "relation", "rhythm", "design"]

        # Determine whether state is partial (multi-agent mid-flight)
        stage = (state.get("runtime") or {}).get("generation_stage", "")

        for name in all_layers:
            method = getattr(self, f"_validate_{name}", None)
            if method is None:
                continue
            method(state, result, stage=stage, slide_range=slide_range)

        # Phase P2: Attach quality score
        if score and not slide_range:
            from ..scoring_engine import ScoringEngine
            engine = ScoringEngine()
            quality = engine.evaluate(state)
            result.quality_score = quality.to_dict()

        return result

    def validate_for_agent(self, state: dict, agent_name: str):
        """Validate only layers relevant to a specific agent."""
        scopes = AGENT_SCOPES.get(agent_name, ["structure", "semantic", "relation", "rhythm", "design"])
        return self.validate(state, layers=scopes)

    def validate_fast(self, state: dict) -> ValidationResult:
        """Fast-path: structure + semantic only. For runtime/incremental use."""
        return self.validate(state, layers=["structure", "semantic"])

    # ------------------------------------------------------------------
    # L1 — Structure Layer
    # ------------------------------------------------------------------

    def _validate_structure(self, state, result, **kwargs):
        L = "structure"
        slides = state.get("slides", [])
        arc = state.get("narrative_arc")
        if not arc:
            result.add(L, "S01", "error", "缺少 narrative_arc", "$.narrative_arc")
            return

        sections = arc.get("sections", [])
        if not sections:
            result.add(L, "S02", "error", "narrative_arc.sections 为空", "$.narrative_arc.sections")
            return

        n_slides = len(slides)
        covered = [False] * n_slides
        last_end = -1

        for i, sec in enumerate(sections):
            loc = f"$.narrative_arc.sections[{i}]"
            sr = sec.get("slide_range")

            if not isinstance(sr, list) or len(sr) != 2:
                result.add(L, "S03", "error", f"section[{i}] 缺少合法 slide_range", loc)
                continue

            start, end = sr[0], sr[1]

            if start < 0 or end >= n_slides:
                result.add(L, "S04", "error",
                           f"section[{i}] slide_range [{start},{end}] 越界 (共 {n_slides} 页)",
                           loc, {"slide_range": sr, "total_slides": n_slides})

            if start > end:
                result.add(L, "S05", "error",
                           f"section[{i}] slide_range 起始>{end}", loc)

            # No overlap
            if start <= last_end:
                result.add(L, "S06", "error",
                           f"section[{i}] 与前一 section 重叠 (前一段结束于 {last_end}, 本段始于 {start})",
                           loc)

            # Gap detection
            if last_end >= 0 and start > last_end + 1:
                result.add(L, "S07", "warning",
                           f"section[{i}] 与前一段之间有 {start - last_end - 1} 页间隙",
                           loc, {"gap": [last_end + 1, start - 1]})

            # Mark coverage
            for idx in range(max(0, start), min(end + 1, n_slides)):
                covered[idx] = True

            last_end = max(last_end, end)

        # Uncovered slides
        uncovered = [i for i, c in enumerate(covered) if not c]
        if uncovered:
            result.add(L, "S08", "error",
                       f"{len(uncovered)} 页未被任何 section 覆盖: indices {uncovered[:10]}",
                       "$.slides", {"uncovered": uncovered})

        # arc_role ordering
        structure_type = arc.get("structure", "custom")
        expected_order = self.ARC_ORDER_RULES.get(structure_type)
        if expected_order:
            actual_order = [s.get("arc_role", "") for s in sections]
            idx_a, idx_b = 0, 0
            for role in actual_order:
                if role in expected_order:
                    while idx_b < len(expected_order) and expected_order[idx_b] != role:
                        idx_b += 1
                    if idx_b >= len(expected_order):
                        result.add(L, "S09", "warning",
                                   f"arc_role 序列不符合 {structure_type} 模式: {actual_order}",
                                   "$.narrative_arc.sections",
                                   {"actual": actual_order, "expected_pattern": expected_order})
                        break
                    idx_a = idx_b
                # unknown roles are tolerated

    # ------------------------------------------------------------------
    # L2 — Semantic Layer
    # ------------------------------------------------------------------

    def _validate_semantic(self, state, result, **kwargs):
        L = "semantic"
        slides = state.get("slides", [])
        arc = state.get("narrative_arc")
        sections = arc.get("sections", []) if arc else []
        n = len(slides)

        if n == 0:
            return

        # Determine last section start index
        last_section_start = 0
        if sections:
            last_section_start = sections[-1].get("slide_range", [0, 0])[0]

        # Per-slide checks
        for i, slide in enumerate(slides):
            loc = f"$.slides[{i}]"
            n_role = slide.get("narrative_role", "")
            p_role = slide.get("presentation_role")
            e_role = slide.get("emotional_role")
            s_role = slide.get("structural_role", "")
            content = slide.get("content", {})
            rhythm = slide.get("rhythm", {})
            design = slide.get("design", {})

            # --- semantic legality ---

            # breathing_page must have low intensity
            if n_role == "breathing_page":
                intensity = rhythm.get("intensity", 3)
                if intensity and intensity > 2:
                    result.add(L, "M01", "warning",
                               f"breathing_page[{i}] intensity={intensity}，建议 ≤2",
                               loc, {"narrative_role": n_role, "intensity": intensity})

            # hook shouldn't be in last section
            if n_role == "hook" and i >= last_section_start:
                result.add(L, "M02", "warning",
                           f"hook[{i}] 出现在最后一个 section，hook 应在开头",
                           loc, {"narrative_role": n_role})

            # call_to_action shouldn't be in first section
            first_section_end = sections[0].get("slide_range", [0, 0])[1] if sections else 0
            if n_role == "call_to_action" and first_section_end is not None and i <= first_section_end:
                result.add(L, "M03", "warning",
                           f"call_to_action[{i}] 出现在第一个 section，CTA 应在结尾",
                           loc, {"narrative_role": n_role})

            # vision shouldn't open
            if n_role == "vision" and i <= first_section_end:
                result.add(L, "M04", "warning",
                           f"vision[{i}] 出现在第一个 section，愿景应在建立信任后提出",
                           loc)

            # conflict shouldn't end
            if n_role == "conflict" and i >= last_section_start:
                result.add(L, "M05", "warning",
                           f"conflict[{i}] 出现在最后一个 section，应以解决方案收尾",
                           loc)

            # --- role compatibility ---

            # narrative + emotional suspect pairs
            key = (n_role, e_role)
            if key in self.NARRATIVE_EMOTIONAL_SUSPECT:
                result.add(L, "M06", "suggestion",
                           f"narrative_role={n_role} + emotional_role={e_role} 组合不协调",
                           loc, {"narrative_role": n_role, "emotional_role": e_role})

            # data_viz should have content.data
            if p_role == "data_viz":
                if not content or not content.get("data"):
                    result.add(L, "M07", "warning",
                               f"presentation_role=data_viz 但 content.data 为空",
                               loc, {"presentation_role": p_role})

            # quote should have content.quote
            if p_role == "quote":
                if not content or not content.get("quote"):
                    result.add(L, "M08", "suggestion",
                               f"presentation_role=quote 建议填写 content.quote",
                               loc)

            # structural + narrative coherence
            if s_role == "cover" and n_role not in ("hook", "", None):
                result.add(L, "M09", "suggestion",
                           f"cover 页 narrative_role 建议为 hook 或空，当前为 {n_role}",
                           loc)
            if s_role == "thanks" and n_role not in ("call_to_action", "recap", "release", "", None):
                result.add(L, "M10", "suggestion",
                           f"thanks 页 narrative_role 建议为 CTA/recap/release，当前为 {n_role}",
                           loc)

        # --- Semantic Content Checks (new: narrative presence + emotional alignment) ---
        # Run content-level narrative role presence checks
        content_issues = run_all_semantic_content_checks(state)
        for issue in content_issues:
            if issue.severity == "error":
                result.errors.append(issue)
                result.valid = False
            elif issue.severity == "warning":
                result.warnings.append(issue)
            else:
                result.suggestions.append(issue)

        # Run emotional alignment checks
        emotional_issues = run_all_emotional_checks(state)
        for issue in emotional_issues:
            if issue.severity == "error":
                result.errors.append(issue)
                result.valid = False
            elif issue.severity == "warning":
                result.warnings.append(issue)
            else:
                result.suggestions.append(issue)

    # ------------------------------------------------------------------
    # L3 — Relation Layer
    # ------------------------------------------------------------------

    def _validate_relation(self, state, result, **kwargs):
        L = "relation"
        slides = state.get("slides", [])
        n = len(slides)
        if n <= 1:
            return

        for i in range(n):
            slide = slides[i]
            loc = f"$.slides[{i}]"

            rel_next = slide.get("relation_to_next")
            rel_prev = slide.get("relation_to_prev")

            # First slide: relation_to_prev should be null
            if i == 0 and rel_prev is not None:
                result.add(L, "R01", "warning",
                           f"第一页 relation_to_prev 应为 null，当前为 {rel_prev}",
                           loc, {"relation_to_prev": rel_prev})

            # Last slide: relation_to_next should be null
            if i == n - 1 and rel_next is not None:
                result.add(L, "R02", "warning",
                           f"最后一页 relation_to_next 应为 null，当前为 {rel_next}",
                           loc, {"relation_to_next": rel_next})

            # Bidirectional consistency
            if i < n - 1 and rel_next is not None:
                next_prev = slides[i + 1].get("relation_to_prev")
                if next_prev and not self._relation_compatible(rel_next, next_prev):
                    result.add(L, "R03", "warning",
                               f"页{i}→next={rel_next} 与 页{i+1}→prev={next_prev} 不一致",
                               loc, {
                                   "relation_to_next": rel_next,
                                   "next_relation_to_prev": next_prev,
                               })

            # escalation → release constraint
            if rel_next == "escalation" and i < n - 1:
                # Check if there's an explicit pivot or breathing page before release
                found_release = False
                found_pivot = False
                for j in range(i + 1, min(i + 4, n)):
                    s = slides[j]
                    if s.get("narrative_role") == "release":
                        found_release = True
                    if s.get("relation_to_prev") == "pivot" or s.get("narrative_role") in ("pivot", "breathing_page", "transition"):
                        found_pivot = True
                        break
                if found_release and not found_pivot:
                    result.add(L, "R04", "warning",
                               f"escalation(页{i}) 后直接跟 release(页{i+1}-{i+3})，建议插入 pivot 或 breathing_page",
                               loc, {"escalation_slide": i})

            # echo: previous reference should exist
            if rel_prev == "echo" and i >= 3:
                # echo should reference something from the first half
                early_slides = slides[: max(1, n // 2)]
                has_related = any(
                    s.get("narrative_role") == slides[i].get("narrative_role")
                    or any(t in (slides[i].get("semantic_tags") or []) for t in (s.get("semantic_tags") or []))
                    for s in early_slides
                )
                if not has_related:
                    result.add(L, "R05", "suggestion",
                               f"echo(页{i}) 未检测到与前半部分的主题关联",
                               loc)

    def _relation_compatible(self, a: str, b: str):
        """Check if relation_to_next (a) is compatible with relation_to_prev (b)."""
        compatible_pairs = {
            ("progression", "progression"),
            ("deepening", "deepening"),
            ("deepening", "progression"),
            ("contrast", "contrast"),
            ("example", "example"),
            ("example", "progression"),
            ("escalation", "escalation"),
            ("escalation", "progression"),
            ("recap", "recap"),
            ("pivot", "pivot"),
            ("pivot", "contrast"),
            ("echo", "echo"),
            ("emotional_shift", "emotional_shift"),
            ("emotional_shift", "contrast"),
            ("build", "build"),
            ("build", "progression"),
        }
        # Relaxed: if either refines the other, it's ok
        return (a, b) in compatible_pairs or a == b

    # ------------------------------------------------------------------
    # L4 — Rhythm Layer
    # ------------------------------------------------------------------

    def _validate_rhythm(self, state, result, **kwargs):
        L = "rhythm"
        slides = state.get("slides", [])
        rhythm_map = state.get("rhythm_map", [])
        context = state.get("context", {})
        n = len(slides)

        # rhythm_map coverage
        rm_indices = {e.get("slide_index") for e in rhythm_map}
        if len(rm_indices) != n:
            missing = [i for i in range(n) if i not in rm_indices]
            if missing:
                result.add(L, "Y01", "error",
                           f"rhythm_map 缺少 {len(missing)} 页: {missing[:10]}",
                           "$.rhythm_map", {"missing_indices": missing})

        # Per-slide rhythm checks
        prev_intensity = None
        intensities = []

        for i, slide in enumerate(slides):
            loc = f"$.slides[{i}]"
            rhythm = slide.get("rhythm", {})
            intensity = rhythm.get("intensity")
            pace = rhythm.get("pace", "")
            pause_after = rhythm.get("pause_after", False)
            est_sec = rhythm.get("estimated_seconds", 0)
            e_state = rhythm.get("emotional_state", "")

            if intensity is not None:
                intensities.append(intensity)
            else:
                intensities.append(3)  # default assumption

            # pause_after + pace coherence
            if pause_after and pace not in ("slow", "pause", ""):
                result.add(L, "Y02", "warning",
                           f"pause_after=true 但 pace={pace}，建议 pace=slow/pause",
                           loc, {"pause_after": True, "pace": pace})

            # estimated_seconds reasonableness
            if est_sec and est_sec < 10:
                result.add(L, "Y03", "warning",
                           f"estimated_seconds={est_sec} 过短(<10s)，听众来不及阅读",
                           loc)
            if est_sec and est_sec > 300:
                result.add(L, "Y04", "suggestion",
                           f"estimated_seconds={est_sec} 过长(>5min)，考虑拆分或增加交互",
                           loc)

            # Intensity jump
            if prev_intensity is not None and intensity is not None:
                jump = abs(intensity - prev_intensity)
                if jump > self.MAX_INTENSITY_JUMP:
                    result.add(L, "Y05", "warning",
                               f"页{i-1}→页{i} intensity 跳变 {prev_intensity}→{intensity} (Δ={jump})",
                               f"$.slides[{i-1}]→slides[{i}]",
                               {"jump": jump, "from": prev_intensity, "to": intensity})

            prev_intensity = intensity

        # Global intensity curve
        if intensities:
            # No climax warning
            if max(intensities) < 4:
                result.add(L, "Y06", "suggestion",
                           "全篇 intensity 最高仅 " + str(max(intensities)) + "，缺少情绪高点",
                           "$.slides[*].rhythm.intensity",
                           {"max_intensity": max(intensities)})

            # Monotone warning
            unique = len(set(intensities))
            if unique <= 1:
                result.add(L, "Y07", "suggestion",
                           "intensity 曲线完全平坦，缺乏节奏变化",
                           "$.slides[*].rhythm.intensity")

        # Total estimated time vs declared duration
        total_est = sum(
            s.get("rhythm", {}).get("estimated_seconds", 0) or 0
            for s in slides
        )
        declared_sec = (context.get("duration") or {}).get("total_minutes", 0) * 60
        if declared_sec > 0 and total_est > 0:
            ratio = total_est / declared_sec
            if ratio < 0.7:
                result.add(L, "Y08", "warning",
                           f"预估总时长({total_est}s) 远低于声明时长({declared_sec}s), ratio={ratio:.1%}",
                           "$.slides[*].rhythm.estimated_seconds",
                           {"estimated_total": total_est, "declared": declared_sec})
            elif ratio > 1.3:
                result.add(L, "Y09", "warning",
                           f"预估总时长({total_est}s) 超过声明时长({declared_sec}s), ratio={ratio:.1%}",
                           "$.slides[*].rhythm.estimated_seconds",
                           {"estimated_total": total_est, "declared": declared_sec})

        # Emotional state transitions: check for jarring adjacent states
        jarring_transitions = {
            ("solemn", "excited"),
            ("excited", "solemn"),
            ("shocked", "relieved"),
            ("concerned", "relieved"),
        }
        for i in range(1, n):
            prev_state = slides[i - 1].get("rhythm", {}).get("emotional_state", "")
            curr_state = slides[i].get("rhythm", {}).get("emotional_state", "")
            if (prev_state, curr_state) in jarring_transitions:
                result.add(L, "Y10", "suggestion",
                           f"emotional_state 突变: {prev_state} → {curr_state} (页{i-1}→{i})",
                           f"$.slides[{i-1}]→slides[{i}]",
                           {"from": prev_state, "to": curr_state})

    # ------------------------------------------------------------------
    # L5 — Design Layer
    # ------------------------------------------------------------------

    def _validate_design(self, state, result, **kwargs):
        L = "design"
        ds = state.get("design_system")
        slides = state.get("slides", [])
        n = len(slides)

        if not ds:
            result.add(L, "D01", "warning", "缺少全局 design_system", "$.design_system")
            return

        # Palette hex format
        palette = ds.get("palette", {}).get("colors", {})
        for name, color in palette.items():
            if color and not (len(color) == 7 and color[0] == "#"):
                result.add(L, "D02", "error",
                           f"颜色 {name}:{color} 不是合法 hex", f"$.design_system.palette.colors.{name}")

        # Typography scale
        scale = ds.get("typography", {}).get("scale", [])
        if len(scale) < 4:
            result.add(L, "D03", "warning",
                       f"typography.scale 仅 {len(scale)} 级，建议至少 4 级",
                       "$.design_system.typography.scale")

        # Per-slide design checks
        prev_background = None
        for i, slide in enumerate(slides):
            loc = f"$.slides[{i}]"
            design = slide.get("design", {})
            layout = design.get("layout_mode", "")
            media = design.get("media_weight", "")
            color_role = design.get("color_role", "")
            s_role = slide.get("structural_role", "")
            e_role = slide.get("emotional_role", "")
            emphasis = design.get("emphasis_level", "")

            # layout + media compatibility
            suspect_key = (layout, media)
            if suspect_key in self.LAYOUT_MEDIA_SUSPECT:
                result.add(L, "D04", "warning",
                           f"layout_mode={layout} + media_weight={media} 不兼容",
                           loc, {"layout_mode": layout, "media_weight": media})

            # color_role usage pattern
            if color_role == "brand":
                if s_role not in ("cover", "section_header", "thanks"):
                    if i > 0 and slides[i - 1].get("design", {}).get("color_role") != "brand":
                        result.add(L, "D05", "suggestion",
                                   f"brand color_role 建议仅用于 cover/section_header/thanks",
                                   loc, {"structural_role": s_role, "color_role": color_role})

            # background switch without section boundary
            bg = design.get("background", "")
            if prev_background and bg != prev_background:
                # Check if this is a section boundary
                arc = state.get("narrative_arc")
                sections = arc.get("sections", []) if arc else []
                is_boundary = any(s.get("slide_range", [])[0] == i for s in sections)
                if not is_boundary and bg and prev_background:
                    if {bg, prev_background} in ({"light", "dark"}, {"light", "brand"}, {"dark", "brand"}):
                        result.add(L, "D06", "suggestion",
                                   f"背景从 {prev_background} 切换到 {bg} (页{i-1}→{i})，建议仅在 section 边界切换",
                                   loc, {"from": prev_background, "to": bg})
            prev_background = bg

            # emphasis + emotional role synergy
            strong_emotions = {"shock", "excitement", "solemnity", "inspired"}
            if emphasis == "hero" and e_role not in strong_emotions and e_role:
                result.add(L, "D07", "suggestion",
                           f"emphasis_level=hero 但 emotional_role={e_role}，hero 更适合强烈情绪",
                           loc)
            if emphasis == "hero" and s_role == "recap":
                result.add(L, "D08", "suggestion",
                           f"recap 页不建议 emphasis_level=hero",
                           loc)

            # density + content length check (numeric, not just guess)
            content = slide.get("content", {})
            points = content.get("points", []) if content else []
            density = design.get("density", "")
            if density == "sparse" and len(points) > 5:
                result.add(L, "D09", "warning",
                           f"design.density=sparse 但 content.points 有 {len(points)} 条",
                           loc)
            if density == "dense" and len(points) < 3 and len(points) > 0:
                result.add(L, "D10", "suggestion",
                           f"design.density=dense 但 content.points 仅 {len(points)} 条",
                           loc)
