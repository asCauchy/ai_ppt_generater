"""Style Family Manifest — defines what makes a family a coherent visual civilization.

A family is NOT a theme. A theme is a color swap. A family is:
  - A complete philosophical position on visual communication
  - A bounded aesthetic vocabulary with explicit inclusions and exclusions
  - A lineage of parent traditions it draws from
  - An emotional range it can express authentically

The manifest is the constitution of a style family. Every pack in the
family must conform to it.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AestheticVocabulary:
    """The allowed and forbidden aesthetic tokens within a family."""
    surfaces: list[str] = field(default_factory=list)
    motion: list[str] = field(default_factory=list)
    typography: list[str] = field(default_factory=list)
    depth: list[str] = field(default_factory=list)
    spacing: list[str] = field(default_factory=list)
    color_mood: list[str] = field(default_factory=list)
    transitions: list[str] = field(default_factory=list)


@dataclass
class EmotionalRange:
    """The emotional register a family can authentically express."""
    primary: list[str] = field(default_factory=list)
    secondary: list[str] = field(default_factory=list)
    avoid: list[str] = field(default_factory=list)


@dataclass
class FamilyManifest:
    """Complete family identity definition.

    This is the constitution. Every style pack in this family must
    conform to the vocabulary, principles, and emotional range defined here.
    """
    family_name: str = ""
    version: str = "1.0"
    philosophy: str = ""

    core_principles: list[str] = field(default_factory=list)
    aesthetic_vocabulary: AestheticVocabulary = field(default_factory=AestheticVocabulary)
    forbidden_patterns: list[str] = field(default_factory=list)
    parent_traditions: list[str] = field(default_factory=list)
    emotional_range: EmotionalRange = field(default_factory=EmotionalRange)

    # Isolation metadata
    isolated: bool = True
    cross_family_inheritance_allowed: bool = False
    description: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> FamilyManifest:
        vocab = d.get("aesthetic_vocabulary", {})
        emo = d.get("emotional_range", {})

        return cls(
            family_name=d.get("family_name", ""),
            version=d.get("version", "1.0"),
            philosophy=d.get("philosophy", ""),
            core_principles=d.get("core_principles", []),
            aesthetic_vocabulary=AestheticVocabulary(
                surfaces=vocab.get("surfaces", []),
                motion=vocab.get("motion", []),
                typography=vocab.get("typography", []),
                depth=vocab.get("depth", []),
                spacing=vocab.get("spacing", []),
                color_mood=vocab.get("color_mood", []),
                transitions=vocab.get("transitions", []),
            ),
            forbidden_patterns=d.get("forbidden_patterns", []),
            parent_traditions=d.get("parent_traditions", []),
            emotional_range=EmotionalRange(
                primary=emo.get("primary", []),
                secondary=emo.get("secondary", []),
                avoid=emo.get("avoid", []),
            ),
            isolated=d.get("isolated", True),
            cross_family_inheritance_allowed=d.get("cross_family_inheritance_allowed", False),
            description=d.get("description", ""),
        )

    def to_dict(self) -> dict:
        return {
            "family_name": self.family_name,
            "version": self.version,
            "philosophy": self.philosophy,
            "core_principles": self.core_principles,
            "aesthetic_vocabulary": {
                "surfaces": self.aesthetic_vocabulary.surfaces,
                "motion": self.aesthetic_vocabulary.motion,
                "typography": self.aesthetic_vocabulary.typography,
                "depth": self.aesthetic_vocabulary.depth,
                "spacing": self.aesthetic_vocabulary.spacing,
                "color_mood": self.aesthetic_vocabulary.color_mood,
                "transitions": self.aesthetic_vocabulary.transitions,
            },
            "forbidden_patterns": self.forbidden_patterns,
            "parent_traditions": self.parent_traditions,
            "emotional_range": {
                "primary": self.emotional_range.primary,
                "secondary": self.emotional_range.secondary,
                "avoid": self.emotional_range.avoid,
            },
            "isolated": self.isolated,
            "cross_family_inheritance_allowed": self.cross_family_inheritance_allowed,
            "description": self.description,
        }
