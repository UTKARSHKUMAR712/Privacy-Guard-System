"""
Advanced Camera Testing Utility for Privacy Guard System
(with motion, face, measurement and more — NO barcode)
"""

import cv2
import sys
import time
import numpy as np
from utils import get_available_cameras, setup_logging

# -------- Line measurement state --------
measuring = False
measure_start = None
measure_end = None
last_line_length = None

def list_standard_resolutions():
    return [
        (640, 480),
        (800, 600),
        (1024, 768),
        (1280, 720),
        (1920, 1080),
        (2560, 1440)
    ]

def print_camera_properties(cap):
    print("\nCamera Properties:")
    try:
        print(f"  Brightness: {cap.get(cv2.CAP_PROP_BRIGHTNESS)}")
        print(f"  Contrast:   {cap.get(cv2.CAP_PROP_CONTRAST)}")
        print(f"  FPS:        {cap.get(cv2.CAP_PROP_FPS)}")
        print(f"  Resolution: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        print(f"  Auto Gain:  {cap.get(cv2.CAP_PROP_AUTO_EXPOSURE)}")
    except Exception:
        pass

def test_all_cameras():
    logger = setup_logging()
    cameras = get_available_cameras()
    if not cameras:
        print("❌ No cameras found!")
        return False
    print("📷 Available Cameras:")
    print("-" * 50)
    for camera in cameras:
        print(f"Camera {camera['index']}: {camera['resolution'][0]}x{camera['resolution'][1]}")
        if camera['index'] == 0:
            print("  └─ Likely: Laptop built-in camera")
        else:
            print("  └─ Likely: External/Phone camera")
    return True

def show_frame_modes(frame, mode):
    if mode == "gray":
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    elif mode == "edge":
        return cv2.Canny(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 100, 200)
    return frame

def detect_motion_rects(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (21, 21), 0)
    if not hasattr(detect_motion_rects, "bg_subtractor"):
        detect_motion_rects.bg_subtractor = cv2.createBackgroundSubtractorMOG2()
    fg_mask = detect_motion_rects.bg_subtractor.apply(blurred)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for cnt in contours:
        if cv2.contourArea(cnt) > 600:
            x, y, w, h = cv2.boundingRect(cnt)
            boxes.append((x, y, w, h))
    return boxes

def detect_faces(frame, face_cascade):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.15, 6, minSize=(60,60))
    return faces

# ----------- Mouse callback for measurement: -----------
def measure_callback(event, x, y, flags, param):
    global measuring, measure_start, measure_end, last_line_length
    if measuring:
        if event == cv2.EVENT_LBUTTONDOWN:
            measure_start = (x, y)
            measure_end = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and measure_start is not None:
            measure_end = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            measure_end = (x, y)
            if measure_start and measure_end:
                dx = measure_end[0] - measure_start[0]
                dy = measure_end[1] - measure_start[1]
                last_line_length = np.sqrt(dx*dx + dy*dy)
            measuring = False

