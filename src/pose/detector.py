"""
MediaPipe wrapper for single frame pose detection
"""
import mediapipe as mp
import numpy as np
from typing import Optional, List

# Default confidence thresholds
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5


class PoseDetector:
    """Wrapper for MediaPipe Pose detection.

    Provides a clean interface for pose estimation, hiding MediaPipe
    complexity from the rest of the application.
    """

    def __init__(
        self,
        min_detection_confidence: float = MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence: float = MIN_TRACKING_CONFIDENCE
    ):
        """Initialize the pose detector.

        Args:
            min_detection_confidence: Minimum confidence for person detection (0.0-1.0)
            min_tracking_confidence: Minimum confidence for landmark tracking (0.0-1.0)
        """
        self.pose = mp.solutions.pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def detect(self, frame: np.ndarray) -> Optional[List]:
        """Detect pose landmarks in an RGB frame.

        Args:
            frame: RGB image as numpy array (H, W, 3)

        Returns:
            List of 33 MediaPipe landmarks if pose detected, None otherwise.
            Each landmark has x, y, z coordinates and visibility score.

        Note:
            Frame must be in RGB format. If using OpenCV (BGR), convert first:
            `frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)`
        """
        results = self.pose.process(frame)

        if results.pose_landmarks:
            return results.pose_landmarks.landmark

        return None

    def __del__(self):
        """Clean up MediaPipe resources."""
        if hasattr(self, 'pose') and self.pose:
            self.pose.close()
