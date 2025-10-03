import os
import sys
import subprocess
import shutil

def install_requirements():
    """Install required packages"""
    requirements = [
        'opencv-python',
        'psutil',
        'pywin32'  # Optional: for window minimizing
    ]
    
    print("Installing required packages...")
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, '-pip', 'install', package])
            print(f"✓ Installed {package}")
        except:
            print(f"✗ Failed to install {package}")

def create_startup_batch():
    """Create batch file to run Python script"""
    batch_content = f'''@echo off
cd /d "{os.getcwd()}"
python privacy_guard.py --camera 1
pause
'''
    
    with open('privacy_guard.bat', 'w') as f:
        f.write(batch_content)
    
    print("Created privacy_guard.bat")

def add_to_startup():
    """Add script to Windows startup"""
    startup_folder = os.path.expanduser(
        r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
    )
    
    batch_file = os.path.join(os.getcwd(), 'privacy_guard.bat')
    startup_file = os.path.join(startup_folder, 'privacy_guard.bat')
    
    try:
        shutil.copy2(batch_file, startup_file)
        print(f"✓ Added to startup folder: {startup_file}")
    except Exception as e:
        print(f"✗ Failed to add to startup: {e}")
        print("Manual setup required:")
        print(f"1. Copy {batch_file}")
        print(f"2. To {startup_folder}")

def main():
    print("Setting up Privacy Guard...")
    install_requirements()
    create_startup_batch()
    add_to_startup()
    print("\nSetup complete!")
    print("\nUsage:")
    print("- Run manually: python privacy_guard.py")
    print("- With specific camera: python privacy_guard.py --camera 1")
    print("- Adjust sensitivity: python privacy_guard.py --sensitivity 2000")

if __name__ == "__main__":
    main()
