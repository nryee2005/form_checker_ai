"""
Form rules for squat analysis

Based on research from:
Straub RK, Powers CM. "A Biomechanical Review of the Squat Exercise."
IJSPT 2024;19(4):490-501.
"""
from typing import Dict, List, Tuple
from .models import FormViolation, Severity

# Spine neutral thresholds
SPINE_NEUTRAL_CONFIG = {
    'max_sudden_change': 20,
    'max_total_range': 35,
    'butt_wink_hip_threshold': 60,
    'butt_wink_back_change': 30,
    'min_consecutive_frames': 2,  # Require N consecutive frames to trigger sudden change violation
}

# Squat depth thresholds (knee angle)
SQUAT_DEPTH_CONFIG = {
    'ideal_min': 60,
    'ideal_max': 100,
    'acceptable_min': 40,
    'acceptable_max': 120,
    'danger_threshold': 40,
}

# Hip angle thresholds
HIP_ANGLE_CONFIG = {
    'ideal_min': 70,
    'ideal_max': 110,
    'watch_threshold': 60,
    'danger_threshold': 40,
}

# Trunk inclination thresholds (from vertical)
TRUNK_INCLINATION_CONFIG = {
    'good_max': 45,
    'moderate_max': 60,
    'excessive': 60,
}

# Tibia inclination thresholds (from vertical)
TIBIA_INCLINATION_CONFIG = {
    'upright_max': 15,
    'moderate_max': 30,
    'high_forward': 30,
}


def _average_bilateral(left: List, right: List) -> List:
    """Average bilateral angles, handling None values.

    Args:
        left: Left side angle measurements (may contain None)
        right: Right side angle measurements (may contain None)

    Returns:
        Averaged angles with None handling:
        - Both valid: average
        - One None: use valid value
        - Both None: None
    """
    result = []
    for l, r in zip(left, right):
        if l is not None and r is not None:
            result.append((l + r) / 2)
        elif l is not None:
            result.append(l)
        elif r is not None:
            result.append(r)
        else:
            result.append(None)
    return result


def _filter_outliers(values: List, percentile_range: float = 0.1) -> List:
    """Remove statistical outliers from angle measurements.

    Uses percentile-based filtering to remove extreme values.
    Handles MediaPipe detection glitches that create extreme angle spikes.

    Args:
        values: List of angle values (may contain None)
        percentile_range: Fraction to trim from each tail (default: 0.1 = remove top/bottom 10%)

    Returns:
        List with outliers removed, preserving None values
    """
    valid = [x for x in values if x is not None]

    if len(valid) < 10:  # Need at least 10 points for meaningful percentile filtering
        return values

    # Sort and calculate percentile bounds
    sorted_valid = sorted(valid)
    n = len(sorted_valid)
    lower_idx = int(n * percentile_range)
    upper_idx = int(n * (1 - percentile_range))

    if lower_idx >= upper_idx:  # Too few data points
        return values

    lower_bound = sorted_valid[lower_idx]
    upper_bound = sorted_valid[upper_idx - 1]

    # Filter values outside bounds
    filtered = []
    for val in values:
        if val is None:
            filtered.append(None)
        elif lower_bound <= val <= upper_bound:
            filtered.append(val)
        else:
            filtered.append(None)  # Replace outliers with None

    return filtered


