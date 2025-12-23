"""
Basic test for the video processing pipeline.
Tests core functionality without visualization.
"""
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pose.pipeline import process_video

def test_basic_pipeline():
    """Test basic pipeline without visualization."""

    # TODO: Replace with your actual video path
    video_path = "data/videos/good_form/squat.mp4"

    # Check if video exists
    if not Path(video_path).exists():
        print(f"❌ Error: Video not found at {video_path}")
        print("Please update the video_path variable with your test video.")
        return

    print("🎬 Testing pipeline on:", video_path)
    print("=" * 60)

    # Process video without visualization (faster)
    result = process_video(
        video_path=video_path,
        visualize=False,
        frame_skip=0  # Process every frame
    )

    # Print results
    print("\n📊 Results:")
    print("-" * 60)
    print(f"Frames processed: {result['frames_processed']}")
    print(f"Poses detected: {result['poses_detected']}")
    print(f"Detection rate: {result['poses_detected']/result['frames_processed']*100:.1f}%")

    print("\n📹 Video metadata:")
    print("-" * 60)
    for key, value in result['metadata'].items():
        print(f"{key}: {value}")

    print("\n📐 Angle data (first 5 frames):")
    print("-" * 60)
    for i, frame_data in enumerate(result['angles'][:5]):
        print(f"Frame {frame_data['frame']}:")
        print(f"  Left knee:  {frame_data['knee_left']:.1f}°" if frame_data['knee_left'] else "  Left knee:  None")
        print(f"  Right knee: {frame_data['knee_right']:.1f}°" if frame_data['knee_right'] else "  Right knee: None")

    if len(result['angles']) > 5:
        print(f"... and {len(result['angles']) - 5} more frames")

    print("\n✅ Test completed successfully!")

    # Basic sanity checks
    print("\n🔍 Sanity checks:")
    print("-" * 60)

    if result['poses_detected'] == 0:
        print("⚠️  WARNING: No poses detected! Check if:")
        print("   - Video shows a person")
        print("   - Person is clearly visible")
        print("   - Lighting is adequate")
    else:
        print(f"✓ Poses detected in {result['poses_detected']} frames")

    # Check if angles are in reasonable range
    valid_angles = [a for a in result['angles'] if a['knee_left'] is not None]
    if valid_angles:
        left_angles = [a['knee_left'] for a in valid_angles]
        avg_left = sum(left_angles) / len(left_angles)
        print(f"✓ Average left knee angle: {avg_left:.1f}°")

        if avg_left < 0 or avg_left > 180:
            print(f"⚠️  WARNING: Unusual angle range ({avg_left:.1f}°)")

    return result

if __name__ == "__main__":
    test_basic_pipeline()
