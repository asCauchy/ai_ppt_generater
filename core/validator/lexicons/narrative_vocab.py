"""Narrative role vocabulary lexicons.

Each narrative_role maps to required and forbidden content patterns
in Chinese presentation language.
"""

# ---------------------------------------------------------------------------
# narrative_role → required content keywords/patterns
# ---------------------------------------------------------------------------

NARRATIVE_ROLE_REQUIRED = {
    "hook": {
        "patterns": {
            "question": [r"\?|吗\s*$|呢\s*$|你想过|有没有想过|什么是|谁是|为什么|如何"],
            "curiosity": [r"秘密|不为人知|背后|真相|颠覆|重新定义|竟然|没想到"],
            "contrast": [r"不是.*而是|曾经.*现在|过去.*如今|从.*到|不再是"],
            "tension": [r"挑战|危机|冲击|变局|重塑|改写|洗牌|淘汰"],
            "surprising_statement": [r"全球第一|世界最大|前所未有|史无前例|已经"],
        },
        "min_matches": 1,  # at least one pattern type must match
        "forbidden_patterns": [
            r"^本次.*介绍",
            r"^今天.*汇报",
            r"^我要.*讲",
            r"^首先.*介绍",
            r"^欢迎.*来到",
            r"^这是.*PPT",
            r"^我们.*开始",
            r"^大家好.*今天",
        ],
    },
    "conflict": {
        "patterns": {
            "risk": [r"风险|危机|威胁|危险|隐患"],
            "problem": [r"问题|挑战|困难|瓶颈|障碍"],
            "tension": [r"但是|然而|矛盾|冲突|对抗|差距|落后"],
            "limitation": [r"不足|缺乏|短缺|制约|受限|缺口|只.*能|仅.*能"],
            "stakes": [r"如果.*不|一旦|否则|后果|代价|损失|错过"],
        },
        "min_matches": 2,  # conflict needs at least 2 dimensions
        "forbidden_patterns": [
            r"优缺点",
            r"优势.*劣势",
            r"好处.*坏处",
            r"已经解决",
            r"不是问题",
            r"轻松应对",
        ],
    },
    "escalation": {
        "patterns": {
            "intensifying": [r"更|越|进一步|愈发|日益|不断|持续|加速|升级"],
            "raising_stakes": [r"如果.*不|后果|代价|影响.*深远|波及|扩散"],
            "deepening": [r"不仅如此|更深层|根本上|本质上|更严重|更紧迫"],
        },
        "min_matches": 1,
        "forbidden_patterns": [
            r"不过",
            r"然而.*好转",
            r"已经改善",
        ],
    },
    "release": {
        "patterns": {
            "relief": [r"解决|缓解|改善|恢复|回归|化解|消除|克服"],
            "clarity": [r"清晰|明确|方向|路径|关键.*是|答案.*在"],
            "hope": [r"希望|曙光|出路|机会|可能|未来|前景"],
            "stability": [r"稳定|持续|稳步|健康|有序|可预期"],
        },
        "min_matches": 1,
        "forbidden_patterns": [
            r"危机.*持续",
            r"问题.*严重",
            r"越来越.*差",
            r"无法解决",
        ],
    },
    "vision": {
        "patterns": {
            "future_oriented": [r"未来|十年|下.*阶段|即将|将会|必将|有望"],
            "imagination": [r"想象|蓝图|愿景|前景|可能性|新.*世界|重新.*定义"],
            "possibility": [r"可能|可以|能够|潜力|空间|机会|突破"],
            "long_term": [r"长期|长远|战略|趋势|方向|路径|路线图"],
        },
        "min_matches": 2,
        "forbidden_patterns": [
            r"目前.*现状",
            r"过去.*已经",
            r"已经.*实现",
            r"回顾",
            r"总结",
        ],
    },
    "call_to_action": {
        "patterns": {
            "action_verb": [r"加入|参与|行动|开始|关注|学习|尝试|探索|抓住"],
            "audience_direction": [r"你|你们|大家|每个人|我们.*一起|在座"],
            "imperative": [r"！|吧|请|让.*我们|必须|不要.*等待|现在.*就是"],
            "invitation": [r"邀请|欢迎|期待|希望.*你|等.*你|与你"],
        },
        "min_matches": 2,
        "forbidden_patterns": [
            r"以上就是",
            r"谢谢.*大家",
            r"汇报完毕",
            r"敬请.*指正",
            r"请.*批评",
        ],
    },
    "evidence": {
        "patterns": {
            "data": [r"\d+%|\d+亿|\d+万|\d+倍|排名|数据|统计|图表"],
            "fact": [r"事实|确实|证明|表明|显示|已经|已"],
            "comparison": [r"相比|对比|超过|高于|低于|全球|国际"],
        },
        "min_matches": 1,
        "forbidden_patterns": [],
    },
    "context": {
        "patterns": {
            "background": [r"背景|现状|目前|当前|过去|历史|从.*以来"],
            "overview": [r"概览|总览|全景|框架|结构|维度|角度|方面"],
        },
        "min_matches": 1,
        "forbidden_patterns": [],
    },
    "insight": {
        "patterns": {
            "reframing": [r"不是.*而是|本质|根本上|更.*是|真正的|核心.*在于"],
            "deeper_meaning": [r"意味着|代表|象征|说明.*问题|背后.*逻辑"],
            "new_perspective": [r"换个.*角度|从.*看|如果.*看|更深|更广"],
        },
        "min_matches": 1,
        "forbidden_patterns": [
            r"首先.*其次",
            r"第一.*第二",
            r"优点.*缺点",
        ],
    },
    "recap": {
        "patterns": {
            "synthesis": [r"回顾|总结|核心|关键|三大|综上|归根|本质上"],
            "reinforcement": [r"再次|强调|敲黑板|记住|最重要|别忘了"],
        },
        "min_matches": 1,
        "forbidden_patterns": [
            r"接下来",
            r"下面",
            r"新的.*内容",
        ],
    },
}

# ---------------------------------------------------------------------------
# Structural role → expected location / forbidden location
# ---------------------------------------------------------------------------

STRUCTURAL_ROLE_CONSTRAINTS = {
    "cover": {
        "expected_positions": [0],
        "forbidden_narrative_roles": ["call_to_action", "recap", "release"],
    },
    "toc": {
        "expected_positions": [1],
        "forbidden_narrative_roles": ["call_to_action", "vision", "release"],
    },
    "thanks": {
        "expected_positions": [-1],  # -1 = last slide
        "forbidden_narrative_roles": ["hook", "conflict", "evidence"],
    },
    "summary": {
        "expected_positions": [-2, -1],
        "forbidden_narrative_roles": ["hook", "context", "escalation"],
    },
}
