"""
Video I/O utility module for reading and writing video files
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Generator, Dict, Optional, Tuple

def validate_video_file(path: str) -> bool:
    """Takes in a video file path and verifies that it exists and is openable

    Args:
        path (str): The file path of the video

    Returns:
        bool: Returns True if the file path is valid, False otherwise
    """
    
    # Return False if path doesn't exist or the video cannot be opened
    if not Path(path).exists():
        return False
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return False
    
    cap.release()
    
    return True
    
def read_video(path: str) -> cv2.VideoCapture:
    """Reads in the video at the input file path

    Args:
        path (str): File path of the video to be opened

    Returns:
        VideoCapture: cv2 VideoCapture object
    """
    
    if not validate_video_file(path):
        raise FileNotFoundError('File does not exist or is not openable')
    
    return cv2.VideoCapture(path)
    
    
def get_video_info(path: str) -> dict:
    """Returns relevant parameters of the input video

    Args:
        path (str): File path of the video 

    Returns:
        dict: Dictionary containing the relevant parameters of the video
    """
    
    cap = read_video(path)
    
    vid_info = {}
    
    # Store fps, height, width, frame_count, and duration of video
    vid_info['fps'] = cap.get(cv2.CAP_PROP_FPS)
    vid_info['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_info['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    vid_info['frame_count'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Check for corrupted video file
    if vid_info['fps'] > 0:
        vid_info['duration'] = vid_info['frame_count'] / vid_info['fps']
    else:
        vid_info['duration'] = 0.0
    
    cap.release()
    
    return vid_info
    
    
def iterate_frames(path: str) -> Generator[np.ndarray, None, None]:
    """_summary_

    Args:
        path (str): _description_

    Yields:
        Generator[np.ndarray, None, None]: _description_
    """

def extract_frames(path: str, max_frames: Optional[int] = None) -> List[np.ndarray]:
    """_summary_

    Args:
        path (str): _description_
        max_frames (Optional[int], optional): _description_. Defaults to None.

    Returns:
        List[np.ndarray]: _description_
    """
    
def write_video(path: str, frames: List[np.ndarray], fps: int, codec: str = "mp4v") -> None:
    """Writes the input frames to a new video file

    Args:
        path (str): Name of output file
        frames (List[np.ndarray]): Frames to be written into the video (all must be same size)
        fps (int): Frames per second desired
        codec (str): Four-character codec code (default: 'mp4v')
    """
    if not frames:
        raise ValueError("Frame list is empty")
    # Check all frames are the same shape
    frame_shapes = [frame.shape[:2] for frame in frames]
    if len(set(frame_shapes)) > 1:
        raise ValueError("Not all frames are the same size")
    
    # Get height and width of frames
    height, width = frames[0].shape[:2]
    
    # Create fourcc code
    fourcc = cv2.VideoWriter_fourcc(*codec)
    # Create VideoWriter
    # Note: dimensions are (width, height) not (height, width)
    out = cv2.VideoWriter(path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        raise IOError(f"Failed to create video file: {path}")
    
    for frame in frames:
        out.write(frame)
    
    out.release()