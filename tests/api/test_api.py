"""
Basic API endpoint tests

Tests the core API endpoints without requiring video files.
For full integration tests with real videos, use manual testing via Swagger UI.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns correct message"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Form Checker API"}


def test_recording_tips_endpoint():
    """Test the recording tips endpoint returns guidelines"""
    response = client.get("/api/recording-tips")
    assert response.status_code == 200

    data = response.json()

    # Check key fields exist
    assert "camera_angle_bodyweight" in data
    assert "camera_angle_barbell" in data
    assert "why_diagonal" in data
    assert "minimum_requirement" in data

    # Check content is helpful
    assert "90°" in data["camera_angle_bodyweight"]
    assert "45°" in data["camera_angle_barbell"]


def test_analyze_endpoint_no_file():
    """Test analyze endpoint rejects request with no file"""
    response = client.post("/api/analyze")
    assert response.status_code == 422  # Unprocessable Entity (missing required field)


def test_analyze_with_video_endpoint_no_file():
    """Test analyze-with-video endpoint rejects request with no file"""
    response = client.post("/api/analyze-with-video")
    assert response.status_code == 422  # Unprocessable Entity (missing required field)


def test_analyze_endpoint_invalid_extension():
    """Test analyze endpoint rejects non-video file"""
    response = client.post(
        "/api/analyze",
        files={"video": ("test.txt", b"fake content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid extension" in response.json()["detail"]


def test_analyze_with_video_endpoint_invalid_extension():
    """Test analyze-with-video endpoint rejects non-video file"""
    response = client.post(
        "/api/analyze-with-video",
        files={"video": ("test.txt", b"fake content", "text/plain")}
    )
    assert response.status_code == 400
    assert "Invalid file extension" in response.json()["detail"]


def test_openapi_docs_available():
    """Test that OpenAPI documentation is accessible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    openapi_spec = response.json()

    # Check basic structure
    assert "openapi" in openapi_spec
    assert "paths" in openapi_spec

    # Check our endpoints are documented
    assert "/api/analyze" in openapi_spec["paths"]
    assert "/api/analyze-with-video" in openapi_spec["paths"]
    assert "/api/recording-tips" in openapi_spec["paths"]
