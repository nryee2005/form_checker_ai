"""
Main entry point for video form analysis
"""

from typing import Dict, Any, Optional, Tuple
from src.pose.pipeline import process_video
from src.analysis.form_rules import evaluate_form
from src.analysis.scoring import calculate_score, is_passing
from src.analysis.feedback import generate_feedback, generate_summary
from src.analysis.models import FormResult


def transform_angles(angles_data: list) -> Dict[str, list]:
    """Transform per-frame angle data to per-angle lists

    Converts from pipeline format (list of dicts per frame) to
    form rules format (dict of lists per angle)

    Args:
        angles_data (list): List of dicts from process_video(), each with frame angles

    Returns:
        Dict[str, list]: Dict mapping angle names to lists of values across frames
    """

    if not angles_data:
        return {}

    # Get all angle names (exclude 'frame' key)
    angle_names = [key for key in angles_data[0].keys() if key != 'frame']

    # Build dict of lists
    transformed = {}
    for angle_name in angle_names:
        transformed[angle_name] = [
            frame_data.get(angle_name)
            for frame_data in angles_data
        ]

    return transformed


def validate_pose_visibility(pipeline_data: Dict[str, Any],
                            required_visibility: float = 0.5) -> Tuple[bool, str]:
    """Check if required landmarks (shoulders) are visible throughout video

    Validates that shoulder landmarks are detected in enough frames to
    perform accurate form analysis. For barbell squats, shoulders may be
    partially obstructed by the bar, so we only require 50% visibility.
    Bilateral averaging handles cases where one shoulder is blocked.

    Args:
        pipeline_data (Dict[str, Any]): Output from process_video() containing angles
        required_visibility (float): Minimum fraction of frames that need shoulders (default 0.5)

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
            - is_valid: True if shoulders visible enough, False otherwise
            - error_message: Empty string if valid, helpful message if invalid

    Example:
        >>> result = process_video("squat.mp4")
        >>> is_valid, msg = validate_pose_visibility(result['pipeline_data'])
        >>> if not is_valid:
        ...     print(msg)  # "Shoulders not visible in enough frames..."
    """
    angles_data = pipeline_data.get('angles', [])

    if not angles_data:
        return False, (
            "No pose detected in video. Please ensure:\n"
            "- A person is clearly visible in the frame\n"
            "- Lighting is adequate\n"
            "- Camera is stable"
        )

    # Check if shoulders are visible by looking for shoulder-dependent angles
    total_frames = len(angles_data)
    frames_with_shoulders = 0

    for frame_data in angles_data:
        # Shoulder landmarks (11, 12) are used in hip and back angles
        # If these angles exist (not None), shoulders were detected
        has_shoulder_angles = (
            frame_data.get('hip_left') is not None or
            frame_data.get('hip_right') is not None or
            frame_data.get('back_left') is not None or
            frame_data.get('back_right') is not None
        )

        if has_shoulder_angles:
            frames_with_shoulders += 1

    # Calculate visibility percentage
    shoulder_visibility_pct = frames_with_shoulders / total_frames if total_frames > 0 else 0

    if shoulder_visibility_pct < required_visibility:
        return False, (
            f"Shoulders not visible in enough frames ({shoulder_visibility_pct:.0%} detected, need {required_visibility:.0%}). "
            f"\n\nFor accurate analysis, please:\n"
            f"- BODYWEIGHT SQUATS: Record from the side at 90° angle\n"
            f"- BARBELL SQUATS: Record from a 45° diagonal angle (barbell blocks pure side view)\n"
            f"- Include full body from head to feet in frame\n"
            f"- At least one shoulder should be visible throughout the movement\n"
            f"- Stand 6-8 feet from the camera\n"
            f"- Use good lighting (avoid backlighting)"
        )

    return True, ""


def analyze_video(
    video_path: str,
    output_path: Optional[str] = None,
    frame_skip: int = 0,
    visualize: bool = True,
    min_visibility: float = 0.7
) -> Dict[str, Any]:
    """Analyze squat form from video file

    End-to-end pipeline that processes video, evaluates form against
    research-backed rules, and generates actionable feedback

    Args:
        video_path (str): Path to input video file
        output_path (Optional[str]): Optional path to save annotated video
        frame_skip (int): Number of frames to skip (0 = process all)
        visualize (bool): Whether to draw pose skeleton on output video
        min_visibility (float): Minimum landmark visibility threshold (0.0-1.0)

    Returns:
        Dict[str, Any]: Dict containing form_result and pipeline_data
    """

    # Run pose detection and angle extraction
    pipeline_data = process_video(
        video_path=video_path,
        output_path=output_path,
        frame_skip=frame_skip,
        visualize=visualize,
        min_visibility=min_visibility
    )

    # Transform angle data for analysis
    angles_dict = transform_angles(pipeline_data['angles'])

    # Evaluate form rules
    violations = evaluate_form(angles_dict)

    # Calculate score
    score = calculate_score(violations)

    # Generate feedback
    feedback_items = generate_feedback(violations, max_items=5)
    summary = generate_summary(violations, score)

    # Build result object
    form_result = FormResult(
        score=score,
        violations=violations,
        passed=is_passing(score),
        feedback_summary=feedback_items,
        details={
            'summary': summary,
            'frames_processed': pipeline_data['frames_processed'],
            'poses_detected': pipeline_data['poses_detected']
        }
    )

    return {
        'form_result': form_result,
        'pipeline_data': pipeline_data
    }
