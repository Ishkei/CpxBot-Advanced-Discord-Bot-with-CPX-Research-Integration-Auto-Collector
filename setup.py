#!/usr/bin/env python3
"""
Setup Script for Survey Bot

Helps users configure and set up the survey bot with all necessary components.
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess
import json


def print_banner():
    """Print the setup banner."""
    print("=" * 60)
    print("🤖 Survey Bot Setup")
    print("=" * 60)
    print("This script will help you set up the Survey Bot with")
    print("CPX Research integration and tip.cc auto-collector.")
    print("=" * 60)


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print("✅ Python version check passed")
    return True


def create_directories():
    """Create necessary directories."""
    directories = ["logs", "data", "config"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def create_env_file():
    """Create .env file from template."""
    env_template = """# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here

# CPX Research Configuration
CPX_USERNAME=your_cpx_username_here
CPX_PASSWORD=your_cpx_password_here
CPX_URL=https://offers.cpx-research.com/index.php?app_id=27806&ext_user_id=533055960609193994_1246050346233757798&secure_hash=49069f12991d2283f61a52dc967dff9f&subid_1=&subid_2=&cpx_message_id=K05VejRYcUJsQUw2ZGFYOUkzaEc0bHJCU3BBOElJSEVoRzFJSForNUo1MD0=

# Tip.cc Auto-collector Integration
TIP_CC_WEBHOOK_URL=your_tip_cc_webhook_url_here

# Database Configuration
DATABASE_URL=sqlite:///data/survey_bot.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/survey_bot.log

# Security Settings
ENCRYPTION_KEY=your_encryption_key_here

# Web Scraping Settings
SELENIUM_HEADLESS=true
BROWSER_TIMEOUT=30
MAX_RETRY_ATTEMPTS=3

# Survey Bot Settings
MIN_EARNINGS_THRESHOLD=0.10
MAX_SURVEY_TIME=30
AUTO_ACCEPT_SURVEYS=true
RANDOM_DELAYS=true

# Auto-Collection Settings
AUTO_COLLECTION_ENABLED=true
COLLECTION_INTERVAL=300
MIN_TIP_AMOUNT=0.01
"""
    
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_template)
        print("✅ Created .env file")
        print("⚠️  Please edit .env with your actual credentials")
    else:
        print("✅ .env file already exists")


def create_config_file():
    """Create config.yaml file."""
    config_template = """# Survey Bot Configuration

# Discord Bot Configuration
discord:
  token: ${DISCORD_TOKEN}
  guild_id: ${DISCORD_GUILD_ID}
  prefix: "!"
  intents:
    - message_content
    - guilds
    - guild_messages
    - guild_reactions
    - guild_members

# Channel Configuration
channels:
  airdrops: "airdrops"
  mines: "mines"
  lakes: "lakes"
  alley: "alley"
  stash: "stash"
  nexus: "nexus"
  arena: "arena"
  shop: "shop"
  bank: "bank"

# CPX Research Configuration
cpx_research:
  base_url: "https://offers.cpx-research.com/index.php"
  app_id: "27806"
  ext_user_id: "533055960609193994_1246050346233757798"
  secure_hash: "49069f12991d2283f61a52dc967dff9f"
  username: ${CPX_USERNAME}
  password: ${CPX_PASSWORD}
  
  # Survey Completion Settings
  survey_settings:
    min_earnings: 0.10  # Minimum earnings to accept survey
    max_time: 30        # Maximum time in minutes
    auto_accept: true   # Automatically accept surveys
    random_delays: true # Add random delays to appear human
    
  # Survey Types to Target
  survey_types:
    - "gaming"
    - "technology"
    - "entertainment"
    - "sports"
    - "shopping"
    - "general"

# Web Scraping Configuration
web_scraper:
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  timeout: 30
  retry_attempts: 3
  headless: true
  window_size:
    width: 1920
    height: 1080

# Database Configuration
database:
  url: "sqlite:///data/survey_bot.db"
  backup_interval: 24  # hours

# Logging Configuration
logging:
  level: "INFO"
  file: "logs/survey_bot.log"
  max_size: "10MB"
  backup_count: 5

