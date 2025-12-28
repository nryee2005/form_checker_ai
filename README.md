# AI Workout Form Checker

> Computer vision-powered workout form analysis system using MediaPipe and FastAPI

## Project Status

**Current Phase:** Week 4 - API Backend ✅ COMPLETE
**Status:** 🚧 In Development (Ready for Week 5 - Optimization)
**Last Updated:** 2025-12-28

## Overview

An AI-powered workout form analyzer that provides real-time feedback on exercise technique, helping home fitness enthusiasts improve their form and prevent injuries without expensive personal trainers.

### Core Features (MVP)
- ✅ Pose detection using MediaPipe
- ✅ Biomechanical angle calculations (knee, hip, back)
- ✅ Video I/O utilities (complete)
- ✅ End-to-end video processing pipeline
- ✅ Video annotation with skeleton overlay and angle text
- ✅ Research-backed form evaluation (Straub & Powers 2024)
- ✅ Actionable feedback generation (0-100 score, prioritized violations)
- ✅ Outlier filtering for robust analysis
- ✅ REST API for video analysis (FastAPI)
- ✅ Video upload endpoints (JSON response + annotated video download)
- ✅ Shoulder visibility validation
- ✅ Temp file cleanup with monitoring

### Initial Focus
- **Exercise:** Squat (expanding to others post-MVP)
- **Mode:** Post-processing (real-time is stretch goal)
- **Timeline:** 7-8 weeks to MVP

## Tech Stack

**Backend/ML:**
- Python 3.12.2
- MediaPipe 0.10.14 (pose estimation)
- OpenCV 4.8+ (video processing)
- NumPy 1.26+ (angle calculations)
- SciPy 1.11+ (signal processing)

**API:**
- FastAPI 0.104+ (REST API)
- Pydantic 2.5+ (data validation)
- Uvicorn 0.24+ (ASGI server)

**Testing:**
- pytest 7.4+

## Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd form_checker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import mediapipe; import cv2; import fastapi; print('✅ All imports successful!')"
```

## Project Structure

```
form_checker/
├── src/                    # Application code
│   ├── pose/              # Pose detection (MediaPipe wrapper)
│   ├── features/          # Angle calculations & feature extraction
│   ├── analysis/          # Form evaluation & scoring
│   ├── api/               # FastAPI endpoints
│   └── utils/             # Shared utilities
├── tests/                 # Test suite
├── research/              # Biomechanics research & experiments
├── data/                  # Videos & annotations (not in git)
├── scripts/               # Standalone scripts
└── docs/                  # Documentation
```

## Development Roadmap

- [x] **Week 1:** Proof of Concept - MediaPipe integration & research ✅
- [x] **Week 2:** Pose Pipeline - Video processing & angle extraction ✅
- [x] **Week 3:** Analysis Engine - Form scoring & feedback ✅
- [x] **Week 4:** API Backend - FastAPI endpoints & file handling ✅
- [ ] **Week 5:** Optimization - Performance tuning (**MVP Complete**)
- [ ] **Week 6:** Frontend - Basic UI
- [ ] **Week 7:** Documentation - Portfolio ready

## API Usage

### Start the Development Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start API server with auto-reload
uvicorn src.api.main:app --reload

# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs (Swagger UI)
```

### API Endpoints

**GET `/`** - Health check
- Returns: `{"message": "Form Checker API"}`

**GET `/api/recording-tips`** - Get video recording guidelines
- Returns: JSON with camera angle, framing, lighting tips

**POST `/api/analyze`** - Analyze squat form (JSON response)
- Upload: Video file (MP4/MOV, max 100MB)
- Returns: JSON with score, violations, feedback, metadata

**POST `/api/analyze-with-video`** - Analyze + download annotated video
- Upload: Video file (MP4/MOV, max 100MB)
- Returns: MP4 file with pose skeleton and angle overlays

### Example Usage (Python)

```python
import requests

# Analyze video and get JSON feedback
with open("squat_video.mp4", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/analyze",
        files={"video": f}
    )
    result = response.json()
    print(f"Score: {result['form_result']['score']}")

# Download annotated video
with open("squat_video.mp4", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/analyze-with-video",
        files={"video": f}
    )
    with open("analyzed_output.mp4", "wb") as out:
        out.write(response.content)
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run API tests only
pytest tests/api/ -v

# Check for orphaned temp files
python scripts/check_temp_files.py
```

## Documentation

Detailed documentation coming soon in the `docs/` folder.

## Author

Nathan Yee
UC Santa Cruz 
BS Computer Engineering
