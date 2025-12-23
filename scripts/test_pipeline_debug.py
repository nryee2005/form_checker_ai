"""
Detailed debug test for the pipeline.
Provides verbose output to help troubleshoot issues.
"""
import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pose.pipeline import process_video

def test_pipeline_debug():
    """Test pipeline with detailed debug output."""

    # TODO: Update video path
    video_path = "data/videos/good_form/squat.mp4"

    if not Path(video_path).exists():
        print(f"❌ Error: Video not found at {video_path}")
        return

    print("🔍 DEBUG MODE - Detailed Pipeline Test")
    print("=" * 60)

    # Process video
    result = process_video(
        video_path=video_path,
        visualize=False,
        frame_skip=0
    )

    print("\n📊 METADATA:")
    print("-" * 60)
    print(json.dumps(result['metadata'], indent=2))

    print("\n📈 STATISTICS:")
    print("-" * 60)
    print(f"Total frames processed: {result['frames_processed']}")
    print(f"Poses detected:         {result['poses_detected']}")
    print(f"Frames with no pose:    {result['frames_processed'] - result['poses_detected']}")
    print(f"Detection rate:         {result['poses_detected']/result['frames_processed']*100:.1f}%")

    # Analyze angle data
    print("\n📐 ANGLE ANALYSIS:")
    print("-" * 60)

    left_angles = [a['knee_left'] for a in result['angles'] if a['knee_left'] is not None]
    right_angles = [a['knee_right'] for a in result['angles'] if a['knee_right'] is not None]

    if left_angles:
        print(f"Left knee angles detected: {len(left_angles)}")
        print(f"  Min:  {min(left_angles):.1f}°")
        print(f"  Max:  {max(left_angles):.1f}°")
        print(f"  Avg:  {sum(left_angles)/len(left_angles):.1f}°")
    else:
        print("⚠️  No left knee angles detected!")

    if right_angles:
        print(f"\nRight knee angles detected: {len(right_angles)}")
        print(f"  Min:  {min(right_angles):.1f}°")
        print(f"  Max:  {max(right_angles):.1f}°")
        print(f"  Avg:  {sum(right_angles)/len(right_angles):.1f}°")
    else:
        print("⚠️  No right knee angles detected!")

    # Show sample data
    print("\n📋 SAMPLE ANGLE DATA (first 10 frames):")
    print("-" * 60)
    for frame_data in result['angles'][:10]:
        left = f"{frame_data['knee_left']:6.1f}°" if frame_data['knee_left'] else "   None"
        right = f"{frame_data['knee_right']:6.1f}°" if frame_data['knee_right'] else "   None"
        print(f"Frame {frame_data['frame']:3d}: L={left}  R={right}")

    # Check for issues
    print("\n⚠️  ISSUE DETECTION:")
    print("-" * 60)

    issues_found = False

    if result['poses_detected'] == 0:
        print("❌ CRITICAL: No poses detected in any frame!")
        print("   Possible causes:")
        print("   - No person visible in video")
        print("   - Poor lighting")
        print("   - Person too far from camera")
        print("   - Video format issues")
        issues_found = True

    if result['poses_detected'] / result['frames_processed'] < 0.3:
        print("⚠️  WARNING: Low detection rate (<30%)")
        print("   Consider:")
        print("   - Improving video quality")
        print("   - Ensuring full body is visible")
        print("   - Better lighting conditions")
        issues_found = True

    if left_angles and (min(left_angles) < 10 or max(left_angles) > 175):
        print("⚠️  WARNING: Extreme angle values detected")
        print("   This might indicate:")
        print("   - Incorrect landmark detection")
        print("   - Need for angle calculation validation")
        issues_found = True

    # Check for None values
    none_count = sum(1 for a in result['angles'] if a['knee_left'] is None and a['knee_right'] is None)
    if none_count > 0:
        print(f"ℹ️  INFO: {none_count} frames with no angle data (low landmark visibility)")

    if not issues_found:
        print("✅ No major issues detected!")

    # Save detailed results to JSON
    output_file = "data/pipeline_debug_results.json"
    print(f"\n💾 Saving detailed results to: {output_file}")
    Path(output_file).parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"✅ Results saved!")

    return result

if __name__ == "__main__":
    test_pipeline_debug()
