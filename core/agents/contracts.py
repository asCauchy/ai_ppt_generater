"""Agent Contracts — define read/write permissions per agent.

A contract is the data-boundary contract between an agent and the Presentation State.
It declares:
  - write_paths : which dotted paths the agent is allowed to modify
  - read_paths  : which paths the agent is expected to consume (documentation)
  - required_input : user-provided fields needed at agent start

write_paths use dotted notation with wildcards:
  "slides[*].title"   → any slide's title
  "narrative_arc"     → entire sub-tree
  "runtime.history"   → append-only log
"""

AGENT_CONTRACTS = {
    "narrative_planner": {
        "write_paths": [
            "narrative_arc",
            "slides",
            "rhythm_map",
            "meta.uuid",
            "runtime.generation_stage",
            "runtime.history",
        ],
        "read_paths": [
            "meta.title",
            "meta.style",
            "context",
        ],
        "required_input": ["topic", "style", "pages", "context"],
    },

    "content_writer": {
        "write_paths": [
            # Content fill-in
            "slides[*].content.points",
            "slides[*].content.data",
            "slides[*].content.quote",
            "slides[*].content.visual_description",
            "slides[*].content.footnote",
            # Semantic enrichment
            "slides[*].presentation_role",
            "slides[*].emotional_role",
            "slides[*].semantic_tags",
            # Speaker notes
            "slides[*].notes.speaker_notes",
            # Runtime
            "runtime.generation_stage",
            "runtime.history",
        ],
        "read_paths": [
            "meta",
            "context",
            "narrative_arc",
            "rhythm_map",
            "slides[*].id",
            "slides[*].index",
            "slides[*].structural_role",
            "slides[*].narrative_role",
            "slides[*].title",
            "slides[*].subtitle",
            "slides[*].content.lead",
            "slides[*].relation_to_prev",
            "slides[*].relation_to_next",
            "slides[*].rhythm",
            "slides[*].design",
        ],
        "required_input": [],
    },

    # ---- future agents (declared, not yet implemented) ----

    "rhythm_adjuster": {
        "write_paths": [
            "rhythm_map",
            "slides[*].rhythm",
            "runtime.generation_stage",
            "runtime.history",
        ],
        "read_paths": [
            "narrative_arc",
            "context.duration",
            "slides[*].index",
            "slides[*].narrative_role",
            "slides[*].emotional_role",
            "slides[*].content.points",
        ],
        "required_input": [],
    },

    "design_stylist": {
        "write_paths": [
            "design_system",
            "slides[*].design",
            "runtime.generation_stage",
            "runtime.history",
        ],
        "read_paths": [
            "meta.style",
            "context",
            "slides[*].index",
            "slides[*].structural_role",
            "slides[*].narrative_role",
            "slides[*].emotional_role",
            "slides[*].content",
            "slides[*].rhythm",
        ],
        "required_input": [],
    },

    "animation_director": {
        "write_paths": [
            "slides[*].notes.animation_hints",
            "slides[*].rhythm.build_steps",
            "slides[*].rhythm.transition_in",
            "slides[*].rhythm.transition_out",
            "runtime.generation_stage",
            "runtime.history",
        ],
        "read_paths": [
            "slides[*].rhythm",
            "slides[*].design.layout_mode",
            "slides[*].narrative_role",
        ],
        "required_input": [],
    },
}


def get_contract(agent_name: str) -> dict:
    c = AGENT_CONTRACTS.get(agent_name)
    if c is None:
        raise KeyError(f"Unknown agent: {agent_name}. Registered: {list(AGENT_CONTRACTS)}")
    return c
