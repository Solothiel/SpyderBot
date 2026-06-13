import subprocess
import sys

''' This creates a list of packages to install.
    Defines the function named  `install_requirements`.
    Creates a list of package names to install:
        customtkinter - a gui toolkit.
        requests - HTTP library for making web requests.
        beautifulsoup4 - HTML/XML parsing library.
'''

def install_requirements():
    packages = ['customtkinter', 'requests', 'beautifulsoup4']
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print("All requirements installed successfully!")

if __name__ == "__main__":
    install_requirements()