def check_spine_neutral(angles: Dict[str, List[float]]) -> List[FormViolation]:
    """Check if spine remains neutral throughout squat.

    Uses proxy measures since we can't directly measure spine curvature:
    - Sudden changes in back angle (>12° between frames)
    - Butt wink pattern (deep hip + large back angle change)
    - Excessive total range of back angle motion

    Args:
        angles (Dict[str, List[float]]): Dict with 'back_left', 'hip_left', etc.

    Returns:
        List[FormViolation]: List of violations found (empty if passed)
    """
    violations = []

    back_left = angles.get('back_left')
    back_right = angles.get('back_right')

    # Average the two sides for more robust measurement
    if back_left and back_right:
        back_left_filtered = _filter_outliers(back_left)
        back_right_filtered = _filter_outliers(back_right)
        back_angles = _average_bilateral(back_left_filtered, back_right_filtered)
    elif back_left:
        back_angles = _filter_outliers(back_left)
    elif back_right:
        back_angles = _filter_outliers(back_right)
    else:
        return violations

    # Check 1: Sudden changes (consecutive frame requirement)
    violation_frames = []
    for i in range(len(back_angles) - 1):
        if back_angles[i] is not None and back_angles[i+1] is not None:
            change = abs(back_angles[i+1] - back_angles[i])
            if change > SPINE_NEUTRAL_CONFIG['max_sudden_change']:
                violation_frames.append(i)

    # Group into consecutive sequences
    if violation_frames:
        sequences = []
        current_seq = [violation_frames[0]]

        for frame in violation_frames[1:]:
            if frame == current_seq[-1] + 1:
                current_seq.append(frame)
            else:
                sequences.append(current_seq)
                current_seq = [frame]
        sequences.append(current_seq)

        # Only report sequences meeting minimum consecutive frame requirement
        min_consecutive = SPINE_NEUTRAL_CONFIG['min_consecutive_frames']
        for seq in sequences:
            if len(seq) >= min_consecutive:
                # Calculate max change in this sequence
                max_change = max(
                    abs(back_angles[i+1] - back_angles[i])
                    for i in seq
                    if back_angles[i] is not None and back_angles[i+1] is not None
                )
                violations.append(FormViolation(
                    rule_name='spine_sudden_change',
                    severity=Severity.CRITICAL,
                    passed=False,
                    score_penalty=30,
                    feedback=f'Sustained spine movement detected ({len(seq)} consecutive frames) - maintain neutral spine',
                    frames=seq + [seq[-1] + 1],
                    details={'max_change': max_change, 'threshold': SPINE_NEUTRAL_CONFIG['max_sudden_change'], 'num_frames': len(seq)}
                ))

    # Check 2: Butt wink pattern (aggregate analysis)
    hip_left = angles.get('hip_left', [])
    hip_right = angles.get('hip_right', [])

    # Average both sides for hip angle (same approach as back angle)
    if hip_left and hip_right:
        hip_left_filtered = _filter_outliers(hip_left)
        hip_right_filtered = _filter_outliers(hip_right)
        hip_angles = _average_bilateral(hip_left_filtered, hip_right_filtered)
    elif hip_left:
        hip_angles = _filter_outliers(hip_left)
    elif hip_right:
        hip_angles = _filter_outliers(hip_right)
    else:
        hip_angles = []

    if hip_angles:
        valid_hip = [x for x in hip_angles if x is not None]
        valid_back = [x for x in back_angles if x is not None]

        if valid_hip and valid_back:
            min_hip = min(valid_hip)
            back_range = max(valid_back) - min(valid_back)

            # Butt wink = deep hip flexion + large back angle change
            if (min_hip < SPINE_NEUTRAL_CONFIG['butt_wink_hip_threshold'] and
                back_range > SPINE_NEUTRAL_CONFIG['butt_wink_back_change']):
                violations.append(FormViolation(
                    rule_name='butt_wink',
                    severity=Severity.CRITICAL,
                    passed=False,
                    score_penalty=25,
                    feedback=f'Butt wink detected - squatting beyond hip mobility (hip: {min_hip:.0f}°, back change: {back_range:.0f}°)',
                    details={
                        'min_hip_angle': min_hip,
                        'back_range': back_range,
                        'hip_threshold': SPINE_NEUTRAL_CONFIG['butt_wink_hip_threshold'],
                        'back_threshold': SPINE_NEUTRAL_CONFIG['butt_wink_back_change']
                    }
                ))

    # Check 3: Excessive total range
    valid_back = [x for x in back_angles if x is not None]
    if valid_back:
        back_range = max(valid_back) - min(valid_back)
        if back_range > SPINE_NEUTRAL_CONFIG['max_total_range']:
            violations.append(FormViolation(
                rule_name='excessive_spine_movement',
                severity=Severity.HIGH,
                passed=False,
                score_penalty=20,
                feedback=f'Excessive spine movement throughout squat ({back_range:.0f}° total range) - maintain more stable spine position',
                details={
                    'back_range': back_range,
                    'threshold': SPINE_NEUTRAL_CONFIG['max_total_range']
                }
            ))

    return violations


