import mediapipe as mp
import cv2
import numpy as np

# read the test image
image = cv2.imread('data/test_images/squat.jpeg')
# convert the colors to RGB instead of BGR
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# initialize MediaPipe pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

# process the test image
results = pose.process(image_rgb) 

if results.pose_landmarks:
    landmarks = results.pose_landmarks.landmark
    
# draw the skeleton on the image
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

mp_drawing.draw_landmarks(
    image,
    results.pose_landmarks,
    mp_pose.POSE_CONNECTIONS,
    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
)

# display
cv2.imshow('Pose Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
    