# Auto-Collection Settings
auto_collection:
  enabled: true
  tip_cc_integration: true
  collection_interval: 300  # seconds
  min_tip_amount: 0.01

# Discord Commands Integration
discord_commands:
  # Tip.cc Auto-collector Integration
  tip_cc:
    enabled: true
    webhook_url: ${TIP_CC_WEBHOOK_URL}
    
  # Survey Commands
  survey_commands:
    - "survey"
    - "earnings"
    - "status"
    - "withdraw"
    
  # Gaming Commands (from the Discord server)
  gaming_commands:
    - "setup"
    - "profile"
    - "mine"
    - "fish"
    - "rob"
    - "open"
    - "refine"
    - "learn"
    - "craft"
    - "blow-up"
    - "enchant"
    - "shop"
    - "sell"
    - "offers"
    - "withdraw"
    - "pet"
    - "feed"
    - "switch"
    - "battle"
    - "tip"
    - "rain"
    - "magic-storm"
    - "invites"
    - "leaderboards"
    - "codex"
    - "emoji"
    - "flex"
    - "pings"

# Security Settings
security:
  rate_limiting: true
  max_requests_per_minute: 60
  ip_rotation: false
  proxy_enabled: false

# Notification Settings
notifications:
  discord_webhook: ${DISCORD_WEBHOOK_URL}
  email_notifications: false
  earnings_threshold: 1.00  # Notify when earnings reach this amount
"""
    
    if not os.path.exists("config.yaml"):
        with open("config.yaml", "w") as f:
            f.write(config_template)
        print("✅ Created config.yaml file")
    else:
        print("✅ config.yaml file already exists")


def check_chrome():
    """Check if Chrome browser is available."""
    try:
        # Try to find Chrome
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                print("✅ Chrome browser found")
                return True
        
        print("⚠️  Chrome browser not found in standard locations")
        print("   Please install Chrome for web scraping functionality")
        return False
        
    except Exception as e:
        print(f"❌ Error checking Chrome: {e}")
        return False


def print_setup_instructions():
    """Print setup instructions."""
    print("\n" + "=" * 60)
    print("📋 Setup Instructions")
    print("=" * 60)
    
    print("\n1. 🔧 Configure Environment Variables:")
    print("   Edit the .env file with your credentials:")
    print("   - DISCORD_TOKEN: Your Discord bot token")
    print("   - DISCORD_GUILD_ID: Your Discord server ID")
    print("   - CPX_USERNAME: Your CPX Research username")
    print("   - CPX_PASSWORD: Your CPX Research password")
    
    print("\n2. 🤖 Discord Bot Setup:")
    print("   a. Go to https://discord.com/developers/applications")
    print("   b. Create a new application")
    print("   c. Add a bot to your application")
    print("   d. Copy the bot token to .env")
    print("   e. Invite the bot to your server")
    
    print("\n3. 🌐 CPX Research Setup:")
    print("   a. Create an account at CPX Research")
    print("   b. Add your credentials to .env")
    print("   c. Configure survey preferences in config.yaml")
    
    print("\n4. 💰 Tip.cc Integration (Optional):")
    print("   a. Set up tip.cc webhook URL")
    print("   b. Configure auto-collector settings")
    
    print("\n5. 🚀 Run the Bot:")
    print("   python main.py")
    
    print("\n6. 📚 Documentation:")
    print("   Read README.md for detailed instructions")
    
    print("\n" + "=" * 60)


def run_tests():
    """Run basic tests to verify setup."""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test imports
        import discord
        import yaml
        import loguru
        import selenium
        print("✅ All required modules imported successfully")
        
        # Test config loading
        if os.path.exists("config.yaml"):
            with open("config.yaml", "r") as f:
                yaml.safe_load(f)
            print("✅ Configuration file is valid")
        
        # Test database directory
        if os.path.exists("data"):
            print("✅ Database directory exists")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        return
    
    # Create configuration files
    create_env_file()
    create_config_file()
    
    # Check Chrome
    check_chrome()
    
    # Run tests
    run_tests()
    
    # Print instructions
    print_setup_instructions()
    
    print("\n🎉 Setup completed successfully!")
    print("Please configure your credentials and run 'python main.py' to start the bot.")


if __name__ == "__main__":
    main() 