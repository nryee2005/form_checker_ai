"""
Scoring algorithm for squat form analysis
"""
from typing import List, Dict
from .models import FormViolation, Severity

# Penalty weights by severity level
SEVERITY_WEIGHTS = {
    Severity.CRITICAL: 1.5,
    Severity.HIGH: 1.2,
    Severity.MEDIUM: 1.0,
    Severity.LOW: 0.5
}

# Minimum score to pass
PASSING_SCORE = 70


def calculate_score(violations: List[FormViolation]) -> int:
    """Calculate overall form score from 0-100.

    Starts at 100 (perfect) and deducts weighted penalties for each violation.
    Critical violations are penalized more heavily than low severity ones.

    Args:
        violations (List[FormViolation]): List of form violations from rule evaluation

    Returns:
        int: Score from 0-100 (90-100: excellent, 75-89: good, 60-74: fair, <60: poor)
    """
    score = 100

    # Deduct weighted penalties for failed rules
    for violation in violations:
        if not violation.passed:
            weight = SEVERITY_WEIGHTS[violation.severity]
            penalty = violation.score_penalty * weight
            score -= penalty

    # Clamp to valid range
    return max(0, min(100, int(score)))


def get_score_grade(score: int) -> str:
    """Convert numerical score to letter grade.

    Args:
        score (int): Score from 0-100

    Returns:
        str: Letter grade (A, B, C, D, or F)
    """
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'


def is_passing(score: int) -> bool:
    """Check if score meets passing threshold.

    Args:
        score (int): Score from 0-100

    Returns:
        bool: True if score >= 70
    """
    return score >= PASSING_SCORE


def get_score_description(score: int) -> str:
    """Get human-readable description of score.

    Args:
        score (int): Score from 0-100

    Returns:
        str: Description of form quality
    """
    if score >= 90:
        return "Excellent form"
    elif score >= 75:
        return "Good form"
    elif score >= 60:
        return "Fair form"
    elif score >= 40:
        return "Poor form - needs improvement"
    else:
        return "Dangerous form - high injury risk"


def get_violation_summary(violations: List[FormViolation]) -> Dict[str, int]:
    """Get summary statistics about violations.

    Args:
        violations (List[FormViolation]): List of violations

    Returns:
        dict: Counts by severity level
            Example: {'total': 5, 'critical': 1, 'high': 2, 'passed': 2}
    """
    summary = {
        'total': len(violations),
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'passed': 0
    }

    for violation in violations:
        if violation.passed:
            summary['passed'] += 1
        else:
            severity_name = violation.severity.value
            if severity_name in summary:
                summary[severity_name] += 1

    return summary
