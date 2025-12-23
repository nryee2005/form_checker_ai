"""
Test video processing pipeline with visualization.
Creates an annotated output video with pose skeleton drawn.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pose.pipeline import process_video

def test_pipeline_with_visualization():
    """Test pipeline with visualization enabled."""

    # TODO: Update these paths for your setup
    video_path = "data/videos/good_form/squat.mp4"
    output_path = "data/videos/good_form/squat_annotated.mp4"

    # Check if video exists
    if not Path(video_path).exists():
        print(f"❌ Error: Video not found at {video_path}")
        print("Please update the video_path variable.")
        return

    print("🎬 Processing video with visualization...")
    print("=" * 60)
    print(f"Input:  {video_path}")
    print(f"Output: {output_path}")
    print()

    # Process with visualization
    result = process_video(
        video_path=video_path,
        output_path=output_path,
        visualize=True,
        frame_skip=0  # Process every frame
    )

    # Print results
    print("\n✅ Processing complete!")
    print("=" * 60)
    print(f"Frames processed: {result['frames_processed']}")
    print(f"Poses detected:   {result['poses_detected']}")
    print(f"Detection rate:   {result['poses_detected']/result['frames_processed']*100:.1f}%")

    print(f"\n📹 Annotated video saved to: {output_path}")
    print("\n💡 Next steps:")
    print("   1. Open the output video to verify pose detection")
    print("   2. Check if skeleton is drawn correctly")
    print("   3. Verify angle calculations look reasonable")

    return result

if __name__ == "__main__":
    test_pipeline_with_visualization()
