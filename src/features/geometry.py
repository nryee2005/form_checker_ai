"""
Geometric calculations for pose analysis.
"""
import numpy as np
from typing import Any

def calculate_angle(point_a: Any, point_b: Any, point_c: Any) -> float:
    """Calculates angle between three MediaPipe landmark points

    Args:
        point_a (MediaPipe_landmark): first landmark
        point_b (MediaPipe_landmark): second landmark, should be in between the other two
        point_c (MediaPipe_landmark): third landmark

    Returns:
        float: calculated angle between the three landmark points in degrees (0-180)
    """
    # Extract coordinates
    a = np.array([point_a.x, point_a.y, point_a.z])
    b = np.array([point_b.x, point_b.y, point_b.z])
    c = np.array([point_c.x, point_c.y, point_c.z])
    
    # Create BA and BC vectors
    ba = a - b
    bc = c - b
    
    # Calculate the cosine of the angle using the dot product
    cos_theta = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    # Clip to handle floating point errors
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    
    # Convert to angle in degrees
    theta = np.arccos(cos_theta)
    angle = np.degrees(theta)
    
    return angle
    
