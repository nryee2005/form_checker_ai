"""
Data models for form analysis
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class Severity(Enum):
    """Severity levels for form violations"""

    CRITICAL = 'critical'  # Dangerous, must fix immediately
    HIGH = 'high'          # Significant form issue
    MEDIUM = 'medium'      # Should improve
    LOW = 'low'            # Minor optimization


@dataclass
class FormViolation:
    """Represents a single form rule violation

    Attributes:
        rule_name (str): Identifier for the rule that was violated
        severity (Severity): How severe the violation is
        passed (bool): Whether the rule passed or failed
        score_penalty (int): Raw points to deduct from score (0-100)
        feedback (str): Human-readable message explaining the issue
        frames (Optional[List[int]]): Frame indices where violation occurred
        details (Optional[Dict[str, Any]]): Additional data like angle values
    """

    rule_name: str
    severity: Severity
    passed: bool
    score_penalty: int
    feedback: str
    frames: Optional[List[int]] = None
    details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate data after initialization"""

        if not 0 <= self.score_penalty <= 100:
            raise ValueError(f'score_penalty must be 0-100, got {self.score_penalty}')


@dataclass
class FormResult:
    """Overall form analysis result for a squat video

    Attributes:
        score (int): Overall score from 0-100
        violations (List[FormViolation]): List of all violations found
        passed (bool): Whether form is acceptable overall
        feedback_summary (List[str]): Top prioritized feedback items
        details (Dict[str, Any]): Additional information
    """

    score: int
    violations: List[FormViolation]
    passed: bool
    feedback_summary: List[str]
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate data after initialization"""

        if not 0 <= self.score <= 100:
            raise ValueError(f'score must be 0-100, got {self.score}')

    def get_critical_violations(self) -> List[FormViolation]:
        """Get only critical severity violations

        Returns:
            List[FormViolation]: Critical violations that failed
        """

        return [v for v in self.violations if v.severity == Severity.CRITICAL and not v.passed]

    def get_failed_violations(self) -> List[FormViolation]:
        """Get all violations that failed

        Returns:
            List[FormViolation]: All violations with passed=False
        """

        return [v for v in self.violations if not v.passed]

    def has_critical_issues(self) -> bool:
        """Check if there are any critical violations

        Returns:
            bool: True if any critical violations exist
        """

        return len(self.get_critical_violations()) > 0
