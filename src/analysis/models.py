"""
Data models for form analysis.

This module defines the data structures used to represent form analysis results,
violations, and severity levels.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class Severity(Enum):
    """Severity levels for form violations.

    Used to prioritize violations and determine penalty weights.
    """
    CRITICAL = "critical"  # Dangerous, must fix immediately (e.g., spine flexion)
    HIGH = "high"          # Significant form issue (e.g., depth beyond mobility)
    MEDIUM = "medium"      # Should improve (e.g., suboptimal depth)
    LOW = "low"            # Minor optimization (e.g., slight asymmetry)


@dataclass
class FormViolation:
    """Represents a single form rule violation.

    Attributes:
        rule_name: Identifier for the rule that was violated
        severity: How severe the violation is
        passed: Whether the rule passed (True) or failed (False)
        score_penalty: Raw points to deduct from score (0-100)
        feedback: Human-readable message explaining the issue
        frames: Optional list of frame indices where violation occurred
        details: Optional dict with additional data (angle values, etc.)

    Example:
        violation = FormViolation(
            rule_name="spine_neutral",
            severity=Severity.CRITICAL,
            passed=False,
            score_penalty=30,
            feedback="Lower back rounding detected - maintain neutral spine",
            frames=[45, 46, 47],
            details={'max_change': 15.2, 'threshold': 12.0}
        )
    """
    rule_name: str
    severity: Severity
    passed: bool
    score_penalty: int
    feedback: str
    frames: Optional[List[int]] = None
    details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate data after initialization."""
        if not 0 <= self.score_penalty <= 100:
            raise ValueError(f"score_penalty must be 0-100, got {self.score_penalty}")


@dataclass
class FormResult:
    """Overall form analysis result for a squat video.

    Attributes:
        score: Overall score from 0-100
        violations: List of all violations found
        passed: Whether form is acceptable overall (typically score >= 70)
        feedback_summary: Top 3-5 prioritized feedback items
        details: Additional information (summary message, metrics, etc.)

    Example:
        result = FormResult(
            score=75,
            violations=[violation1, violation2],
            passed=True,
            feedback_summary=[
                "Good depth - thigh parallel to floor",
                "Minor back rounding at bottom - reduce depth slightly"
            ],
            details={
                'summary': 'Good form with room for improvement',
                'num_critical': 0,
                'num_high': 1
            }
        )
    """
    score: int
    violations: List[FormViolation]
    passed: bool
    feedback_summary: List[str]
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate data after initialization."""
        if not 0 <= self.score <= 100:
            raise ValueError(f"score must be 0-100, got {self.score}")

    def get_critical_violations(self) -> List[FormViolation]:
        """Get only critical severity violations."""
        return [v for v in self.violations if v.severity == Severity.CRITICAL and not v.passed]

    def get_failed_violations(self) -> List[FormViolation]:
        """Get all violations that failed (passed=False)."""
        return [v for v in self.violations if not v.passed]

    def has_critical_issues(self) -> bool:
        """Check if there are any critical violations."""
        return len(self.get_critical_violations()) > 0
