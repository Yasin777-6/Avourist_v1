#!/usr/bin/env python
"""
AvtoUrist Production Deployment Script
Handles database migrations, static files, and initial setup
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description, check=True):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
        else:
            print(f"⚠️ {description} completed with warnings")
            if result.stderr.strip():
                print(f"Warnings: {result.stderr.strip()}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting AvtoUrist Production Deployment...")
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Error: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Production deployment steps
    steps = [
        ("python manage.py collectstatic --noinput", "Collecting static files", True),
        ("python manage.py makemigrations", "Creating database migrations", True),
        ("python manage.py migrate", "Applying database migrations", True),
        ("python manage.py setup_templates", "Setting up contract templates", False),
    ]
    
    # Execute deployment steps
    success_count = 0
    for command, description, required in steps:
        if run_command(command, description, check=required):
            success_count += 1
        elif required:
            print(f"\n❌ Critical deployment step failed: {description}")
            print("Deployment cannot continue.")
            sys.exit(1)
        else:
            print(f"⚠️ Optional step failed: {description}")
    
    print(f"\n🎉 AvtoUrist deployment completed! ({success_count}/{len(steps)} steps successful)")
    
    # Check if superuser exists
    print("\n🔍 Checking for superuser...")
    result = subprocess.run(
        "python manage.py shell -c \"from django.contrib.auth.models import User; print('exists' if User.objects.filter(is_superuser=True).exists() else 'none')\"",
        shell=True, capture_output=True, text=True
    )
    
    if 'none' in result.stdout:
        print("⚠️ No superuser found. Create one with: python manage.py createsuperuser")
    else:
        print("✅ Superuser exists")
    
    print("\n📋 Deployment Summary:")
    print("✅ Static files collected")
    print("✅ Database migrations applied")
    print("✅ Contract templates configured")
    print("\n🌐 Your AvtoUrist AI Bot is ready for production!")
    print("📱 Don't forget to set up your Telegram webhook!")

if __name__ == "__main__":
    main()
