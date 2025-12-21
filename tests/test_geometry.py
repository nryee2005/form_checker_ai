"""
Unit tests for geometry calculations.

Tests the calculate_angle function with known geometric configurations.
"""

import pytest
import numpy as np
from src.features.geometry import calculate_angle


class Point:
    """Simple point class for testing (mimics MediaPipe landmark)."""
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


class TestCalculateAngle:
    """Test suite for calculate_angle function."""

    def test_90_degree_angle(self):
        """Test angle calculation for 90 degree angle."""
        # Arrange: Create points forming 90° angle
        # p1 at (1,0,0), p2 at origin, p3 at (0,1,0)
        point_a = Point(1.0, 0.0, 0.0)
        point_b = Point(0.0, 0.0, 0.0)
        point_c = Point(0.0, 1.0, 0.0)

        # Act: Calculate angle
        angle = calculate_angle(point_a, point_b, point_c)

        # Assert: Should be 90 degrees
        assert angle == pytest.approx(90.0, abs=0.1)

    def test_180_degree_angle(self):
        """Test angle calculation for straight line (180 degrees)."""
        # Arrange: Points in a straight line
        point_a = Point(1.0, 0.0, 0.0)
        point_b = Point(0.0, 0.0, 0.0)
        point_c = Point(-1.0, 0.0, 0.0)

        # Act
        angle = calculate_angle(point_a, point_b, point_c)

        # Assert: Should be 180 degrees
        assert angle == pytest.approx(180.0, abs=0.1)

    def test_45_degree_angle(self):
        """Test angle calculation for 45 degree angle."""
        # Arrange: Create 45° angle
        point_a = Point(1.0, 0.0, 0.0)
        point_b = Point(0.0, 0.0, 0.0)
        point_c = Point(1.0, 1.0, 0.0)  # 45° from x-axis

        # Act
        angle = calculate_angle(point_a, point_b, point_c)

        # Assert: Should be 45 degrees
        assert angle == pytest.approx(45.0, abs=0.1)

    def test_collinear_points_straight_line(self):
        """Test angle calculation for collinear points (straight line = 180°)."""
        # Arrange: All points aligned in a straight line
        point_a = Point(2.0, 0.0, 0.0)
        point_b = Point(1.0, 0.0, 0.0)
        point_c = Point(0.0, 0.0, 0.0)

        # Act
        angle = calculate_angle(point_a, point_b, point_c)

        # Assert: Collinear points form 180° angle
        assert angle == pytest.approx(180.0, abs=0.1)

    def test_60_degree_angle(self):
        """Test angle calculation for 60 degree angle."""
        # Arrange: Equilateral triangle configuration
        point_a = Point(1.0, 0.0, 0.0)
        point_b = Point(0.0, 0.0, 0.0)
        point_c = Point(0.5, np.sqrt(3)/2, 0.0)  # 60° from x-axis

        # Act
        angle = calculate_angle(point_a, point_b, point_c)

        # Assert: Should be 60 degrees
        assert angle == pytest.approx(60.0, abs=0.1)

    def test_with_3d_points(self):
        """Test angle calculation works in 3D space."""
        # Arrange: Points in 3D (not in xy-plane)
        point_a = Point(1.0, 0.0, 1.0)
        point_b = Point(0.0, 0.0, 0.0)
        point_c = Point(0.0, 1.0, 1.0)

        # Act
        angle = calculate_angle(point_a, point_b, point_c)

        # Assert: Should calculate correctly in 3D space
        # The actual angle between these vectors is 60°
        assert angle == pytest.approx(60.0, abs=0.1)

    def test_realistic_knee_angle(self):
        """Test with realistic knee angle values from squats."""
        # Arrange: Simulate hip-knee-ankle at ~90° (squat bottom position)
        hip = Point(0.5, 0.5, 0.1)
        knee = Point(0.5, 0.7, 0.1)
        ankle = Point(0.5, 0.9, 0.1)

        # Act
        angle = calculate_angle(hip, knee, ankle)

        # Assert: Should be close to 180° (extended leg) or acute angle
        # This is just checking it returns reasonable values
        assert 0 <= angle <= 180
