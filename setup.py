#!/usr/bin/env python3
"""
Setup script for Video Recorder with AI Transcription
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    print("🚀 Setting up Video Recorder with AI Transcription")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Create virtual environment
    if not run_command("python3.11 -m venv venv", "Creating virtual environment"):
        print("💡 Try: python3 -m venv venv")
        if not run_command("python3 -m venv venv", "Creating virtual environment (fallback)"):
            sys.exit(1)
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("DEEPGRAM_API_KEY=your_api_key_here\n")
        print("✅ Created .env file")
        print("⚠️  Please edit .env and add your Deepgram API key")
    else:
        print("✅ .env file already exists")
    
    # Create uploads directory
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        print("✅ Created uploads directory")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file and add your Deepgram API key")
    print("2. Run: source venv/bin/activate (or venv\\Scripts\\activate on Windows)")
    print("3. Run: python app.py")
    print("4. Open: http://127.0.0.1:5000")

if __name__ == "__main__":
    main()
