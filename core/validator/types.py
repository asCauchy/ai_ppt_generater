"""Shared validation types — no dependencies on other validator modules.

These types are used by both the main validator and the semantic/emotional
rule modules, so they live in a separate file to avoid circular imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ValidationIssue:
    layer: str
    rule: str
    severity: str  # "error" | "warning" | "suggestion"
    message: str
    location: str
    context: Optional[dict] = None
    suggested_fix: Optional[str] = None

    def to_dict(self):
        d = {
            "layer": self.layer,
            "rule": self.rule,
            "severity": self.severity,
            "message": self.message,
            "location": self.location,
        }
        if self.context:
            d["context"] = self.context
        if self.suggested_fix:
            d["suggested_fix"] = self.suggested_fix
        return d


@dataclass
class ValidationResult:
    valid: bool = True
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    suggestions: list[ValidationIssue] = field(default_factory=list)
    quality_score: Optional[dict] = None  # Phase P2 scoring

    def add(self, layer: str, rule: str, severity: str, message: str, location: str, context: dict = None):
        issue = ValidationIssue(layer, rule, severity, message, location, context)
        if severity == "error":
            self.errors.append(issue)
            self.valid = False
        elif severity == "warning":
            self.warnings.append(issue)
        else:
            self.suggestions.append(issue)
        return self

    def merge(self, other: "ValidationResult"):
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.suggestions.extend(other.suggestions)
        if other.errors:
            self.valid = False
        return self

    def to_dict(self):
        d = {
            "valid": self.valid,
            "errors": [i.to_dict() for i in self.errors],
            "warnings": [i.to_dict() for i in self.warnings],
            "suggestions": [i.to_dict() for i in self.suggestions],
        }
        if self.quality_score:
            d["quality_score"] = self.quality_score
        return d
