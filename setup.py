#!/usr/bin/env python
"""
Setup script for MATILDA
This script:
1. Verifies Python version (3.9+)
2. Sets up virtual environment if not present
3. Installs dependencies from requirements.txt
4. Guides user through creating their .env file
5. Runs the connection test
"""

import os
import sys
import platform
import subprocess
import shutil
import venv
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_color(text, color):
    """Print colored text to the terminal"""
    print(f"{color}{text}{Colors.ENDC}")

def check_python_version():
    """Check if Python version is 3.9 or higher"""
    print_color("Checking Python version...", Colors.HEADER)
    
    major, minor, *_ = sys.version_info
    
    if major < 3 or (major == 3 and minor < 9):
        print_color("Error: Python 3.9 or higher is required.", Colors.RED)
        print_color(f"Current Python version: {platform.python_version()}", Colors.RED)
        sys.exit(1)
    
    print_color(f"✓ Python version {platform.python_version()} detected", Colors.GREEN)
    return True

def setup_virtual_environment():
    """Set up a virtual environment if it doesn't exist"""
    print_color("\nSetting up virtual environment...", Colors.HEADER)
    
    venv_dir = Path("venv")
    
    if venv_dir.exists():
        print_color("✓ Virtual environment already exists", Colors.GREEN)
        return venv_dir
    
    print_color("Creating virtual environment...", Colors.CYAN)
    try:
        venv.create(venv_dir, with_pip=True)
        print_color("✓ Virtual environment created successfully", Colors.GREEN)
    except Exception as e:
        print_color(f"Error creating virtual environment: {str(e)}", Colors.RED)
        sys.exit(1)
    
    return venv_dir

def get_venv_python_path(venv_dir):
    """Get the path to the Python executable in the virtual environment"""
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"

def install_dependencies(venv_python):
    """Install dependencies from requirements.txt"""
    print_color("\nInstalling dependencies...", Colors.HEADER)
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print_color("Error: requirements.txt not found", Colors.RED)
        sys.exit(1)
    
    print_color("Installing packages from requirements.txt...", Colors.CYAN)
    print_color("This might take a few minutes...", Colors.YELLOW)
    
    try:
        # Use --no-cache-dir to avoid cache issues and increase timeout
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--no-cache-dir", "--timeout", "120", "-r", "requirements.txt"],
            check=True
        )
        print_color("✓ Dependencies installed successfully", Colors.GREEN)
    except subprocess.CalledProcessError as e:
        print_color(f"Error installing dependencies: {str(e)}", Colors.RED)
        print_color("Try installing dependencies manually with: venv/Scripts/pip install -r requirements.txt", Colors.YELLOW)
        return False
    
    return True

def setup_env_file():
    """Guide user through creating their .env file"""
    print_color("\nSetting up environment variables...", Colors.HEADER)
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        overwrite = input("A .env file already exists. Overwrite it? (y/n): ").lower() == 'y'
        if not overwrite:
            print_color("✓ Using existing .env file", Colors.GREEN)
            return True
    
    if not env_example.exists():
        print_color("Error: .env.example file not found", Colors.RED)
        return False
    
    # Copy example file to .env
    shutil.copy(env_example, env_file)
    print_color(".env file created from template", Colors.CYAN)
    
    # Get Together.ai API key
    print_color("\nTo use MATILDA, you need a Together.ai API key.", Colors.YELLOW)
    print_color("You can get one by signing up at https://together.ai", Colors.YELLOW)
    
    api_key = input("\nEnter your Together.ai API key (or press Enter to add it later): ").strip()
    
    if api_key:
        # Read current .env file
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        # Replace API key placeholder
        env_content = env_content.replace("TOGETHER_API_KEY=your_together_api_key_here", f"TOGETHER_API_KEY={api_key}")
        
        # Write updated content
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print_color("✓ API key added to .env file", Colors.GREEN)
    else:
        print_color("No API key provided. You'll need to add it manually to the .env file later.", Colors.YELLOW)
    
    # Customize username
    username = input("\nEnter your preferred name (or press Enter to use 'User'): ").strip()
    
    if username:
        # Read current .env file
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        # Replace username placeholder
        env_content = env_content.replace("USERNAME=User", f"USERNAME={username}")
        
        # Write updated content
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print_color(f"✓ Username set to '{username}'", Colors.GREEN)
    
    print_color("\n✓ Environment setup complete", Colors.GREEN)
    print_color("You can edit the .env file anytime to change settings.", Colors.CYAN)
    
    return True

def run_connection_test(venv_python):
    """Run the connection test script"""
    print_color("\nRunning connection test...", Colors.HEADER)
    
    test_script = Path("tests") / "test_connection.py"
    if not test_script.exists():
        print_color("Error: Connection test script not found", Colors.RED)
        return False
    
    try:
        print_color("\n" + "=" * 70, Colors.CYAN)
        subprocess.run([str(venv_python), str(test_script)], check=True)
        print_color("=" * 70, Colors.CYAN)
        return True
    except subprocess.CalledProcessError:
        print_color("Connection test failed. Check the error messages above.", Colors.RED)
        return False

def activate_instructions():
    """Show instructions for activating the virtual environment"""
    print_color("\nTo activate the virtual environment:", Colors.HEADER)
    
    if platform.system() == "Windows":
        print_color("Run: .\\venv\\Scripts\\activate", Colors.CYAN)
    else:
        print_color("Run: source venv/bin/activate", Colors.CYAN)

def main():
    """Main setup function"""
    print_color("\n" + "=" * 70, Colors.BLUE)
    print_color("MATILDA - Setup Assistant", Colors.BOLD + Colors.BLUE)
    print_color("=" * 70, Colors.BLUE)
    
    # Check Python version
    check_python_version()
    
    # Setup virtual environment
    venv_dir = setup_virtual_environment()
    venv_python = get_venv_python_path(venv_dir)
    
    # Install dependencies
    if not install_dependencies(venv_python):
        print_color("Setup incomplete. Fix the issues above and try again.", Colors.RED)
        sys.exit(1)
    
    # Setup .env file
    setup_env_file()
    
    # Ask user if they want to run the connection test
    run_test = input("\nDo you want to run the connection test now? (y/n): ").lower() == 'y'
    
    if run_test:
        run_connection_test(venv_python)
    else:
        print_color("\nSkipping connection test.", Colors.YELLOW)
        print_color("You can run it later with: python tests/test_connection.py", Colors.YELLOW)
    
    # Show final instructions
    print_color("\n" + "=" * 70, Colors.GREEN)
    print_color("✨ MATILDA setup complete! ✨", Colors.BOLD + Colors.GREEN)
    print_color("=" * 70, Colors.GREEN)
    
    activate_instructions()
    
    print_color("\nTo start MATILDA:", Colors.HEADER)
    print_color("1. Activate the virtual environment (see above)", Colors.CYAN)
    print_color("2. Run: python src/matilda.py", Colors.CYAN)
    
    print_color("\nEnjoy your personal AI assistant!", Colors.BOLD + Colors.GREEN)

if __name__ == "__main__":
    main()

