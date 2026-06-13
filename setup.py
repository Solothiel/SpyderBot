import subprocess
import sys


def install_requirements():
    # The updated list of packages needed for our crawler and custom designs
    packages = ['requests', 'beautifulsoup4', 'ttkbootstrap', 'pillow', 'pyinstaller']

    print("Starting installation of required dependencies...")
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"Error occurred while trying to install {package}.")

    print("\nAll requirements installed successfully!")


if __name__ == "__main__":
    install_requirements()
