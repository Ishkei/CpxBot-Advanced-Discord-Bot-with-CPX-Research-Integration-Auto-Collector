#!/usr/bin/env python3
"""
Multiple Webhook Setup Helper

This script helps you set up multiple Discord webhooks for different notification types.
"""

import os
import requests
from pathlib import Path

def create_multiple_webhook_guide():
    """Display step-by-step multiple webhook creation guide."""
    print("🔗 Multiple Discord Webhook Setup Guide")
    print("=" * 60)
    print()
    print("📋 You need to create 5 separate webhooks:")
    print()
    
    webhooks = {
        "surveys": {
            "name": "Survey Completions",
            "description": "Notifications when surveys are finished",
            "channel": "#survey-notifications"
        },
        "earnings": {
            "name": "Earnings Updates", 
            "description": "Notifications when you earn money",
            "channel": "#earnings-updates"
        },
        "errors": {
            "name": "Error Reports",
            "description": "Notifications when something goes wrong",
            "channel": "#error-logs"
        },
        "system": {
            "name": "System Status",
            "description": "Bot startup/shutdown notifications",
            "channel": "#system-status"
        },
        "withdrawals": {
            "name": "Withdrawal Confirmations",
            "description": "Notifications when you withdraw money",
            "channel": "#withdrawal-confirmations"
        }
    }
    
    for i, (webhook_type, info) in enumerate(webhooks.items(), 1):
        print(f"{i}️⃣  **{info['name']}**")
        print(f"    Channel: {info['channel']}")
        print(f"    Purpose: {info['description']}")
        print()
    
    print("📝 Step-by-Step Instructions:")
    print()
    print("1️⃣  Create 5 separate channels in your Discord server:")
    for webhook_type, info in webhooks.items():
        print(f"    • {info['channel']} - {info['description']}")
    print()
    print("2️⃣  For each channel, create a webhook:")
    print("    • Right-click the channel")
    print("    • Select 'Edit Channel'")
    print("    • Go to 'Integrations' tab")
    print("    • Click 'Create Webhook'")
    print("    • Name it appropriately")
    print("    • Copy the Webhook URL")
    print()
    print("3️⃣  Add the URLs to your .env file:")
    print("    DISCORD_WEBHOOK_SURVEYS=your_survey_webhook_url")
    print("    DISCORD_WEBHOOK_EARNINGS=your_earnings_webhook_url")
    print("    DISCORD_WEBHOOK_ERRORS=your_errors_webhook_url")
    print("    DISCORD_WEBHOOK_SYSTEM=your_system_webhook_url")
    print("    DISCORD_WEBHOOK_WITHDRAWALS=your_withdrawal_webhook_url")
    print()

def check_multiple_webhooks():
    """Check if multiple webhooks are configured."""
    webhook_types = ['surveys', 'earnings', 'errors', 'system', 'withdrawals']
    configured_webhooks = {}
    
    for webhook_type in webhook_types:
        env_var = f'DISCORD_WEBHOOK_{webhook_type.upper()}'
        webhook_url = os.getenv(env_var)
        
        if webhook_url and webhook_url != f'your_{webhook_type}_webhook_url':
            configured_webhooks[webhook_type] = webhook_url
            print(f"✅ {webhook_type.capitalize()} webhook configured")
        else:
            print(f"❌ {webhook_type.capitalize()} webhook not configured")
    
    return configured_webhooks

def test_multiple_webhooks(webhooks):
    """Test all configured webhooks."""
    if not webhooks:
        print("⚠️  No webhooks configured to test")
        return
    
    print("\n🧪 Testing configured webhooks...")
    
    for webhook_type, url in webhooks.items():
        try:
            data = {
                "content": f"🔔 {webhook_type.capitalize()} webhook test successful!",
                "username": "Survey Bot"
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 204:
                print(f"✅ {webhook_type.capitalize()} webhook test successful")
            else:
                print(f"❌ {webhook_type.capitalize()} webhook test failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {webhook_type.capitalize()} webhook test error: {e}")

def create_env_template():
    """Create a template .env file with multiple webhooks."""
    template = """# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here

# Discord Webhooks (Create separate webhooks for each channel)
DISCORD_WEBHOOK_SURVEYS=https://discord.com/api/webhooks/SURVEY_WEBHOOK_ID/SURVEY_WEBHOOK_TOKEN
DISCORD_WEBHOOK_EARNINGS=https://discord.com/api/webhooks/EARNINGS_WEBHOOK_ID/EARNINGS_WEBHOOK_TOKEN
DISCORD_WEBHOOK_ERRORS=https://discord.com/api/webhooks/ERRORS_WEBHOOK_ID/ERRORS_WEBHOOK_TOKEN
DISCORD_WEBHOOK_SYSTEM=https://discord.com/api/webhooks/SYSTEM_WEBHOOK_ID/SYSTEM_WEBHOOK_TOKEN
DISCORD_WEBHOOK_WITHDRAWALS=https://discord.com/api/webhooks/WITHDRAWAL_WEBHOOK_ID/WITHDRAWAL_WEBHOOK_TOKEN

# CPX Research Configuration
CPX_USERNAME=your_cpx_username_here
CPX_PASSWORD=your_cpx_password_here
CPX_URL=https://offers.cpx-research.com/index.php?app_id=27806&ext_user_id=533055960609193994_1246050346233757798&secure_hash=49069f12991d2283f61a52dc967dff9f&subid_1=&subid_2=&cpx_message_id=K05VejRYcUJsQUw2ZGFYOUkzaEc0bHJCU3BBOElJSEVoRzFJSForNUo1MD0=

# Database Configuration
DATABASE_URL=sqlite:///data/survey_bot.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/survey_bot.log
"""
    
    with open(".env", "w") as f:
        f.write(template)
    
    print("✅ Created .env template with multiple webhook configuration")

def main():
    """Main function."""
    print("🤖 Multiple Webhook Setup for Survey Bot")
    print("=" * 50)
    print()
    
    # Show setup guide
    create_multiple_webhook_guide()
    
    # Check current configuration
    configured_webhooks = check_multiple_webhooks()
    
    if configured_webhooks:
        print(f"\n✅ Found {len(configured_webhooks)} configured webhooks")
        test_multiple_webhooks(configured_webhooks)
    else:
        print("\n📝 No webhooks configured yet")
        print("Would you like to create a .env template? (y/n): ", end="")
        
        try:
            response = input().lower()
            if response == 'y':
                create_env_template()
                print("✅ Template created! Edit .env with your webhook URLs")
        except KeyboardInterrupt:
            print("\n👋 Setup cancelled")
    
    print()
    print("📚 For bot profile setup, check BOT_PROFILE_SETUP.md")

if __name__ == "__main__":
    main() 