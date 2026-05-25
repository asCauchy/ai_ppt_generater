from .base import BaseAgent, AgentError
from .narrative_planner import NarrativePlanner
from .content_writer import ContentWriter

AGENT_REGISTRY = {
    "narrative_planner": NarrativePlanner,
    "content_writer": ContentWriter,
    # ---- future ----
    # "rhythm_adjuster": RhythmAdjuster,
    # "design_stylist": DesignStylist,
    # "animation_director": AnimationDirector,
}


def create_agent(name: str, api_key: str = None) -> BaseAgent:
    cls = AGENT_REGISTRY.get(name)
    if cls is None:
        raise KeyError(f"Unknown agent: {name}. Available: {list(AGENT_REGISTRY)}")
    return cls(api_key=api_key)
