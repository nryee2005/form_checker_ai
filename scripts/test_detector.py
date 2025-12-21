import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import cv2
from src.pose.detector import PoseDetector


def test_image():
    """Test pose detection on a single image."""
    print("Testing PoseDetector on image...")

    # Load test image
    image = cv2.imread('data/test_images/squat.jpeg')
    if image is None:
        print("Could not load test image")
        return False

    # Convert BGR to RGB (OpenCV loads as BGR)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Create detector and detect pose
    detector = PoseDetector()
    landmarks = detector.detect(image_rgb)

    if landmarks:
        print(f"Detected {len(landmarks)} landmarks")
        print(f"   First landmark (nose): x={landmarks[0].x:.3f}, y={landmarks[0].y:.3f}")
        return True
    else:
        print("No pose detected")
        return False


def test_video():
    """Test pose detection on video frames."""
    print("\nTesting PoseDetector on video...")

    # Open video
    cap = cv2.VideoCapture('data/videos/good_form/squat.mp4')
    if not cap.isOpened():
        print("Could not open video")
        return False

    # Create detector
    detector = PoseDetector(min_detection_confidence=0.5)

    # Test first 10 frames
    detected_count = 0
    for i in range(10):
        success, frame = cap.read()
        if not success:
            break

        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect pose
        landmarks = detector.detect(frame_rgb)
        if landmarks:
            detected_count += 1

    cap.release()

    print(f"Detected pose in {detected_count}/10 frames")
    return detected_count > 0


if __name__ == "__main__":
    # Run tests
    image_pass = test_image()
    video_pass = test_video()

    # Summary
    if image_pass and video_pass:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
