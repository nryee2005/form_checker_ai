"""
Pydantic schemas for API request and response models

This module defines the data models for FastAPI endpoints using Pydantic.
Pydantic models provide:
- Automatic JSON serialization/deserialization
- Request/response validation
- Auto-generated OpenAPI documentation
- Type safety at runtime

These models act as a "contract" between the API and clients, separate from
the internal dataclass models used in the analysis pipeline.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from src.analysis.models import FormResult, FormViolation


class ViolationResponse(BaseModel):
    """API response model for a single form violation

    Represents one specific form rule that was evaluated (passed or failed).
    This is the Pydantic version of the FormViolation dataclass, designed
    for JSON serialization in API responses.

    Attributes:
        rule_name (str): Unique identifier for the rule (e.g., "spine_neutral")
        severity (str): Severity level - "critical", "high", "medium", or "low"
        passed (bool): True if rule passed, False if violated
        score_penalty (int): Points deducted from score (0-100)
        feedback (str): Human-readable explanation of the violation
        frames (Optional[List[int]]): Frame numbers where violation occurred
        details (Optional[Dict[str, Any]]): Additional data like angle measurements
    """

    rule_name: str = Field(
        ...,
        description="Identifier for the violated rule",
        examples=["spine_neutral", "squat_depth", "hip_angle"]
    )

    severity: str = Field(
        ...,
        description="Severity level: critical, high, medium, or low",
        examples=["critical", "high", "medium", "low"]
    )

    passed: bool = Field(
        ...,
        description="Whether the rule passed (True) or was violated (False)"
    )

    score_penalty: int = Field(
        ...,
        ge=0,  # Greater than or equal to 0
        le=100,  # Less than or equal to 100
        description="Points deducted from overall score (0-100)"
    )

    feedback: str = Field(
        ...,
        description="Human-readable feedback message explaining the issue",
        examples=["Excessive back rounding detected at bottom of squat"]
    )

    frames: Optional[List[int]] = Field(
        None,  # None = not required, can be null
        description="List of frame numbers where violation was detected",
        examples=[[45, 67, 89]]
    )

    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional violation details like angle measurements",
        examples=[{"max_deviation": 15.3, "avg_angle": 142.7}]
    )

    class Config:
        """Pydantic model configuration

        json_schema_extra provides example data that shows up in:
        - Swagger UI (http://localhost:8000/docs)
        - ReDoc (http://localhost:8000/redoc)
        - OpenAPI spec (/openapi.json)
        """
        json_schema_extra = {
            "example": {
                "rule_name": "spine_neutral",
                "severity": "medium",
                "passed": False,
                "score_penalty": 10,
                "feedback": "Slight back rounding detected at bottom of squat",
                "frames": [45, 67, 89],
                "details": {"max_deviation": 15.3}
            }
        }


class FormResultResponse(BaseModel):
    """API response model for overall form analysis result

    Contains the complete analysis of a squat video including score,
    pass/fail status, violations, and feedback. This is the Pydantic
    version of the FormResult dataclass.

    Attributes:
        score (int): Overall form score from 0-100 (higher is better)
        passed (bool): True if form meets acceptable standards (score >= 70)
        feedback_summary (List[str]): Top 3-5 prioritized feedback items
        violations (List[ViolationResponse]): All detected form violations
        details (Dict[str, Any]): Additional metadata (frames processed, etc.)
    """

    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall form score (0-100, higher is better)",
        examples=[75]
    )

    passed: bool = Field(
        ...,
        description="Whether form meets acceptable standards (typically score >= 70)",
        examples=[True]
    )

    feedback_summary: List[str] = Field(
        ...,
        description="Top prioritized feedback items (3-5 most important points)",
        examples=[
            ["Good depth achieved on most reps", "Watch knee alignment on left side"]
        ]
    )

    violations: List[ViolationResponse] = Field(
        ...,
        description="List of all detected form violations (both passed and failed)",
        examples=[[]]  # Can be empty list if perfect form
    )

    details: Dict[str, Any] = Field(
        default_factory=dict,  # Defaults to empty dict if not provided
        description="Additional analysis details (summary text, processing stats, etc.)",
        examples=[{
            "summary": "Overall good form with minor improvements needed",
            "frames_processed": 120,
            "poses_detected": 115
        }]
    )

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "score": 75,
                "passed": True,
                "feedback_summary": [
                    "Good depth achieved on most reps",
                    "Watch knee alignment on left side"
                ],
                "violations": [
                    {
                        "rule_name": "spine_neutral",
                        "severity": "medium",
                        "passed": False,
                        "score_penalty": 10,
                        "feedback": "Slight back rounding detected",
                        "frames": [45, 67],
                        "details": {}
                    }
                ],
                "details": {
                    "summary": "Overall good form",
                    "frames_processed": 120,
                    "poses_detected": 115
                }
            }
        }


class AnalysisResponse(BaseModel):
    """Complete API response for video analysis endpoint

    Top-level response that wraps the form analysis results and
    video processing metadata. This is what the /api/analyze
    endpoint returns.

    Attributes:
        form_result (FormResultResponse): Complete form analysis results
        metadata (Dict[str, Any]): Video processing metadata (fps, resolution, etc.)
    """

    form_result: FormResultResponse = Field(
        ...,
        description="Complete form analysis results with score and violations"
    )

    metadata: Dict[str, Any] = Field(
        ...,
        description="Video processing metadata (fps, dimensions, frame counts)",
        examples=[{
            "frames_processed": 120,
            "poses_detected": 115,
            "fps": 30.0,
            "width": 1920,
            "height": 1080,
            "duration": 4.0
        }]
    )

    class Config:
        """Pydantic model configuration"""
        json_schema_extra = {
            "example": {
                "form_result": {
                    "score": 75,
                    "passed": True,
                    "feedback_summary": ["Good depth", "Watch knee alignment"],
                    "violations": [],
                    "details": {}
                },
                "metadata": {
                    "frames_processed": 120,
                    "poses_detected": 115,
                    "fps": 30.0,
                    "width": 1920,
                    "height": 1080,
                    "duration": 4.0
                }
            }
        }


def convert_form_result_to_response(form_result: FormResult) -> FormResultResponse:
    """Convert internal FormResult dataclass to API response model

    Bridges the gap between internal dataclass models (used in analysis pipeline)
    and external Pydantic models (used in API responses). Handles conversion of:
    - Dataclasses to Pydantic models
    - Enums to string values (Severity.CRITICAL → "critical")
    - Nested objects (list of FormViolation → list of ViolationResponse)

    Args:
        form_result (FormResult): Internal analysis result from analyzer.analyze_video()

    Returns:
        FormResultResponse: Pydantic model ready for JSON serialization

    Example:
        >>> from src.analysis.analyzer import analyze_video
        >>> result = analyze_video("squat.mp4")
        >>> api_response = convert_form_result_to_response(result['form_result'])
        >>> # Can now return api_response from FastAPI endpoint
    """

    # Convert each FormViolation dataclass to ViolationResponse Pydantic model
    violations_response = [
        ViolationResponse(
            rule_name=violation.rule_name,
            severity=violation.severity.value,  # Convert Enum to string ("critical")
            passed=violation.passed,
            score_penalty=violation.score_penalty,
            feedback=violation.feedback,
            frames=violation.frames,
            details=violation.details
        )
        for violation in form_result.violations
    ]

    # Build the complete Pydantic response model
    return FormResultResponse(
        score=form_result.score,
        passed=form_result.passed,
        feedback_summary=form_result.feedback_summary,
        violations=violations_response,
        details=form_result.details
    )
