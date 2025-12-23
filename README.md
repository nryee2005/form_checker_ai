# AI Workout Form Checker

> Computer vision-powered workout form analysis system using MediaPipe and FastAPI

## Project Status

**Current Phase:** Week 2 - Pose Pipeline ✅ COMPLETE
**Status:** 🚧 In Development
**Last Updated:** 2025-12-22

## Overview

An AI-powered workout form analyzer that provides real-time feedback on exercise technique, helping home fitness enthusiasts improve their form and prevent injuries without expensive personal trainers.

### Core Features (MVP)
- ✅ Pose detection using MediaPipe
- ✅ Biomechanical angle calculations (knee, hip, back)
- ✅ Video I/O utilities (complete)
- ✅ End-to-end video processing pipeline
- ✅ Video annotation with skeleton overlay and angle text
- ⏳ Research-backed form evaluation
- ⏳ Actionable feedback generation
- ⏳ REST API for video analysis

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

- [x] **Week 1:** Proof of Concept - MediaPipe integration & research
- [x] **Week 2:** Pose Pipeline - Video processing & angle extraction ✅
- [ ] **Week 3:** Analysis Engine - Form scoring & feedback
- [ ] **Week 4:** API - FastAPI endpoints
- [ ] **Week 5:** Optimization - Performance tuning (**MVP Complete**)
- [ ] **Week 6:** Frontend - Basic UI
- [ ] **Week 7:** Documentation - Portfolio ready

## Documentation

Detailed documentation coming soon in the `docs/` folder.

## Author

Nathan Yee
UC Santa Cruz 
BS Computer Engineering
