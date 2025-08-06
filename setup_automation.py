#!/usr/bin/env python3
"""
Setup Script for Automated Survey Bot

This script sets up all necessary components for the automated survey bot system.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install required packages."""
    try:
        print("📦 Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = [
        "logs",
        "data", 
        "screenshots",
        "config",
        "src/discord_bot/commands",
        "src/discord_bot/events",
        "src/discord_bot/handlers",
        "src/utils",
        "src/web_automation",
        "src/survey_handler"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create .env file from template."""
    if not os.path.exists(".env"):
        if os.path.exists("env.example"):
            shutil.copy("env.example", ".env")
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your actual credentials")
        else:
            print("❌ env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    return True

def check_discord_token():
    """Check if Discord token is configured."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        token = os.getenv("DISCORD_TOKEN")
        if not token or token == "your_discord_bot_token_here":
            print("⚠️  Discord token not configured in .env file")
            return False
        print("✅ Discord token configured")
        return True
    except ImportError:
        print("❌ python-dotenv not installed")
        return False

def check_cpx_credentials():
    """Check if CPX credentials are configured."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        username = os.getenv("CPX_USERNAME")
        password = os.getenv("CPX_PASSWORD")
        
        if not username or username == "your_cpx_username_here":
            print("⚠️  CPX username not configured in .env file")
            return False
        
        if not password or password == "your_cpx_password_here":
            print("⚠️  CPX password not configured in .env file")
            return False
        
        print("✅ CPX credentials configured")
        return True
    except ImportError:
        print("❌ python-dotenv not installed")
        return False

def setup_firefox():
    """Setup Firefox browser for automation."""
    try:
        print("🦊 Setting up Firefox browser...")
        
        # Check if Firefox is installed
        firefox_paths = [
            "/usr/bin/firefox",
            "/usr/local/bin/firefox",
            "/opt/firefox/firefox",
            "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
        ]
        
        firefox_found = False
        for path in firefox_paths:
            if os.path.exists(path):
                print(f"✅ Firefox found at: {path}")
                firefox_found = True
                break
        
        if not firefox_found:
            print("⚠️  Firefox not found in common locations")
            print("Please install Firefox manually")
        
        # Install geckodriver if needed
        try:
            from selenium import webdriver
            from selenium.webdriver.firefox.service import Service
            from webdriver_manager.firefox import GeckoDriverManager
            
            # Test Firefox setup
            service = Service(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service)
            driver.quit()
            print("✅ Firefox automation setup successful")
            return True
        except Exception as e:
            print(f"❌ Firefox automation setup failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up Firefox: {e}")
        return False

def test_discord_bot():
    """Test Discord bot functionality."""
    try:
        print("🤖 Testing Discord bot...")
        
        # Import bot components
        sys.path.append(str(Path(__file__).parent / "src"))
        
        from src.discord_bot.bot import SurveyBot
        from src.utils.config_manager import ConfigManager
        
        # Load config
        config_manager = ConfigManager("config.yaml")
        config = config_manager.get_config()
        
        # Create bot instance (don't start it)
        bot = SurveyBot(config, None)
        
        print("✅ Discord bot test successful")
        return True
        
    except Exception as e:
        print(f"❌ Discord bot test failed: {e}")
        return False

def test_cpx_automation():
    """Test CPX automation functionality."""
    try:
        print("🔍 Testing CPX automation...")
        
        # Import CPX automation
        from cpx_survey_automation import CPXSurveyAutomation
        
        # Create automation instance (don't start browser)
        automation = CPXSurveyAutomation(headless=True)
        
        print("✅ CPX automation test successful")
        return True
        
    except Exception as e:
        print(f"❌ CPX automation test failed: {e}")
        return False

def create_startup_script():
    """Create startup script for easy launching."""
    script_content = """#!/bin/bash
# Automated Survey Bot Startup Script

echo "Starting Automated Survey Bot..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please run setup first."
    exit 1
fi

# Start the bot
python3 automated_survey_bot.py
"""
    
    with open("start_bot.sh", "w") as f:
        f.write(script_content)
    
    # Make executable
    os.chmod("start_bot.sh", 0o755)
    print("✅ Created startup script: start_bot.sh")

def create_windows_batch():
    """Create Windows batch file for easy launching."""
    batch_content = """@echo off
REM Automated Survey Bot Startup Script

echo Starting Automated Survey Bot...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ❌ .env file not found. Please run setup first.
    pause
    exit /b 1
)

REM Start the bot
python automated_survey_bot.py
pause
"""
    
    with open("start_bot.bat", "w") as f:
        f.write(batch_content)
    
    print("✅ Created Windows batch file: start_bot.bat")

def run_quick_test():
    """Run a quick test of the entire system."""
    print("\n🧪 Running quick system test...")
    
    tests = [
        ("Python version", check_python_version),
        ("Requirements installation", install_requirements),
        ("Discord bot", test_discord_bot),
        ("CPX automation", test_cpx_automation),
        ("Firefox setup", setup_firefox)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

def main():
    """Main setup function."""
    print("🚀 Automated Survey Bot Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Install requirements
    print("\n📦 Installing requirements...")
    if not install_requirements():
        print("❌ Setup failed at requirements installation")
        return
    
    # Create .env file
    print("\n🔧 Setting up environment...")
    if not create_env_file():
        print("❌ Setup failed at environment setup")
        return
    
    # Check credentials
    print("\n🔐 Checking credentials...")
    discord_ok = check_discord_token()
    cpx_ok = check_cpx_credentials()
    
    if not discord_ok or not cpx_ok:
        print("\n⚠️  Please configure your credentials in the .env file:")
        print("   - DISCORD_TOKEN")
        print("   - CPX_USERNAME")
        print("   - CPX_PASSWORD")
        print("\nThen run this setup script again.")
        return
    
    # Setup Firefox
    print("\n🦊 Setting up Firefox...")
    if not setup_firefox():
        print("⚠️  Firefox setup failed, but you can still use the Discord bot")
    
    # Test components
    print("\n🧪 Testing components...")
    test_discord_bot()
    test_cpx_automation()
    
    # Create startup scripts
    print("\n📝 Creating startup scripts...")
    create_startup_script()
    create_windows_batch()
    
    # Run final test
    print("\n🎯 Running final system test...")
    if run_quick_test():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Edit .env file with your actual credentials")
        print("2. Run: python automated_survey_bot.py")
        print("3. Or use: ./start_bot.sh (Linux/Mac) or start_bot.bat (Windows)")
    else:
        print("\n⚠️  Setup completed with warnings. Please check the errors above.")

if __name__ == "__main__":
    main()