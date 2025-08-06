#!/usr/bin/env python3
"""
Discord Webhook Setup Helper

This script helps you set up Discord webhooks for your Survey Bot.
"""

import os
import requests
from pathlib import Path

def create_webhook_guide():
    """Display step-by-step webhook creation guide."""
    print("🔗 Discord Webhook Setup Guide")
    print("=" * 50)
    print()
    print("📋 Step-by-Step Instructions:")
    print()
    print("1️⃣  Go to your Discord server")
    print("2️⃣  Right-click on the channel where you want notifications")
    print("3️⃣  Select 'Edit Channel'")
    print("4️⃣  Go to the 'Integrations' tab")
    print("5️⃣  Click 'Create Webhook'")
    print("6️⃣  Give it a name (e.g., 'Survey Bot Notifications')")
    print("7️⃣  Copy the Webhook URL")
    print("8️⃣  Paste it in your .env file")
    print()
    print("📝 Example Webhook URL format:")
    print("https://discord.com/api/webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyz1234567890")
    print()
    print("💡 What you'll get notifications for:")
    print("   • Survey completions")
    print("   • Earnings updates")
    print("   • Error reports")
    print("   • System status")
    print("   • Withdrawal confirmations")
    print()

def test_webhook(webhook_url):
    """Test if a webhook URL is valid."""
    try:
        # Test the webhook with a simple message
        data = {
            "content": "🔔 Survey Bot webhook test successful!",
            "username": "Survey Bot",
            "avatar_url": "https://cdn.discordapp.com/emojis/1234567890.png"
        }
        
        response = requests.post(webhook_url, json=data)
        
        if response.status_code == 204:
            print("✅ Webhook test successful!")
            return True
        else:
            print(f"❌ Webhook test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has webhook URL."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please copy env.example to .env and configure it.")
        return False
    
    with open(env_file, "r") as f:
        content = f.read()
        
    if "DISCORD_WEBHOOK_URL" in content:
        # Extract the webhook URL
        for line in content.split("\n"):
            if line.startswith("DISCORD_WEBHOOK_URL="):
                webhook_url = line.split("=", 1)[1].strip()
                if webhook_url and webhook_url != "your_discord_webhook_url_here":
                    print(f"🔗 Found webhook URL: {webhook_url[:50]}...")
                    return webhook_url
                else:
                    print("⚠️  Webhook URL not configured in .env file")
                    return None
    
    print("❌ DISCORD_WEBHOOK_URL not found in .env file")
    return None

def main():
    """Main function."""
    print("🤖 Survey Bot Webhook Setup")
    print("=" * 40)
    print()
    
    # Show setup guide
    create_webhook_guide()
    
    # Check current configuration
    webhook_url = check_env_file()
    
    if webhook_url:
        print("🧪 Testing webhook...")
        if test_webhook(webhook_url):
            print("🎉 Your webhook is working correctly!")
        else:
            print("⚠️  Webhook test failed. Please check your URL.")
    else:
        print("📝 Please set up your webhook URL in the .env file")
        print("   Format: DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...")
    
    print()
    print("📚 For more help, check the README.md file")

if __name__ == "__main__":
    main() 