def check_squat_depth(angles: Dict[str, List[float]]) -> List[FormViolation]:
    """Check if squat depth is appropriate and safe.

    Evaluates minimum knee angle achieved during squat:
    - Ideal: 70-90° (thigh parallel)
    - Acceptable: 45-110° (shallow to deep)
    - Too deep: <45° (joint stress risk)

    Args:
        angles (Dict[str, List[float]]): Dict with 'knee_left', 'knee_right'

    Returns:
        List[FormViolation]: List of violations found
    """
    violations = []

    knee_left = angles.get('knee_left', [])
    knee_right = angles.get('knee_right', [])

    # Filter outliers from knee angles
    knee_left_filtered = _filter_outliers(knee_left) if knee_left else []
    knee_right_filtered = _filter_outliers(knee_right) if knee_right else []

    # Use minimum of both sides (worse side = more conservative)
    if knee_left_filtered and knee_right_filtered:
        valid_left = [x for x in knee_left_filtered if x is not None]
        valid_right = [x for x in knee_right_filtered if x is not None]
        if valid_left and valid_right:
            min_knee = min(min(valid_left), min(valid_right))
        elif valid_left:
            min_knee = min(valid_left)
        elif valid_right:
            min_knee = min(valid_right)
        else:
            return violations
    elif knee_left_filtered:
        valid_left = [x for x in knee_left_filtered if x is not None]
        if valid_left:
            min_knee = min(valid_left)
        else:
            return violations
    elif knee_right_filtered:
        valid_right = [x for x in knee_right_filtered if x is not None]
        if valid_right:
            min_knee = min(valid_right)
        else:
            return violations
    else:
        return violations

    # Evaluate depth zones
    if SQUAT_DEPTH_CONFIG['ideal_min'] <= min_knee <= SQUAT_DEPTH_CONFIG['ideal_max']:
        # Ideal depth - positive feedback
        violations.append(FormViolation(
            rule_name='depth_ideal',
            severity=Severity.LOW,
            passed=True,
            score_penalty=0,
            feedback=f'Perfect depth - thigh parallel to floor ({min_knee:.0f}°)',
            details={'min_knee': min_knee}
        ))
    elif SQUAT_DEPTH_CONFIG['acceptable_min'] <= min_knee < SQUAT_DEPTH_CONFIG['ideal_min']:
        # Deep squat - acceptable but watch form
        violations.append(FormViolation(
            rule_name='depth_deep',
            severity=Severity.LOW,
            passed=True,
            score_penalty=0,
            feedback=f'Deep squat ({min_knee:.0f}°) - ensure spine stays neutral',
            details={'min_knee': min_knee}
        ))
    elif SQUAT_DEPTH_CONFIG['ideal_max'] < min_knee <= SQUAT_DEPTH_CONFIG['acceptable_max']:
        # Shallow squat - could go deeper
        violations.append(FormViolation(
            rule_name='depth_shallow',
            severity=Severity.MEDIUM,
            passed=False,
            score_penalty=10,
            feedback=f'Squat slightly shallow ({min_knee:.0f}°) - try to reach thigh parallel if comfortable',
            details={'min_knee': min_knee}
        ))
    elif min_knee < SQUAT_DEPTH_CONFIG['danger_threshold']:
        # Too deep - safety concern
        violations.append(FormViolation(
            rule_name='depth_excessive',
            severity=Severity.HIGH,
            passed=False,
            score_penalty=15,
            feedback=f'Squat too deep ({min_knee:.0f}°) - risk of form breakdown and joint stress',
            details={'min_knee': min_knee}
        ))
    else:
        # Very shallow - barely squatting
        violations.append(FormViolation(
            rule_name='depth_very_shallow',
            severity=Severity.HIGH,
            passed=False,
            score_penalty=20,
            feedback=f'Squat very shallow ({min_knee:.0f}°) - increase depth to get benefits',
            details={'min_knee': min_knee}
        ))

    return violations


