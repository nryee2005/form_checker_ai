"""
Test pipeline performance with different frame skip values.
Helps understand speed vs accuracy tradeoffs.
"""
import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pose.pipeline import process_video

def test_pipeline_performance():
    """Test pipeline with different frame_skip values."""

    # TODO: Update video path
    video_path = "data/videos/good_form/squat.mp4"

    if not Path(video_path).exists():
        print(f"❌ Error: Video not found at {video_path}")
        return

    print("⚡ PERFORMANCE TEST")
    print("=" * 60)
    print(f"Testing video: {video_path}")
    print()

    # Test with different frame_skip values
    skip_values = [0, 1, 2, 5]
    results = []

    for frame_skip in skip_values:
        print(f"Testing with frame_skip={frame_skip}...")

        start_time = time.time()

        result = process_video(
            video_path=video_path,
            visualize=False,
            frame_skip=frame_skip
        )

        elapsed_time = time.time() - start_time

        results.append({
            'frame_skip': frame_skip,
            'time': elapsed_time,
            'frames_processed': result['frames_processed'],
            'poses_detected': result['poses_detected']
        })

        print(f"  ✓ Completed in {elapsed_time:.2f}s")
        print()

    # Print comparison table
    print("\n📊 PERFORMANCE COMPARISON:")
    print("=" * 60)
    print(f"{'frame_skip':<12} {'Time (s)':<10} {'Frames':<10} {'Poses':<10} {'FPS':<10}")
    print("-" * 60)

    for r in results:
        fps = r['frames_processed'] / r['time'] if r['time'] > 0 else 0
        print(f"{r['frame_skip']:<12} {r['time']:<10.2f} {r['frames_processed']:<10} {r['poses_detected']:<10} {fps:<10.1f}")

    # Calculate speedup
    print("\n⚡ SPEEDUP ANALYSIS:")
    print("-" * 60)
    baseline_time = results[0]['time']

    for r in results[1:]:
        speedup = baseline_time / r['time'] if r['time'] > 0 else 0
        frames_ratio = r['frames_processed'] / results[0]['frames_processed']
        print(f"frame_skip={r['frame_skip']}: {speedup:.2f}x faster, processes {frames_ratio*100:.0f}% of frames")

    print("\n💡 RECOMMENDATIONS:")
    print("-" * 60)
    print("• frame_skip=0: Best accuracy, slowest")
    print("• frame_skip=1: 2x faster, still good for most cases")
    print("• frame_skip=2: 3x faster, acceptable for quick analysis")
    print("• frame_skip=5+: Very fast, but may miss important frames")

    return results

if __name__ == "__main__":
    test_pipeline_performance()
