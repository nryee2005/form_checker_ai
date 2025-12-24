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

ANGLES_CONFIG = [
    {
        'name': 'knee_left',
        'display': 'L Knee',
        'landmarks': [23, 25, 27],  # Hip → Knee → Ankle
        'color': (0, 255, 0),       # Green
    },
    {
        'name': 'knee_right',
        'display': 'R Knee',
        'landmarks': [24, 26, 28],
        'color': (0, 255, 0),
    },
    {
        'name': 'hip_left',
        'display': 'L Hip',
        'landmarks': [11, 23, 25],  # Shoulder → Hip → Knee
        'color': (255, 165, 0),     # Orange
    },
    {
        'name': 'hip_right',
        'display': 'R Hip',
        'landmarks': [12, 24, 26],
        'color': (255, 165, 0),
    },
    {
        'name': 'back_left',
        'display': 'L Back',
        'landmarks': [11, 23, 27],  # Shoulder → Hip → Ankle
        'color': (255, 0, 255),     # Magenta
    },
    {
        'name': 'back_right',
        'display': 'R Back',
        'landmarks': [12, 24, 28],  # Shoulder → Hip → Ankle
        'color': (255, 0, 255),     # Magenta
    },
]

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

    # Loop through all frames in the cideo
    for frame in iterate_frames(video_path, frame_skip):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Gets MediaPipe pose_landmarks object
        pose_landmarks = detector.detect_with_landmarks(frame_rgb)
        
        if not pose_landmarks:
            frames_processed += 1
            if visualize:
                output_frames.append(frame)
            continue
        
        landmarks = pose_landmarks.landmark
        frame_angles = {}

        for angle_config in ANGLES_CONFIG:
            # Check visibility
            if check_visibility(landmarks, angle_config['landmarks']):
                # Calculate angle
                angle = calculate_angle(
                    landmarks[angle_config['landmarks'][0]],
                    landmarks[angle_config['landmarks'][1]],
                    landmarks[angle_config['landmarks'][2]]
                )
                frame_angles[angle_config['name']] = angle
            else:
                frame_angles[angle_config['name']] = None
        
        # Append annotated frame if visualize=True
        if visualize:
            annotated_frame = frame.copy()
            
            mp_drawing.draw_landmarks(
                annotated_frame,
                pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            # Add text for all angles
            y_position = 30
            for angle_config in ANGLES_CONFIG:
                angle_value = frame_angles.get(angle_config['name'])

                if angle_value is not None:
                    cv2.putText(
                        annotated_frame,
                        f"{angle_config['display']}: {angle_value:.1f} deg",
                        (10, y_position),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        angle_config['color'],
                        2
                    )
                    y_position += 30
            
            output_frames.append(annotated_frame)
            
        frames_processed += 1
        poses_detected += 1
        
        # Store data after frame count incremented
        angles_data.append({
            "frame": frames_processed,
            **frame_angles  # Unpack all angles into dict
        })
        
    # Write output video
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
    