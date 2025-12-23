"""
End-to-end video processing pipeline
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, Dict, Any, List
from src.utils.video_io import (read_video, 
                                write_video, 
                                get_video_info, 
                                iterate_frames, 
                                extract_frames)
from src.features.geometry import calculate_angle
from src.pose.detector import PoseDetector

def process_video(
    video_path: str,
    output_path: Optional[str] = None,
    frame_skip: int = 0,
    visualize: bool = True,
    min_visibility: float = 0.7
) -> Dict[str, Any]:
    """
    Process a video through pose detection and angle extraction.
      
    Args:
        video_path: Path to input video
        output_path: Optional path to save annotated video
        frame_skip: Number of frames to skip (0 = process all)
        visualize: Whether to draw pose skeleton on frames
        min_visibility: Minimum visibility for pose landmarks to be considered
        
    Returns:
        Dictionary containing:
        - 'angles': List of angle measurements per frame
        - 'metadata': Video info (fps, dimensions, etc.)
        - 'frames_processed': Number of frames analyzed
        - 'poses_detected': Number of successful detections
    """
    # Initialize PoseDetector and get video metadata
    detector = PoseDetector()
    metadata = get_video_info(video_path)
    
    angles_data = []
    frames_processed = 0
    poses_detected = 0
    output_frames = []
    
    if visualize:
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
    
    def check_visibility(landmarks, indices: List) -> bool:
        """
        Helper function to check landmark visibility above min_visibility
        """
        return all(landmarks[i].visibility >= min_visibility for i in indices)

    for frame in iterate_frames(video_path, frame_skip):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        landmarks = detector.detect(frame_rgb)
        
        if not landmarks:
            frames_processed += 1
            if visualize:
                output_frames.append(frame)
            continue
        
        # Check visibility of each knee
        left_knee_visible = check_visibility(landmarks, [23, 25, 27])
        right_knee_visible = check_visibility(landmarks, [24, 26, 28])
        
        if left_knee_visible:
            # Left knee angle: Hip → Knee → Ankle
            left_knee_angle = calculate_angle(
                landmarks[23],  # LEFT_HIP
                landmarks[25],  # LEFT_KNEE
                landmarks[27]   # LEFT_ANKLE
            )
        else:
            left_knee_angle = None 

        if right_knee_visible:
            # Right knee angle: Hip → Knee → Ankle
            right_knee_angle = calculate_angle(
                landmarks[24],  # RIGHT_HIP
                landmarks[26],  # RIGHT_KNEE
                landmarks[28]   # RIGHT_ANKLE
            )
        else:
            right_knee_angle = None
        
        # Append angle data from frame to the data list
        angles_data.append({
            "frame": frames_processed, 
            "knee_left": left_knee_angle, 
            "knee_right": right_knee_angle
        })
        
        if visualize:
            pose_landmarks = detector.detect_with_landmarks(frame_rgb)
            annotated_frame = frame.copy()
            
            mp_drawing.draw_landmarks(
                annotated_frame,
                pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            output_frames.append(annotated_frame)
            
        frames_processed += 1
        poses_detected += 1
        
    if visualize and output_path and output_frames:
        write_video(
            output_path,
            output_frames,
            fps=int(metadata['fps']),
            codec='mp4v'
        )
        
    return {
        'angles': angles_data,
        'metadata': metadata,
        'frames_processed': frames_processed,
        'poses_detected': poses_detected
    }
    