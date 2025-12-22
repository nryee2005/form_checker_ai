"""
End-to-end video processing pipeline
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from typing import Optional, Dict, Any
from src.utils.video_io import (read_video, 
                                write_video, 
                                get_video_info, 
                                iterate_frames, 
                                extract_frames)
from src.features.geometry import calculate_angle
import detector

def process_video(
    video_path: str,
    output_path: Optional[str] = None,
    frame_skip: int = 0,
    visualize: bool = True
) -> Dict[str, Any]:
    """
    Process a video through pose detection and angle extraction.
      
    Args:
        video_path: Path to input video
        output_path: Optional path to save annotated video
        frame_skip: Number of frames to skip (0 = process all)
        visualize: Whether to draw pose skeleton on frames
        
    Returns:
        Dictionary containing:
        - 'angles': List of angle measurements per frame
        - 'metadata': Video info (fps, dimensions, etc.)
        - 'frames_processed': Number of frames analyzed
        - 'poses_detected': Number of successful detections
    """
    