def test_specific_camera(camera_index):
    global measuring, measure_start, measure_end, last_line_length

    print(f"\n🔍 Testing Camera {camera_index}...")

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ Cannot access camera {camera_index}")
        return False

    print("Keys: [q]=quit [s]=screenshot [b]=burst [c]=color/gray/edge [r]=res [i]=info [f]=face [m]=measure")

    print_camera_properties(cap)

    frame_count = 0
    color_mode = "color"
    auto_burst = False
    burst_counter = 0
    burst_start_time = None
    last_time = time.time()
    fps_samples = []
    show_face = False

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    std_res = list_standard_resolutions()
    res_idx = 0
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    cv2.namedWindow(f'Camera {camera_index} Test', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(f'Camera {camera_index} Test', measure_callback)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break

        frame_count += 1

        frame_disp = show_frame_modes(frame, color_mode)
        disp = frame_disp if color_mode == "color" else cv2.cvtColor(frame_disp, cv2.COLOR_GRAY2BGR)

        # --- Motion Detection ---
        if color_mode in ("color", "gray"):
            boxes = detect_motion_rects(frame)
            for (x, y, w, h) in boxes:
                cv2.rectangle(disp, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # --- Face Detection ---
        if show_face and color_mode == "color":
            faces = detect_faces(frame, face_cascade)
            for (x, y, w, h) in faces:
                cv2.rectangle(disp, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(disp, "Face", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

        # --- Manual Measurement (draw line and show px) ---
        if measure_start and measure_end:
            cv2.line(disp, measure_start, measure_end, (200, 100, 255), 3)
            if last_line_length:
                cv2.putText(disp, f"Length: {last_line_length:.1f} px",
                            (measure_end[0], measure_end[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (200, 100, 255), 2)

        # FPS calc
        now = time.time()
        fps = 1. / (now - last_time) if frame_count > 1 else 0
        fps_samples.append(fps)
        last_time = now

        overlay_text = f"Frame {frame_count}  FPS:{fps:.1f}  Mode:{color_mode.upper()}  Res:{width}x{height}"
        help_line = "Keys: [q]=quit [s]=screenshot [b]=burst [c]=color/gray/edge [r]=res [i]=info [f]=face [m]=measure (click-drag)"
        cv2.putText(disp, overlay_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (20, 255, 20), 2)
        cv2.putText(disp, help_line, (10, disp.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.53, (255, 255, 100), 1)

        cv2.imshow(f'Camera {camera_index} Test', disp)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"camera_{camera_index}_shot_{frame_count}.jpg"
            cv2.imwrite(filename, frame)
            print(f"📸 Screenshot saved: {filename}")
        elif key == ord('b'):
            if not auto_burst:
                print("⏺️ Burst screenshots started.")
                auto_burst = True
                burst_counter = 0
                burst_start_time = time.time()
            else:
                print("⏹️ Burst screenshots stopped.")
                auto_burst = False
        elif key == ord('c'):
            if color_mode == "color":
                color_mode = "gray"
            elif color_mode == "gray":
                color_mode = "edge"
            else:
                color_mode = "color"
            print(f"Color mode: {color_mode}")
        elif key == ord('r'):
            res_idx = (res_idx + 1) % len(std_res)
            new_w, new_h = std_res[res_idx]
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, new_w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, new_h)
            print(f"Switched to resolution: {new_w}x{new_h}")
            width, height = new_w, new_h
        elif key == ord('i'):
            print_camera_properties(cap)
        elif key == ord('f'):
            show_face = not show_face
            print("Face detection:", "ON" if show_face else "OFF")
        elif key == ord('m'):
            print("Click and drag to measure (pixels).")
            measuring, measure_start, measure_end, last_line_length = True, None, None, None

        if auto_burst and frame_count % 10 == 0:
            filename = f"camera_{camera_index}_burst_{burst_counter}.jpg"
            cv2.imwrite(filename, frame)
            print(f"🖼️ Burst saved: {filename}")
            burst_counter += 1

    cap.release()
    cv2.destroyAllWindows()
    if fps_samples:
        print(f"Average FPS: {sum(fps_samples)/len(fps_samples):.2f}")
        print(f"Frames tested: {len(fps_samples)}")
        if auto_burst and burst_start_time:
            elapsed = time.time() - burst_start_time
            print(f"Burst duration: {elapsed:.2f} sec, {burst_counter} burst images saved")
    return True

def interactive_camera_test():
    print("🚀 Privacy Guard - Camera Test Utility")
    print("=" * 50)
    if not test_all_cameras():
        return
    while True:
        print("\nOptions:")
        print("1. Test specific camera")
        print("2. Scan for new cameras")
        print("3. Exit")
        choice = input("\nEnter choice (1-3): ").strip()
        if choice == "1":
            try:
                camera_idx = int(input("Enter camera index: "))
                test_specific_camera(camera_idx)
            except ValueError:
                print("❌ Invalid camera index")
        elif choice == "2":
            test_all_cameras()
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
            test_specific_camera(camera_index)
        except ValueError:
            print("Usage: python test_camera.py [camera_index]")
    else:
        interactive_camera_test()
