"""
Simple test script for the form analyzer.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.analysis.analyzer import analyze_video

def main():
    # Test video path - replace with your actual video
    video_path = 'data/videos/good_form/squat.mp4'
    output_path = 'data/videos/good_form/annotated_squat.mp4'

    print("Processing video...")
    result = analyze_video(
        video_path=video_path,
        output_path=output_path,
        visualize=True
    )

    # Extract results
    form = result['form_result']
    pipeline = result['pipeline_data']

    # Print results
    print("\n" + "="*60)
    print("FORM ANALYSIS RESULTS")
    print("="*60)

    print(f"\nScore: {form.score}/100")
    print(f"Passed: {'YES' if form.passed else 'NO'}")
    print(f"Summary: {form.details['summary']}")

    print(f"\nFrames processed: {pipeline['frames_processed']}")
    print(f"Poses detected: {pipeline['poses_detected']}")

    print("\n" + "-"*60)
    print("FEEDBACK")
    print("-"*60)
    if form.feedback_summary:
        for i, feedback in enumerate(form.feedback_summary, 1):
            print(f"{i}. {feedback}")
    else:
        print("No issues found - excellent form!")

    print("\n" + "-"*60)
    print("ALL VIOLATIONS")
    print("-"*60)
    for violation in form.violations:
        status = "PASSED" if violation.passed else "FAILED"
        print(f"{status} [{violation.severity.value.upper()}] {violation.rule_name}")
        print(f"   {violation.feedback}")
        if violation.details:
            print(f"   Details: {violation.details}")
        print()

    if form.has_critical_issues():
        print("\nWARNING: CRITICAL SAFETY ISSUES DETECTED - Address immediately!")

    print("="*60)
    print(f"Annotated video saved to: {output_path}")
    print("="*60)


if __name__ == '__main__':
    main()
