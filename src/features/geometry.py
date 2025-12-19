import numpy as np

def calculate_angle(point_a, point_b, point_c):
    a = np.array([point_a.x, point_a.y, point_a.z])
    b = np.array([point_b.x, point_b.y, point_b.z])
    c = np.array([point_c.x, point_c.y, point_c.z])
    
    ba = a - b
    bc = c - b
    
    # find the cos(theta)
    cos_theta = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    # handle floating point errors
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    
    # convert to angle in degrees
    theta = np.arccos(cos_theta)
    angle = np.degrees(theta)
    
    return angle
    
    