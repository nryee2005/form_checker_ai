import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import mediapipe as mp
import cv2
import numpy as np
import matplotlib.pyplot as plt
from src.features.geometry import calculate_angle

class Point:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

cap = cv2.VideoCapture('data/videos/good_form/squat.mp4')

if not cap.isOpened():
    print("Error opening video")
    exit()

with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose:
    
    frame = 0;
    knee_angles = []
    hip_angles = []
    ankle_angles = []
    back_angles = []
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            break
        frame += 1
        
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        
        # calculate angle of knee
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # right side landmarks
            hip = landmarks[24] # right hip
            knee = landmarks[26] # right knee
            ankle = landmarks[28] # right ankle
            shoulder = landmarks[12] # right shoulder
            toe = landmarks[32] # right toe
            
            # calculate angles of interest
            knee_angle = calculate_angle(hip, knee, ankle)
            hip_angle = calculate_angle(shoulder, hip, knee)
            ankle_angle = calculate_angle(knee, ankle, toe)

            # create vertical reference point for back angle
            # This point is directly below the hip in the image (y increases downward)
            vertical_point = Point(hip.x, hip.y + 0.2, hip.z)
            back_angle = calculate_angle(shoulder, hip, vertical_point)

            # store all angles
            knee_angles.append(knee_angle)
            hip_angles.append(hip_angle)
            ankle_angles.append(ankle_angle)
            back_angles.append(back_angle)
        
        # draw pose annotations on image
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )
        
        cv2.imshow('MediaPipe Pose', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
cv2.destroyAllWindows

# plot all angles over time
plt.figure(figsize=(14, 10))

# subplot for each angle
plt.subplot(2, 2, 1)
plt.plot(knee_angles, linewidth=2, color='blue')
plt.xlabel('Frame Number')
plt.ylabel('Angle (degrees)')
plt.title('Knee Angle Over Time')
plt.grid(True, alpha=0.3)
plt.axhline(y=90, color='r', linestyle='--', label='90° reference')

plt.subplot(2, 2, 2)
plt.plot(hip_angles, linewidth=2, color='green')
plt.xlabel('Frame Number')
plt.ylabel('Angle (degrees)')
plt.title('Hip Angle Over Time')
plt.grid(True, alpha=0.3)

plt.subplot(2, 2, 3)
plt.plot(back_angles, linewidth=2, color='orange')
plt.xlabel('Frame Number')
plt.ylabel('Angle (degrees)')
plt.title('Back/Torso Angle Over Time')
plt.grid(True, alpha=0.3)

plt.subplot(2, 2, 4)
plt.plot(ankle_angles, linewidth=2, color='purple')
plt.xlabel('Frame Number')
plt.ylabel('Angle (degrees)')
plt.title('Ankle Angle Over Time')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()