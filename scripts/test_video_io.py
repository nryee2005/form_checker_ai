import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.utils.video_io import validate_video_file, get_video_info, read_video

def test_validate():
    print("=" * 50)
    print("Testing validate_video_file()")
    print("=" * 50)
    # Test with real file
    result = validate_video_file('data/videos/good_form/squat.mp4')
    print(f"✅ Real file: {result}")  # Should be True
    # Test with fake file
    result = validate_video_file('fake.mp4')
    print(f"❌ Fake file: {result}")  # Should be False
    
def test_video_info():
    print("\n" + "=" * 50)
    print("Testing get_video_info()")
    print("=" * 50)
    info = get_video_info('data/videos/good_form/squat.mp4')
    print(f"FPS: {info['fps']}")
    print(f"Resolution: {info['width']}x{info['height']}")
    print(f"Frames: {info['frame_count']}")
    print(f"Duration: {info['duration']:.2f}s")

def test_read_video():
    print("\n" + "=" * 50)
    print("Testing read_video()")
    print("=" * 50)
    cap = read_video('data/videos/good_form/squat.mp4')
    if cap:
        print(f"✅ Good video read")
    else:
        print(f"❌ Bad video read")
    cap.release()

def test_iter_frames():
    print("\n" + "=" * 50)
    print("Testing iter_frames()")
    print("=" * 50)
    frame_count = 0
    for frame in iter_frames('data/videos/good_form/squat.mp4'):
        frame_count += 1
        if frame_count == 1:
            print(f"First frame shape: {frame.shape}")
    print(f"Total frames yielded: {frame_count}")
    
def test_extract_frames():
    pass 

def test_write_video():
    pass
    
if __name__ == "__main__":
    test_validate()
    test_video_info()
    test_read_video()
