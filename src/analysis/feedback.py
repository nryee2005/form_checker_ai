"""
Feedback generation for squat form analysis
"""

from typing import List
from .models import FormViolation, Severity

# Maximum feedback items to show
MAX_FEEDBACK_ITEMS = 5

# Severity ordering for prioritization
SEVERITY_ORDER = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3
}


def generate_feedback(violations: List[FormViolation], max_items: int = MAX_FEEDBACK_ITEMS) -> List[str]:
    """Generate prioritized feedback from violations

    Filters to failed violations, sorts by severity, and returns top N messages

    Args:
        violations (List[FormViolation]): All form violations
        max_items (int): Maximum feedback items to return (default 5)

    Returns:
        List[str]: Prioritized feedback messages
    """

    # Filter to only failed violations
    failed = [v for v in violations if not v.passed]

    if not failed:
        return []

    # Sort by severity (critical first)
    sorted_violations = sorted(failed, key=lambda v: SEVERITY_ORDER[v.severity])

    # Take top N and extract feedback
    top_violations = sorted_violations[:max_items]
    feedback = [v.feedback for v in top_violations]

    return feedback


def generate_summary(violations: List[FormViolation], score: int) -> str:
    """Generate overall summary message

    Args:
        violations (List[FormViolation]): All violations
        score (int): Overall form score (0-100)

    Returns:
        str: Summary message based on score and critical violations
    """

    # Check for critical safety issues
    critical_violations = [v for v in violations if v.severity == Severity.CRITICAL and not v.passed]

    if critical_violations:
        return 'Critical safety issues detected - address immediately'

    # Score-based summary
    if score >= 90:
        return 'Excellent form! Keep it up.'
    elif score >= 75:
        return 'Good form with room for improvement.'
    elif score >= 60:
        return 'Fair form - address the issues below.'
    else:
        return 'Form needs significant improvement for safety.'


def generate_positive_feedback(violations: List[FormViolation]) -> List[str]:
    """Generate positive feedback for aspects that passed

    Args:
        violations (List[FormViolation]): All violations

    Returns:
        List[str]: Positive feedback messages (limited to 3)
    """

    passed = [v for v in violations if v.passed]

    if not passed:
        return []

    # Take up to 3 positive items
    positive_messages = [v.feedback for v in passed[:3]]

    return positive_messages


def format_feedback_numbered(feedback: List[str]) -> List[str]:
    """Add numbering to feedback list

    Args:
        feedback (List[str]): List of feedback strings

    Returns:
        List[str]: Numbered feedback
    """

    return [f'{i+1}. {item}' for i, item in enumerate(feedback)]


def categorize_feedback(violations: List[FormViolation]) -> dict:
    """Group feedback by severity category

    Args:
        violations (List[FormViolation]): All violations

    Returns:
        dict: Categorized feedback
    """

    categorized = {
        'critical_issues': [],
        'improvements': [],
        'optimizations': []
    }

    for violation in violations:
        if violation.passed:
            continue

        if violation.severity == Severity.CRITICAL:
            categorized['critical_issues'].append(violation.feedback)
        elif violation.severity in [Severity.HIGH, Severity.MEDIUM]:
            categorized['improvements'].append(violation.feedback)
        else:
            categorized['optimizations'].append(violation.feedback)

    return categorized
