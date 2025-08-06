#!/usr/bin/env python3
"""
CPX Research Integration Setup for CpxBot

This script helps set up the CPX Research integration for your CpxBot.
"""

import os
import json
import yaml
from pathlib import Path


def setup_cpx_integration():
    """Setup CPX Research integration for CpxBot."""
    
    print("🚀 Setting up CPX Research Integration for CpxBot...\n")
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: Please run this script from the CpxBot directory")
        return False
    
    # Load current config
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("❌ Error: config.yaml not found")
        return False
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Update CPX Research configuration
    cpx_config = {
        "base_url": "https://offers.cpx-research.com/index.php",
        "app_id": "27806",
        "ext_user_id": "533055960609193994_1246050346233757798",
        "secure_hash": "49069f12991d2283f61a52dc967dff9f",
        "username": "${CPX_USERNAME}",
        "password": "${CPX_PASSWORD}",
        
        # Survey Completion Settings
        "survey_settings": {
            "min_earnings": 0.10,
            "max_time": 30,
            "auto_accept": True,
            "random_delays": True
        },
        
        # Survey Types to Target
        "survey_types": [
            "gaming",
            "technology", 
            "entertainment",
            "sports",
            "shopping",
            "general"
        ]
    }
    
    # Update the config
    config["cpx_research"] = cpx_config
    
    # Save updated config
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print("✅ Updated config.yaml with CPX Research settings")
    
    # Create environment template
    env_template = """# CpxBot Environment Variables

# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here

# CPX Research Configuration
CPX_USERNAME=your_cpx_username_here
CPX_PASSWORD=your_cpx_password_here

# Optional: Google API for AI features
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Tip.cc Integration
TIP_CC_WEBHOOK_URL=your_tip_cc_webhook_url_here

# Optional: Discord Webhook for notifications
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
"""
    
    env_path = Path(".env")
    if not env_path.exists():
        with open(env_path, 'w') as f:
            f.write(env_template)
        print("✅ Created .env template file")
    else:
        print("⚠️  .env file already exists - check if CPX credentials are set")
    
    # Create CPX integration info
    cpx_info = {
        "discord_server": "https://discord.gg/VXKfzW4B",
        "cpx_url": "https://offers.cpx-research.com/index.php?app_id=27806&ext_user_id=533055960609193994_1246050346233757798",
        "user_id": "533055960609193994",
        "setup_required": True,
        "commands": {
            "setup": "/setup - Create your character",
            "offers": "/offers - Access CPX Research surveys", 
            "withdraw": "/withdraw - Withdraw earnings",
            "cpx_status": "/cpx_status - Check CPX configuration"
        }
    }
    
    with open("cpx_integration.json", 'w') as f:
        json.dump(cpx_info, f, indent=2)
    
    print("✅ Created cpx_integration.json with integration info")
    
    return True


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("\n🔍 Checking dependencies...")
    
    try:
        import discord
        print("✅ discord.py")
    except ImportError:
        print("❌ discord.py - Run: pip install -r requirements.txt")
    
    try:
        import selenium
        print("✅ selenium")
    except ImportError:
        print("❌ selenium - Run: pip install -r requirements.txt")
    
    try:
        import yaml
        print("✅ pyyaml")
    except ImportError:
        print("❌ pyyaml - Run: pip install -r requirements.txt")
    
    try:
        from loguru import logger
        print("✅ loguru")
    except ImportError:
        print("❌ loguru - Run: pip install -r requirements.txt")


def print_setup_instructions():
    """Print setup instructions."""
    print("\n📋 Setup Instructions:")
    print("=" * 50)
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("2. Configure environment variables:")
    print("   - Edit .env file with your credentials")
    print("   - Set DISCORD_TOKEN and DISCORD_GUILD_ID")
    print("   - Set CPX_USERNAME and CPX_PASSWORD (optional)")
    print()
    print("3. Join Discord server:")
    print("   https://discord.gg/VXKfzW4B")
    print()
    print("4. Set up your character:")
    print("   - Use /setup in Discord")
    print("   - Then use /offers to access surveys")
    print()
    print("5. Run the bot:")
    print("   python main.py")
    print()
    print("6. Available commands:")
    print("   - /offers - Start CPX Research surveys")
    print("   - /withdraw - Withdraw earnings")
    print("   - /cpx_status - Check configuration")
    print("   - /setup - Set up character")


def main():
    """Main setup function."""
    print("🎮 CpxBot CPX Research Integration Setup")
    print("=" * 50)
    
    # Run setup
    if setup_cpx_integration():
        check_dependencies()
        print_setup_instructions()
        
        print("\n✨ Setup complete! Your CpxBot is ready for CPX Research integration.")
        print("\n🎯 Next steps:")
        print("   1. Configure your .env file")
        print("   2. Join the Discord server")
        print("   3. Set up your character with /setup")
        print("   4. Start earning with /offers")
    else:
        print("\n❌ Setup failed. Please check the errors above.")


if __name__ == "__main__":
    main() 