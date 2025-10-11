#!/usr/bin/env python
"""
AvtoUrist Project Setup Script
Automates the initial setup of the Django project
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting AvtoUrist AI Bot Setup...")
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Error: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("python -m pip install -r requirements.txt", "Installing Python dependencies"),
        ("python manage.py makemigrations", "Creating database migrations"),
        ("python manage.py migrate", "Applying database migrations"),
        ("python manage.py setup_templates", "Setting up contract templates"),
    ]
    
    # Execute setup steps
    for command, description in steps:
        if not run_command(command, description):
            print(f"\n❌ Setup failed at step: {description}")
            print("Please fix the error and run the script again.")
            sys.exit(1)
    
    print("\n🎉 AvtoUrist AI Bot setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Update your .env file with correct API keys")
    print("3. Set up your Telegram webhook: POST /telegram/set-webhook/")
    print("4. Start the development server: python manage.py runserver")
    print("\n🌐 Access the admin panel at: http://localhost:8000/admin/")
    print("📱 Your Telegram bot is ready to receive messages!")

if __name__ == "__main__":
    main()
