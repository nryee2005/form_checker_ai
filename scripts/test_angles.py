import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import numpy as np
from src.features.geometry import calculate_angle

class Point:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        
# test 90 degree angle
p1 = Point(1, 0 ,0)
p2 = Point(0, 0, 0)
p3 = Point(0, 1, 0)

angle = calculate_angle(p1, p2 ,p3)
print(f"90 degree test: {angle:.1f} degrees")

# test 180 degree angle
p1 = Point(1, 0, 0)
p2 = Point(0, 0, 0)
p3 = Point(-1, 0, 0)

angle = calculate_angle(p1, p2, p3)
print(f"180 degree test: {angle:.1f} degrees")
    
    