def check_hip_angle(angles: Dict[str, List[float]]) -> List[FormViolation]:
    """Check if hip flexion is within safe range.

    Hip angle below ~70° may trigger posterior pelvic tilt (butt wink).
    Should be checked in combination with spine angle.

    Args:
        angles (Dict[str, List[float]]): Dict with 'hip_left', 'hip_right'

    Returns:
        List[FormViolation]: List of violations found
    """
    violations = []

    hip_left = angles.get('hip_left', [])
    hip_right = angles.get('hip_right', [])

    # Average both sides
    if hip_left and hip_right:
        hip_left_filtered = _filter_outliers(hip_left)
        hip_right_filtered = _filter_outliers(hip_right)
        hip_angles = _average_bilateral(hip_left_filtered, hip_right_filtered)
    elif hip_left:
        hip_angles = _filter_outliers(hip_left)
    elif hip_right:
        hip_angles = _filter_outliers(hip_right)
    else:
        return violations

    valid_hip = [x for x in hip_angles if x is not None]
    if not valid_hip:
        return violations

    min_hip = min(valid_hip)

    # Evaluate hip flexion zones
    if min_hip >= HIP_ANGLE_CONFIG['ideal_min']:
        # Good hip depth
        violations.append(FormViolation(
            rule_name='hip_angle_good',
            severity=Severity.LOW,
            passed=True,
            score_penalty=0,
            feedback=f'Good hip depth ({min_hip:.0f}°)',
            details={'min_hip': min_hip}
        ))
    elif HIP_ANGLE_CONFIG['danger_threshold'] <= min_hip < HIP_ANGLE_CONFIG['watch_threshold']:
        # Warning zone - watch for butt wink
        violations.append(FormViolation(
            rule_name='hip_angle_deep',
            severity=Severity.MEDIUM,
            passed=False,
            score_penalty=5,
            feedback=f'Deep hip flexion ({min_hip:.0f}°) - watch for posterior pelvic tilt',
            details={'min_hip': min_hip}
        ))
    elif min_hip < HIP_ANGLE_CONFIG['danger_threshold']:
        # Excessive hip flexion
        violations.append(FormViolation(
            rule_name='hip_angle_excessive',
            severity=Severity.HIGH,
            passed=False,
            score_penalty=15,
            feedback=f'Excessive hip flexion ({min_hip:.0f}°) - likely causing spine rounding',
            details={'min_hip': min_hip}
        ))

    return violations


def check_trunk_inclination(angles: Dict[str, List[float]]) -> List[FormViolation]:
    """Check if trunk forward lean is reasonable.

    Note: This check requires trunk angle from vertical, which is not
    currently calculated in the pipeline. This is a placeholder for future enhancement.

    Args:
        angles (Dict[str, List[float]]): Dict with angle data

    Returns:
        List[FormViolation]: Empty list (not implemented yet)
    """
    # TODO: Implement when trunk-from-vertical angle is added to pipeline
    # Would need to calculate angle between shoulder-hip line and vertical axis
    return []


def check_tibia_inclination(angles: Dict[str, List[float]]) -> List[FormViolation]:
    """Check tibia forward angle (mostly informational).

    Note: This check requires tibia angle from vertical, which is not
    currently calculated in the pipeline. This is a placeholder for future enhancement.

    Args:
        angles (Dict[str, List[float]]): Dict with angle data

    Returns:
        List[FormViolation]: Empty list (not implemented yet)
    """
    # TODO: Implement when tibia-from-vertical angle is added to pipeline
    # Would need to calculate angle between knee-ankle line and vertical axis
    return []


def evaluate_form(angles: Dict[str, List[float]]) -> List[FormViolation]:
    """Main entry point - runs all form rule checks.

    Args:
        angles (Dict[str, List[float]]): Dict with keys like 'knee_left', 'hip_left', 'back_left'
            Values are lists of angles (degrees) per frame.

    Returns:
        List[FormViolation]: List of all violations found across all rules
    """
    all_violations = []

    # Run all rule checks (order by priority)
    all_violations.extend(check_spine_neutral(angles))
    all_violations.extend(check_squat_depth(angles))
    all_violations.extend(check_hip_angle(angles))
    all_violations.extend(check_trunk_inclination(angles))
    all_violations.extend(check_tibia_inclination(angles))

    return all_violations
