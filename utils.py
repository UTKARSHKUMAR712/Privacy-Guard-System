"""
Utility functions for Privacy Guard System
"""

import logging
import os
import subprocess
import psutil
import time
from datetime import datetime

def setup_logging(log_level="INFO"):
    """Setup logging configuration"""
    if not os.path.exists("logs"):
        os.makedirs("logs")
    log_file = f"logs/privacy_guard_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = ['cv2', 'psutil', 'win32gui', 'numpy']
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    return missing

def get_available_cameras():
    """Detect available cameras"""
    import cv2
    cameras = []
    for i in range(5):  # Check first 5 camera indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append({
                'index': i,
                'name': f'Camera {i}',
                'resolution': (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                               int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            })
            cap.release()
    return cameras

def close_application_by_name(app_name):
    """Close specific application by name"""
    try:
        subprocess.run(['taskkill', '/IM', app_name, '/F'],
                      capture_output=True, check=False)
        return True
    except:
        return False

def close_applications_by_list(app_list, protected_list):
    """Close multiple applications safely"""
    closed_apps = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            process_name = proc.info['name']
            if (process_name in app_list and 
                process_name.lower() not in [p.lower() for p in protected_list]):
                proc.terminate()
                closed_apps.append(process_name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return closed_apps

def minimize_all_windows():
    """Minimize all visible windows"""
    try:
        import win32gui
        import win32con
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text and window_text != "Privacy Guard":
                    hwnds.append((hwnd, window_text))
            return True
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        minimized = []
        for hwnd, title in hwnds:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            minimized.append(title)
        return minimized
    except ImportError:
        return []

def show_notification(title, message):
    """Show Windows notification"""
    try:
        import win32gui
        import win32con
        # Simple message box notification
        win32gui.MessageBox(0, message, title, win32con.MB_OK | win32con.MB_ICONWARNING)
    except:
        print(f"Notification: {title} - {message}")

def close_and_minimize(app_list, protected_list, close_names):
    """Close only close_names apps (by EXE name), minimize all other user-visible windows (but don't minimize closed ones)"""
    import win32gui
    import win32con
    closed_apps = []
    minimized_titles = []
    close_names_lower = [os.path.basename(name).lower() for name in close_names]
    # Close all processes named in close_names ONLY
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            process_name = proc.info['name'].lower()
            if process_name in close_names_lower:
                proc.terminate()
                closed_apps.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Now minimize all windows except the ones in close_names
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            # Don't minimize windows related to the closed process names
            if window_text:
                if not any(name.replace(".exe","") in window_text.lower() for name in close_names_lower):
                    hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    for h in hwnds:
        win32gui.ShowWindow(h, win32con.SW_MINIMIZE)
        minimized_titles.append(win32gui.GetWindowText(h))
    return closed_apps, minimized_titles

def launch_or_activate_app(app_name=None):
    """
    Directly launches comet.exe from absolute path. (No PATH tricks, works always).
    """
    comet_path = r"C:\Users\globa\AppData\Local\Perplexity\Comet\Application\comet.exe"
    try:
        # Preferably bring to front if already running
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == "comet.exe":
                try:
                    import win32gui, win32process
                    pid = proc.info['pid']
                    def enumHandler(hwnd, lParam):
                        try:
                            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                            if found_pid == pid:
                                win32gui.ShowWindow(hwnd, 9)   # SW_RESTORE
                                win32gui.SetForegroundWindow(hwnd)
                        except Exception:
                            pass
                    win32gui.EnumWindows(enumHandler, None)
                    return True
                except Exception:
                    pass
        os.startfile(comet_path)
        return True
    except Exception as e:
        print("Failed to launch or activate comet.exe:", e)
        return False
