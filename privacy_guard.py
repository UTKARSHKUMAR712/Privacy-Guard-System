"""
Privacy Guard - Motion Detection Privacy System
Author: Privacy Guard System
Version: 1.0
"""

import cv2
import time
import threading
import sys
import os
import numpy as np
from datetime import datetime

# Import our custom modules
from config import Config
from utils import (
    setup_logging, close_and_minimize, launch_or_activate_app
)

class PrivacyGuard:
    def __init__(self):
        self.config = Config()
        self.logger = setup_logging(self.config.get('log_level'))
        # Motion detection setup
        self.camera = None
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        self.motion_detected = False
        self.running = False
        self.last_detection_time = 0
        # Statistics
        self.detection_count = 0
        self.start_time = datetime.now()
        self.last_frame = None
        self.logger.info("Privacy Guard initialized")

    def initialize_camera(self, camera_index=None):
        """Initialize camera with specified index"""
        if camera_index is None:
            camera_index = self.config.get('camera_index')
        if self.camera:
            self.camera.release()
        self.camera = cv2.VideoCapture(camera_index)
        if not self.camera.isOpened():
            self.logger.error(f"Cannot access camera {camera_index}")
            return False
        # Set camera properties for better performance
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        self.logger.info(f"Camera {camera_index} initialized successfully")
        return True

    def detect_motion(self, frame):
        """Standard motion detection (no masking/curtain exclusion)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        fg_mask = self.background_subtractor.apply(blurred)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        motion_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Minimum area threshold
                motion_area += area
        return motion_area > self.config.get('motion_sensitivity')

    def handle_privacy_breach(self):
        """Handle detected privacy breach"""
        current_time = time.time()
        # Check detection delay to prevent spam
        if current_time - self.last_detection_time < self.config.get('detection_delay'):
            return
        self.last_detection_time = current_time
        self.detection_count += 1
        self.logger.warning(f"Privacy breach detected! (Count: {self.detection_count})")
        # Take and save screenshot
        try:
            if self.last_frame is not None:
                if not os.path.exists("snapshots"):
                    os.makedirs("snapshots")
                snap_name = f"snapshots/breach_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(snap_name, self.last_frame)
                self.logger.info(f"Snapshot saved: {snap_name}")
        except Exception as e:
            self.logger.error(f"Error saving snapshot: {e}")
        if self.config.get('auto_close_apps'):
            threading.Thread(target=self.close_applications, daemon=True).start()

    def close_applications(self):
        """Close designated apps, minimize others, open/focus comet.exe"""
        try:
            close_list = self.config.get('force_close_list')
            closed_apps, minimized = close_and_minimize(
                self.config.get('target_applications'),
                self.config.get('protected_processes'),
                close_list
            )
            if closed_apps:
                self.logger.info(f"Closed applications: {', '.join(closed_apps)}")
            if minimized:
                self.logger.info(f"Minimized windows: {len(minimized)} windows")
            # Open or focus any app or browser 
            launch_or_activate_app("comet.exe")
        except Exception as e:
            self.logger.error(f"Error closing/minimizing or launching comet: {e}")

    def start_monitoring(self):
        """Start the main monitoring loop"""
        if not self.initialize_camera():
            return False
        self.running = True
        self.logger.info("Privacy Guard monitoring started")
        print("🛡️  Privacy Guard Active")
        print("=" * 40)
        print(f"Camera Index: {self.config.get('camera_index')}")
        print(f"Motion Sensitivity: {self.config.get('motion_sensitivity')}")
        print(f"Detection Delay: {self.config.get('detection_delay')}s")
        print("\nControls:")
        print("  'q' - Quit")
        print("  'c' - Change camera")
        print("  's' - Adjust sensitivity")
        print("  't' - Test mode (show detection)")
        print("  'h' - Hide/Show camera feed")
        print("-" * 40)
        show_feed = self.config.get('show_camera_feed')
        test_mode = False
        try:
            while self.running:
                ret, frame = self.camera.read()
                if not ret:
                    self.logger.error("Failed to read camera frame")
                    break
                self.last_frame = frame.copy()
                motion_detected = self.detect_motion(frame)
                if motion_detected:
                    if not test_mode:
                        self.handle_privacy_breach()
                    else:
                        print(f"🚨 Motion detected (TEST MODE) - {datetime.now().strftime('%H:%M:%S')}")
                # Display camera feed if enabled
                if show_feed:
                    status_color = (0, 0, 255) if motion_detected else (0, 255, 0)
                    status_text = "MOTION DETECTED" if motion_detected else "MONITORING"
                    cv2.putText(frame, status_text, (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
                    cv2.putText(frame, f"Detections: {self.detection_count}",
                               (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(frame, f"Uptime: {str(datetime.now() - self.start_time).split('.')[0]}",
                               (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('Privacy Guard - Camera Feed', frame)
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('c'):
                    self.change_camera()
                elif key == ord('s'):
                    self.adjust_sensitivity()
                elif key == ord('t'):
                    test_mode = not test_mode
                    print(f"Test mode: {'ON' if test_mode else 'OFF'}")
                elif key == ord('h'):
                    show_feed = not show_feed
                    if not show_feed:
                        cv2.destroyAllWindows()
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        finally:
            self.stop_monitoring()
        return True

    def change_camera(self):
        """Change camera source"""
        print("\nAvailable cameras:")
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"  {i}: Available")
                cap.release()
        try:
            new_camera = int(input("Enter new camera index: "))
            if self.initialize_camera(new_camera):
                self.config.set('camera_index', new_camera)
                print(f"✅ Switched to camera {new_camera}")
            else:
                print("❌ Failed to switch camera")
        except ValueError:
            print("❌ Invalid camera index")

    def adjust_sensitivity(self):
        """Adjust motion detection sensitivity"""
        current = self.config.get('motion_sensitivity')
        print(f"\nCurrent sensitivity: {current}")
        print("Sensitivity guide:")
        print("  500-1000: Very sensitive (detects small movements)")
        print("  1000-2000: Normal sensitivity")
        print("  2000-5000: Less sensitive (larger movements only)")
        try:
            new_sensitivity = int(input("Enter new sensitivity (500-5000): "))
            if 500 <= new_sensitivity <= 5000:
                self.config.set('motion_sensitivity', new_sensitivity)
                print(f"✅ Sensitivity set to {new_sensitivity}")
            else:
                print("❌ Sensitivity must be between 500-5000")
        except ValueError:
            print("❌ Invalid sensitivity value")

    def stop_monitoring(self):
        """Stop monitoring and cleanup"""
        self.running = False
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        uptime = datetime.now() - self.start_time
        self.logger.info(f"Privacy Guard stopped. Uptime: {uptime}, Detections: {self.detection_count}")
        print(f"\n🛡️  Privacy Guard stopped")
        print(f"Total detections: {self.detection_count}")
        print(f"Uptime: {uptime}")

def main():
    """Main entry point"""
    print("🚀 Privacy Guard System v1.0")
    from utils import check_dependencies
    missing = check_dependencies()
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return
    camera_index = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '--camera' and len(sys.argv) > 2:
            try:
                camera_index = int(sys.argv[2])
            except ValueError:
                print("❌ Invalid camera index")
                return
        elif sys.argv[1] == '--test':
            from test_camera import interactive_camera_test
            interactive_camera_test()
            return
        elif sys.argv[1] == '--help':
            print("\nUsage:")
            print("  python privacy_guard.py                    # Run with default settings")
            print("  python privacy_guard.py --camera 1         # Use specific camera")
            print("  python privacy_guard.py --test             # Test cameras")
            print("  python privacy_guard.py --help             # Show this help")
            return
    guard = PrivacyGuard()
    if camera_index is not None:
        guard.config.set('camera_index', camera_index)
    try:
        guard.start_monitoring()
    except Exception as e:
        guard.logger.error(f"Fatal error: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
