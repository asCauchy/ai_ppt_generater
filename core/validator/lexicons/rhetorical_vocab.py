"""Rhetorical pattern detection lexicons.

Pattern-based analysis of slide content for rhetorical structure detection.
All patterns are regex-based, designed for Chinese presentation text.
"""

import re

# ---------------------------------------------------------------------------
# Rhetorical pattern definitions
# ---------------------------------------------------------------------------

# Question patterns (rhetorical or direct)
QUESTION_PATTERNS = [
    r"吗\s*[？?]?\s*$",
    r"呢\s*[？?]?\s*$",
    r"[？?]",
    r"你想过",
    r"有没有想过",
    r"什么是",
    r"谁是",
    r"为什么",
    r"如何[做到实现突破]",
    r"多少个",
    r"多少[家人次]",
]

# Contrast / tension patterns
CONTRAST_PATTERNS = [
    r"不是.*而是",
    r"曾经.*现在",
    r"过去.*如今",
    r"从.*到.*的",
    r"不再是.*而是",
    r"原以为.*事实上",
    r"表面.*实际上",
    r"看似.*实则",
    r"虽然.*但是",
    r"不仅.*更是",
]

# Future orientation patterns
FUTURE_PATTERNS = [
    r"未来",
    r"十年",
    r"下.*阶段",
    r"即将",
    r"将会",
    r"必将",
    r"有望",
    r"预计",
    r"前景",
    r"蓝图",
    r"愿景",
    r"下一[步个阶段]",
    r"趋势",
    r"方向",
]

# Action / imperative patterns
ACTION_PATTERNS = [
    r"加入",
    r"参与",
    r"行动",
    r"开始",
    r"关注",
    r"学习",
    r"尝试",
    r"抓住",
    r"探索",
    r"！",
    r"请",
    r"让我们",
    r"必须",
    r"不要[等待犹豫错过]",
    r"现在.*就是",
    r"你.*可以",
    r"邀请",
    r"欢迎",
]

# Agenda-style opening (weak hook)
AGENDA_OPENING_PATTERNS = [
    r"^本次.*介绍",
    r"^今天.*[汇报分享介绍]",
    r"^我要.*讲",
    r"^首先.*介绍",
    r"^欢迎.*来到",
    r"^大家好",
    r"^这是.*PPT",
]

# Tension / crisis language
TENSION_PATTERNS = [
    r"危机",
    r"风险",
    r"威胁",
    r"危险",
    r"挑战",
    r"困难",
    r"瓶颈",
    r"障碍",
    r"困境",
    r"封锁",
    r"制裁",
    r"缺口",
    r"落后",
    r"差距",
    r"不足",
    r"短板",
    r"制约",
    r"如果.*不",
    r"一旦",
    r"否则",
    r"后果",
    r"代价",
    r"损失",
]

# Resolution / release language
RESOLUTION_PATTERNS = [
    r"解决",
    r"缓解",
    r"改善",
    r"恢复",
    r"化解",
    r"消除",
    r"克服",
    r"突破",
    r"转机",
    r"出路",
    r"方向",
    r"路径",
    r"希望",
    r"曙光",
]

# Generic explanation (boring) patterns
GENERIC_EXPLANATION_PATTERNS = [
    r"所谓.*就是",
    r"顾名思义",
    r"众所周知",
    r"大家知道",
    r"简单.*来说",
    r"通俗.*讲",
]

# Surprise / unexpected framing
SURPRISE_PATTERNS = [
    r"竟然",
    r"没想到",
    r"已经",
    r"原以为",
    r"事实上",
    r"颠覆",
    r"重新定义",
    r"不再",
    r"前所未有",
    r"史无前例",
    r"全球第一",
    r"世界最大",
]


def match_any(text: str, patterns: list[str]) -> bool:
    """Check if any pattern matches the text."""
    if not text:
        return False
    for pat in patterns:
        if re.search(pat, text):
            return True
    return False


def count_matches(text: str, pattern_groups: dict[str, list[str]]) -> dict[str, bool]:
    """Count which pattern groups match. Returns {group_name: matched}."""
    result = {}
    for group_name, patterns in pattern_groups.items():
        result[group_name] = any(re.search(p, text) for p in patterns)
    return result


def get_matched_patterns(text: str, patterns: list[str]) -> list[str]:
    """Return the list of patterns that matched the text."""
    matched = []
    for pat in patterns:
        if re.search(pat, text):
            matched.append(pat)
    return matched


def get_all_text(slide: dict) -> str:
    """Extract all text content from a slide for pattern matching."""
    parts = []
    parts.append(slide.get("title", "") or "")
    parts.append(slide.get("subtitle", "") or "")
    content = slide.get("content", {}) or {}
    parts.append(content.get("lead", "") or "")
    points = content.get("points", []) or []
    parts.extend(points)
    return " ".join(p for p in parts if p)
