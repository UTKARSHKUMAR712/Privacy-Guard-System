"""
Updated Setup script for Privacy Guard System - Python 3.12 Compatible
"""
import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher required")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    
    # Special handling for Python 3.12+
    if version.major == 3 and version.minor >= 12:
        print("ℹ️  Python 3.12+ detected - installing setuptools for distutils compatibility")
    
    return True

def install_setuptools_first():
    """Install setuptools first for Python 3.12+ compatibility"""
    print("📦 Installing setuptools for Python 3.12 compatibility...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "setuptools>=65.0.0"
        ], check=True, capture_output=True, text=True)
        print("  ✅ setuptools installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to install setuptools: {e}")
        return False

def install_requirements():
    """Install Python packages with Python 3.12 compatibility"""
    print("📦 Installing Python packages...")
    
    # Python 3.12 compatible package versions
    packages = [
        "opencv-python>=4.8.0",
        "psutil>=5.9.0", 
        "pywin32>=306",
        "numpy>=1.24.0"
    ]
    
    # Install setuptools first for Python 3.12+
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        if not install_setuptools_first():
            return False
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, check=True)
            print(f"  ✅ {package}")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install {package}")
            print(f"     Error: {e.stderr}")
            
            # Try alternative installation for problematic packages
            if "numpy" in package.lower():
                print("     Trying pre-compiled numpy...")
                try:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", 
                        "--only-binary=all", "numpy"
                    ], check=True)
                    print(f"  ✅ numpy (pre-compiled)")
                except:
                    print(f"  ❌ numpy installation failed completely")
                    return False
            else:
                return False
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing package imports...")
    
    test_imports = [
        ("cv2", "OpenCV"),
        ("psutil", "psutil"),
        ("numpy", "NumPy")
    ]
    
    # Test win32 separately as it might not be available on all systems
    try:
        import win32gui
        test_imports.append(("win32gui", "pywin32"))
    except ImportError:
        print("  ⚠️  pywin32 not available (some features may not work)")
    
    all_passed = True
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            all_passed = False
    
    return all_passed

# Rest of the setup functions remain the same...
def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = ["logs", "config"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"  ✅ Created {directory}/")
        else:
            print(f"  ℹ️  {directory}/ already exists")

def main():
    """Main setup function"""
    print("🛡️  Privacy Guard System - Setup (Python 3.12 Compatible)")
    print("=" * 60)
    
    # Check requirements
    if not check_python_version():
        return False
    
    # Installation steps
    steps = [
        ("Installing Python packages", install_requirements),
        ("Testing imports", test_imports),
        ("Creating directories", create_directories),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            print("\n🔧 Troubleshooting:")
            print("1. Try running: pip install setuptools")
            print("2. Try running: pip install --upgrade pip")
            print("3. Try installing packages individually")
            return False
    
    print("\n🎉 Setup Complete!")
    print("\nNext steps:")
    print("1. Connect your phone via Windows Phone Link")
    print("2. Run: python test_camera.py  (to test cameras)")
    print("3. Run: python privacy_guard.py  (to start monitoring)")
    
    return True

if __name__ == "__main__":
    main()
