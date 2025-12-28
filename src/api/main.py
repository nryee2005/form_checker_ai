"""
FastAPI application for squat form analysis

Suppresses MediaPipe/TensorFlow warnings for cleaner logs
"""
import os
import warnings

# Suppress TensorFlow/MediaPipe info and warning messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=all, 1=info, 2=warning, 3=error

# Suppress specific warnings
warnings.filterwarnings('ignore', category=UserWarning, module='google.protobuf')
warnings.filterwarnings('ignore', message='.*absl.*')

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
import tempfile
from pathlib import Path
from src.api.schemas import AnalysisResponse, convert_form_result_to_response
from src.analysis.analyzer import analyze_video, validate_pose_visibility

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Form Checker API"}


@app.get("/api/recording-tips")
def get_recording_tips():
    """Get tips for recording videos for optimal analysis results

    Returns guidelines on camera angle, framing, lighting, and video quality
    to ensure accurate form analysis.
    """
    return {
        "camera_angle_bodyweight": "For bodyweight squats: Record from the SIDE at 90° angle",
        "camera_angle_barbell": "For barbell squats: Record from a 45° DIAGONAL angle (barbell blocks pure side view)",
        "why_diagonal": "The barbell on your shoulders blocks shoulder visibility from the side. A 45° angle lets the camera see your shoulder AND your depth",
        "framing": "Full body visible - head to feet, at least one shoulder visible throughout",
        "distance": "Stand 6-8 feet away from the camera",
        "lighting": "Good, even lighting. Avoid backlighting (don't stand in front of windows)",
        "clothing": "Fitted clothing helps pose detection (avoid baggy clothes)",
        "background": "Clear, uncluttered background for better pose detection",
        "video_format": "MP4 or MOV format",
        "resolution": "720p (1280x720) or higher recommended",
        "duration": "10-30 seconds, perform 3-5 squat reps",
        "camera_stability": "Use a tripod or stable surface (avoid handheld)",
        "minimum_requirement": "At least 50% of frames must have shoulder visible (barbell obstruction is expected)"
    }

ALLOWED_EXTENSIONS = {".mp4", ".mov"}
ALLOWED_TYPES = {"video/mp4", "video/quicktime"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Create analysis endpoint
@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(video: UploadFile = File(..., description="Squat video to analyze")):
    content = await video.read()
    
    # Check validity of file
    file_ext = Path(video.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid extension")
    
    if video.content_type not in ALLOWED_TYPES:
        #raise HTTPException(status_code=400, 
        #                   detail=f"Invalid file type. Allowed: MP4, MOV. Got: {video.content_type}")
        print(f"Warning: Unexpected MIME type '{video.content_type}' for file '{video.filename}'")
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, 
                            detail=f"File too large. Max size: 100MB. Got: {len(content) / 1024 / 1024:.1f}MB")
    
    
    # Write content into a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(content)
        tmp.flush()
        tmp_path = Path(tmp.name)
    
    # Process video and cleanup
    try:
        result = analyze_video(
            video_path=str(tmp_path),
            output_path=None,
            visualize=False,
            frame_skip=0,
            min_visibility=0.85  # Stricter threshold to avoid MediaPipe guesses
        )

        # Validate that shoulders are visible for accurate analysis
        is_valid, error_message = validate_pose_visibility(result['pipeline_data'])
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=error_message
            )

        form_response = convert_form_result_to_response(result['form_result'])
        
        return AnalysisResponse(
            form_result=form_response,
            metadata={
                'frames_processed': result['pipeline_data']['frames_processed'],
                'poses_detected': result['pipeline_data']['poses_detected'],
                **result['pipeline_data']['metadata']  # Unpack fps, width, height, etc.
            }
        )
    except Exception as e:
        # Log the error
        print(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Video analysis failed. Please ensure video contains a person performing squats."
        )
    finally:
        tmp_path.unlink(missing_ok=True)


def cleanup_files(file_paths: list):
    """Delete temporary files after response is sent

    Used as BackgroundTask to clean up temp files after FileResponse
    has finished streaming the video to the client.

    Args:
        file_paths (list): List of Path objects or strings to delete
    """
    for path in file_paths:
        Path(path).unlink(missing_ok=True)


@app.post("/api/analyze-with-video")
async def analyze_with_video(video: UploadFile = File(..., description="Squat video to analyze")):
    """Analyze squat form and return annotated video file

    Processes the uploaded video to analyze squat form and returns an annotated
    MP4 video with:
    - Pose skeleton overlay (MediaPipe landmarks and connections)
    - Angle measurements displayed on screen (knee, hip, back)
    - Color-coded text by angle type (green for knee, orange for hip, magenta for back)

    This endpoint is slower than /api/analyze (adds 2-3 seconds for video generation)
    but provides visual feedback useful for debugging and presentations.

    Args:
        video (UploadFile): Uploaded squat video file (MP4 or MOV, max 100MB)

    Returns:
        FileResponse: Annotated MP4 video file ready for download/playback

    Raises:
        HTTPException 400: Invalid file type, size, or insufficient shoulder visibility
        HTTPException 413: File too large (> 100MB)
        HTTPException 500: Video processing failed
    """
    # Read uploaded file
    content = await video.read()

    # Validate file extension
    file_ext = Path(video.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension '{file_ext}'. Allowed: .mp4, .mov"
        )

    # Validate MIME type (warning only)
    if video.content_type not in ALLOWED_TYPES:
        print(f"Warning: Unexpected MIME type '{video.content_type}' for file '{video.filename}'")

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(content) / 1024 / 1024:.1f}MB). Maximum: 100MB"
        )

    # Create temp files and ensure cleanup
    input_tmp_path = None
    output_tmp_path = None

    try:
        # Create temp file for input video
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as input_tmp:
            input_tmp.write(content)
            input_tmp.flush()
            input_tmp_path = Path(input_tmp.name)

        # Create temp file PATH for output video (don't create the file itself)
        # Let write_video() create the actual file
        import os
        output_tmp_fd, output_tmp_str = tempfile.mkstemp(suffix=".mp4")
        os.close(output_tmp_fd)  # Close file descriptor
        os.unlink(output_tmp_str)  # Delete the empty file - write_video will create it
        output_tmp_path = Path(output_tmp_str)
        # Run analysis WITH visualization enabled
        result = analyze_video(
            video_path=str(input_tmp_path),
            output_path=str(output_tmp_path),  # Save annotated video here
            visualize=True,                     # Enable skeleton + angle overlays
            frame_skip=0,
            min_visibility=0.85  # Stricter threshold to avoid MediaPipe guesses
        )

        # Validate shoulder visibility
        is_valid, error_message = validate_pose_visibility(result['pipeline_data'])
        if not is_valid:
            # Cleanup temp files before raising error
            if input_tmp_path:
                input_tmp_path.unlink(missing_ok=True)
            if output_tmp_path:
                output_tmp_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail=error_message
            )

        # Return annotated video file with background cleanup
        return FileResponse(
            path=str(output_tmp_path),
            media_type="video/mp4",
            filename=f"analyzed_{video.filename}",
            background=BackgroundTask(cleanup_files, [input_tmp_path, output_tmp_path])
        )

    except HTTPException:
        # Re-raise HTTP exceptions (already handled above with cleanup)
        raise
    except Exception as e:
        # Cleanup on unexpected error
        if input_tmp_path:
            input_tmp_path.unlink(missing_ok=True)
        if output_tmp_path:
            output_tmp_path.unlink(missing_ok=True)

        print(f"Video analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Video analysis failed. Please ensure video contains a person performing squats with visible shoulders."
        )
