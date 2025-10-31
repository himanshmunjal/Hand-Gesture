# setup.py
"""
Installation and Setup Script for Nokia Snake Game
Automatically installs all required dependencies
"""
import subprocess
import sys

# mapping pip package -> import name for existence check
PACKAGE_IMPORT_MAP = {
    "opencv-python": "cv2",
    "mediapipe": "mediapipe",
    "numpy": "numpy",
    "pygame": "pygame",
}

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install {package}")
        return False

def check_package(package):
    import importlib
    import_name = PACKAGE_IMPORT_MAP.get(package.split('>=')[0], package.split('>=')[0])
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False

def main():
    print("🐍 Nokia Snake Game - Setup Script")
    print("=" * 50)

    packages = [
        "opencv-python>=4.8.0",
        "mediapipe>=0.10.0",
        "numpy>=1.24.0",
        "pygame>=2.4.0"
    ]

    print("Checking and installing required packages...\n")
    all_success = True

    for package in packages:
        package_name = package.split('>=')[0]
        print(f"Checking {package_name}...")
        if not check_package(package_name):
            print(f"Installing {package}...")
            if not install_package(package):
                all_success = False
        else:
            print(f"✓ {package_name} already installed")

    print("\n" + "=" * 50)
    if all_success:
        print("🎉 Setup completed successfully!\n")
        print("To start the game, run:")
        print("  python main.py\n")
    else:
        print("❌ Some packages failed to install.")
        print("Please install them manually using:")
        print("  pip install -r requirements.txt")

if __name__ == "__main__":
    main()
