"""Presentation Quality Scoring Engine — Phase P2.

Evaluates presentation quality across 7 orthogonal dimensions using
heuristic rule aggregation. The scoring engine is an EVALUATION layer,
not a constraint layer — it produces continuous quality gradients
(0-100) rather than binary pass/fail judgments.

Design principles:
  - All heuristics are rule-based (keyword density, pattern counting, rhythm analysis)
  - No embeddings, no NLP models, no external APIs
  - Scores are calibrated to produce meaningful differentiation
  - Each dimension is independently computed, then weighted into overall
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

# Reuse validator lexicons (no new dependencies)
from .validator.lexicons.rhetorical_vocab import get_all_text, match_any
from .validator.lexicons.emotional_vocab import EMOTION_KEYWORDS, JARRING_TRANSITIONS
from .validator.lexicons.narrative_vocab import NARRATIVE_ROLE_REQUIRED


# ---------------------------------------------------------------------------
# Output types
# ---------------------------------------------------------------------------

@dataclass
class DimensionScore:
    name: str
    score: int  # 0-100
    weight: float
    contributors: list[dict] = field(default_factory=list)  # per-slide subscores

    def to_dict(self):
        return {
            "score": self.score,
            "weight": self.weight,
            "contributors": self.contributors,
        }


@dataclass
class QualityScore:
    overall: int
    dimensions: dict[str, int]

    def to_dict(self):
        return {
            "overall": self.overall,
            "dimensions": self.dimensions,
        }


# ---------------------------------------------------------------------------
# Dimension weights
# ---------------------------------------------------------------------------

DIMENSION_WEIGHTS = {
    "narrative_force": 0.20,
    "emotional_coherence": 0.15,
    "dramatic_tension": 0.15,
    "visionary_strength": 0.12,
    "audience_engagement": 0.13,
    "rhythm_dynamics": 0.13,
    "cinematic_flow": 0.12,
}


# ---------------------------------------------------------------------------
# Scoring Engine
# ---------------------------------------------------------------------------

class ScoringEngine:
    """Evaluates a Presentation State across 7 quality dimensions.

    Usage:
        engine = ScoringEngine()
        score = engine.evaluate(state)
        print(score.overall)  # 78
        print(score.dimensions["narrative_force"])  # 82
    """

    def evaluate(self, state: dict) -> QualityScore:
        """Compute full quality score for a presentation state."""
        slides = state.get("slides", [])
        n = len(slides)
        if n == 0:
            return QualityScore(overall=0, dimensions={d: 0 for d in DIMENSION_WEIGHTS})

        dims = {}
        dims["narrative_force"] = self._score_narrative_force(state)
        dims["emotional_coherence"] = self._score_emotional_coherence(state)
        dims["dramatic_tension"] = self._score_dramatic_tension(state)
        dims["visionary_strength"] = self._score_visionary_strength(state)
        dims["audience_engagement"] = self._score_audience_engagement(state)
        dims["rhythm_dynamics"] = self._score_rhythm_dynamics(state)
        dims["cinematic_flow"] = self._score_cinematic_flow(state)

        weighted = sum(
            dims[d] * DIMENSION_WEIGHTS[d]
            for d in dims
        )
        overall = round(weighted)

        return QualityScore(overall=overall, dimensions=dims)

    # ------------------------------------------------------------------
    # 1. Narrative Force (0.20)
    # ------------------------------------------------------------------

    def _score_narrative_force(self, state: dict) -> int:
        """How strongly narrative roles are realized in content.

        Components:
          - Role realization score (per-role pattern match density)
          - Escalation strength (intensity delta at escalation slides)
          - Conflict persistence (tension dimension count)
          - CTA drive (action technique count)
        """
        slides = state.get("slides", [])
        n = len(slides)
        role_scores = []

        for i, slide in enumerate(slides):
            n_role = slide.get("narrative_role", "")
            if n_role not in NARRATIVE_ROLE_REQUIRED:
                continue

            text = get_all_text(slide)
            spec = NARRATIVE_ROLE_REQUIRED[n_role]
            patterns = spec.get("patterns", {})
            min_required = spec.get("min_matches", 1)

            # Count matching pattern groups
            matched = 0
            for group, pats in patterns.items():
                if any(re.search(p, text) for p in pats):
                    matched += 1

            # Score: how many pattern groups matched vs required
            realization = min(100, int((matched / max(min_required, 1)) * 85 + 15))
            role_scores.append(realization)

        if not role_scores:
            return 50  # neutral baseline

        base = sum(role_scores) / len(role_scores)

        # Bonus: escalation strength
        escalation_bonus = 0
        for i, slide in enumerate(slides):
            if slide.get("narrative_role") == "escalation" and i > 0:
                curr = (slide.get("rhythm") or {}).get("intensity", 3)
                prev = (slides[i - 1].get("rhythm") or {}).get("intensity", 3)
                if curr > prev:
                    escalation_bonus += min(15, (curr - prev) * 7)

        # Bonus: CTA drive
        cta_bonus = 0
        for slide in slides:
            if slide.get("narrative_role") == "call_to_action":
                text = get_all_text(slide)
                techniques = sum([
                    match_any(text, [r"加入|参与|行动|开始|关注|探索"]),
                    match_any(text, [r"你|你们|大家|在座"]),
                    match_any(text, [r"！|吧|请|让|必须|现在.*就是"]),
                ])
                cta_bonus += techniques * 5

        return min(100, round(base + escalation_bonus + cta_bonus))

    # ------------------------------------------------------------------
    # 2. Emotional Coherence (0.15)
    # ------------------------------------------------------------------

    def _score_emotional_coherence(self, state: dict) -> int:
        """How consistent the emotional journey is.

        Components:
          - Emotional state alignment (emotional_role vs rhythm.emotional_state)
          - Emotional continuity (adjacent transitions)
          - Emotional progression (has emotional arc shape)
        """
        slides = state.get("slides", [])
        n = len(slides)

        # Alignment score: how many slides have matching emotional_role vs rhythm
        aligned = 0
        total = 0
        for slide in slides:
            e_role = slide.get("emotional_role", "")
            r_state = (slide.get("rhythm") or {}).get("emotional_state", "")
            if e_role and r_state:
                total += 1
                if e_role == r_state:
                    aligned += 1

        alignment_score = int((aligned / max(total, 1)) * 100) if total > 0 else 60

        # Continuity score: how many adjacent transitions are smooth
        jarring_count = 0
        for i in range(1, n):
            prev_e = slides[i - 1].get("emotional_role", "")
            curr_e = slides[i].get("emotional_role", "")
            if (prev_e, curr_e) in JARRING_TRANSITIONS:
                jarring_count += 1

        continuity_score = max(0, 100 - jarring_count * 15)

        # Progression score: does the emotional arc have a shape?
        emotions = []
        for slide in slides:
            e = slide.get("emotional_role", "") or (slide.get("rhythm") or {}).get("emotional_state", "")
            if e:
                emotions.append(e)

        unique_emotions = len(set(emotions))
        progression_score = min(100, unique_emotions * 15 + 30) if unique_emotions > 0 else 40

        return round((alignment_score * 0.4 + continuity_score * 0.35 + progression_score * 0.25))

    # ------------------------------------------------------------------
    # 3. Dramatic Tension (0.15)
    # ------------------------------------------------------------------

    def _score_dramatic_tension(self, state: dict) -> int:
        """How well the presentation builds and releases dramatic tension.

        Components:
          - Intensity curve shape quality
          - Stakes language density
          - Tension persistence
          - Release payoff
        """
        slides = state.get("slides", [])
        n = len(slides)

        # Intensity curve: does it have a classic peak shape?
        intensities = []
        for slide in slides:
            intensity = (slide.get("rhythm") or {}).get("intensity", 3)
            intensities.append(intensity or 3)

        max_intensity = max(intensities) if intensities else 3
        max_pos = intensities.index(max_intensity) if max_intensity in intensities else 0

        # Classic shape: peak should be around 60-80% of the way through
        peak_position_ratio = max_pos / max(n - 1, 1)
        ideal_peak = 0.65
        peak_quality = max(0, 100 - abs(peak_position_ratio - ideal_peak) * 120)

        # Curve quality: rising then falling
        rising = all(
            intensities[i] <= intensities[i + 1]
            for i in range(max_pos)
        ) if max_pos > 0 else True
        falling = all(
            intensities[i] >= intensities[i + 1]
            for i in range(max_pos, n - 1)
        ) if max_pos < n - 1 else True
        curve_quality = 80 if (rising and falling) else 40 if (rising or falling) else 20

        # Stakes density: tension keywords per slide
        total_stakes = 0
        for slide in slides:
            text = get_all_text(slide)
            stakes_count = len(re.findall(
                r"危机|风险|威胁|危险|如果.*不|一旦|否则|后果|代价|损失|封锁|制裁|缺口|落后|差距",
                text
            ))
            total_stakes += min(stakes_count, 10)

        stakes_density = min(100, int(total_stakes / max(n, 1) * 15))

        # Release payoff: does the release slide exist and have resolution language?
        release_score = 50
        for slide in slides:
            if slide.get("narrative_role") == "release":
                text = get_all_text(slide)
                resolution_count = len(re.findall(
                    r"解决|缓解|改善|恢复|化解|消除|克服|突破|转机|出路|希望|曙光",
                    text
                ))
                release_score = min(100, 40 + resolution_count * 15)

        tension_score = round(
            peak_quality * 0.25 +
            curve_quality * 0.25 +
            stakes_density * 0.30 +
            release_score * 0.20
        )
        return tension_score

    # ------------------------------------------------------------------
    # 4. Visionary Strength (0.12)
    # ------------------------------------------------------------------

    def _score_visionary_strength(self, state: dict) -> int:
        """How compelling the future vision is.

        Components:
          - Future orientation density
          - Scale/magnitude language
          - Long-term framing
          - Transformational framing
        """
        slides = state.get("slides", [])
        vision_slides = [s for s in slides if s.get("narrative_role") == "vision"]
        all_slides_text = " ".join(get_all_text(s) for s in slides)

        # Future keywords across all slides
        future_count = len(re.findall(
            r"未来|十年|下.*阶段|即将|将会|必将|有望|预计|前景|蓝图|愿景|下一[步个阶段]|趋势",
            all_slides_text
        ))
        future_density = min(100, future_count * 5)

        # Scale language
        scale_count = len(re.findall(
            r"全球|世界|万亿|千亿|百亿|亿级|亿人|全国|全产业|全行业|颠覆|革命",
            all_slides_text
        ))
        scale_score = min(100, scale_count * 8)

        # Long-term framing
        longterm_count = len(re.findall(
            r"十年|二十年|长期|长远|战略|趋势|方向|路径|路线图|2030|2035|21世纪",
            all_slides_text
        ))
        longterm_score = min(100, longterm_count * 15)

        # Transformational framing
        transform_count = len(re.findall(
            r"变革|重塑|重新定义|改写|洗牌|颠覆|突破|跃迁|开创|全新|前所未有",
            all_slides_text
        ))
        transform_score = min(100, transform_count * 8)

        # Vision slide specific bonus
        vision_bonus = 0
        for vs in vision_slides:
            text = get_all_text(vs)
            if match_any(text, [r"未来", r"十年", r"将会", r"有望", r"蓝图", r"愿景"]):
                vision_bonus += 15
            if match_any(text, [r"可能", r"潜力", r"空间", r"机会"]):
                vision_bonus += 10

        return min(100, round(
            future_density * 0.30 +
            scale_score * 0.25 +
            longterm_score * 0.25 +
            transform_score * 0.20 +
            vision_bonus
        ))

    # ------------------------------------------------------------------
    # 5. Audience Engagement (0.13)
    # ------------------------------------------------------------------

    def _score_audience_engagement(self, state: dict) -> int:
        """How engaging the content is for the audience.

        Components:
          - Rhetorical question density
          - Contrast pattern density
          - Curiosity/surprise triggers
          - Direct audience address
        """
        slides = state.get("slides", [])
        n = len(slides)

        total_questions = 0
        total_contrasts = 0
        total_surprises = 0
        total_address = 0

        for slide in slides:
            text = get_all_text(slide)
            total_questions += len(re.findall(r"[？?]|吗[？?]?|呢[？?]?", text))
            total_contrasts += len(re.findall(
                r"不是.*而是|曾经.*现在|从.*到.*的|不再是|原以为.*事实上|看似.*实则|虽然.*但是",
                text
            ))
            total_surprises += len(re.findall(
                r"竟然|没想到|竟然|原以为|颠覆|重新定义|前所未有|史无前例|全球第一|世界最大",
                text
            ))
            # Audience address: "你", "你们", "大家", "在座"
            total_address += len(re.findall(r"你|你们|大家|在座|各位", text))

        question_density = min(100, int(total_questions / max(n, 1) * 25))
        contrast_density = min(100, int(total_contrasts / max(n, 1) * 30))
        surprise_density = min(100, int(total_surprises / max(n, 1) * 25))
        address_density = min(100, int(total_address / max(n, 1) * 8))

        return round(
            question_density * 0.25 +
            contrast_density * 0.30 +
            surprise_density * 0.25 +
            address_density * 0.20
        )

    # ------------------------------------------------------------------
    # 6. Rhythm Dynamics (0.13)
    # ------------------------------------------------------------------

    def _score_rhythm_dynamics(self, state: dict) -> int:
        """How dynamic and well-paced the presentation rhythm is.

        Components:
          - Pace variation
          - Strategic pause placement
          - Climax quality
          - Breathing room
        """
        slides = state.get("slides", [])
        n = len(slides)

        # Pace variation
        paces = []
        for slide in slides:
            pace = (slide.get("rhythm") or {}).get("pace", "moderate")
            paces.append(pace)
        unique_paces = len(set(paces))
        pace_variation = min(100, unique_paces * 35)

        # Strategic pause placement
        pause_slides = []
        for i, slide in enumerate(slides):
            if (slide.get("rhythm") or {}).get("pause_after"):
                n_role = slide.get("narrative_role", "")
                # Good pause positions: after conflict, escalation, insight, climax
                is_strategic = n_role in ("conflict", "escalation", "insight", "release", "call_to_action")
                pause_slides.append({"index": i, "strategic": is_strategic})

        strategic_pauses = sum(1 for p in pause_slides if p["strategic"])
        total_pauses = len(pause_slides)
        pause_quality = min(100, int(
            (strategic_pauses / max(total_pauses, 1)) * 70 +
            min(total_pauses, 4) * 7.5
        )) if total_pauses > 0 else 40

        # Climax quality: max intensity value
        intensities = []
        for slide in slides:
            intensity = (slide.get("rhythm") or {}).get("intensity", 3)
            intensities.append(intensity or 3)
        max_intensity = max(intensities) if intensities else 3
        climax_score = min(100, max_intensity * 20)

        # Breathing room: distance between high-intensity slides
        high_intensity_positions = [
            i for i, v in enumerate(intensities) if v >= 4
        ]
        breathing_score = 50
        if len(high_intensity_positions) >= 2:
            gaps = [
                high_intensity_positions[i + 1] - high_intensity_positions[i]
                for i in range(len(high_intensity_positions) - 1)
            ]
            avg_gap = sum(gaps) / len(gaps) if gaps else 1
            # Ideal gap: 1-2 slides between high-intensity slides
            breathing_score = max(30, min(100, int(100 - abs(avg_gap - 1.5) * 30)))
        elif len(high_intensity_positions) == 1:
            breathing_score = 70  # single peak is fine

        return round(
            pace_variation * 0.25 +
            pause_quality * 0.30 +
            climax_score * 0.25 +
            breathing_score * 0.20
        )

    # ------------------------------------------------------------------
    # 7. Cinematic Flow (0.12)
    # ------------------------------------------------------------------

    def _score_cinematic_flow(self, state: dict) -> int:
        """How well the presentation flows like a cinematic story.

        Components:
          - Transition consistency
          - Emotional momentum
          - Section progression
          - Echo/callback presence
        """
        slides = state.get("slides", [])
        n = len(slides)
        arc = state.get("narrative_arc", {})
        sections = arc.get("sections", [])

        # Transition consistency: do relations form a coherent chain?
        transitions = []
        for slide in slides:
            rel = slide.get("relation_to_next", "")
            if rel:
                transitions.append(rel)

        # Prefer varied but non-random transitions
        unique_transitions = len(set(transitions))
        transition_score = min(100, unique_transitions * 20 + 30) if transitions else 40

        # Emotional momentum: cumulative emotional intensity
        emotional_weights = {
            "curious": 2, "focused": 3, "engaged": 4, "impressed": 5,
            "convinced": 6, "confident": 6, "surprised": 7, "excited": 8,
            "concerned": 5, "skeptical": 4, "inspired": 8, "hopeful": 6,
            "determined": 7, "motivated": 8, "reflective": 3,
        }
        momentum = 0
        prev_weight = 0
        for slide in slides:
            e_role = slide.get("emotional_role", "") or (slide.get("rhythm") or {}).get("emotional_state", "")
            weight = emotional_weights.get(e_role, 4)
            if weight > prev_weight:
                momentum += 1  # building
            prev_weight = weight
        momentum_score = min(100, int(momentum / max(n, 1) * 80 + 20))

        # Section progression: does arc_role ordering follow expected patterns?
        arc_roles = [s.get("arc_role", "") for s in sections]
        expected = ["起", "承", "转", "合"]
        order_score = 50
        if arc_roles:
            matches = 0
            for i, role in enumerate(arc_roles):
                if i < len(expected) and role == expected[i]:
                    matches += 1
            order_score = min(100, matches * 25)

        # Echo/callback: do semantic_tags or narrative_roles recur?
        roles_seen = set()
        echoes = 0
        for slide in slides:
            n_role = slide.get("narrative_role", "")
            if n_role in roles_seen and n_role not in ("content", "evidence"):
                echoes += 1
            roles_seen.add(n_role)
        echo_score = min(100, echoes * 20 + 30)

        return round(
            transition_score * 0.25 +
            momentum_score * 0.30 +
            order_score * 0.25 +
            echo_score * 0.20
        )


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def score_presentation(state: dict) -> QualityScore:
    """One-liner: evaluate presentation quality from state."""
    engine = ScoringEngine()
    return engine.evaluate(state)
