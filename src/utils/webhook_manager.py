#!/usr/bin/env python3
"""
Webhook Manager for Discord Notifications

Handles multiple webhooks for different types of notifications:
- Survey completions
- Earnings updates
- Error reports
- System status
- Withdrawal confirmations
"""

import os
import requests
import json
from typing import Dict, Optional, Any
from datetime import datetime
from loguru import logger


class WebhookManager:
    """Manages multiple Discord webhooks for different notification types."""
    
    def __init__(self):
        """Initialize the webhook manager."""
        self.webhooks = {
            'surveys': os.getenv('DISCORD_WEBHOOK_SURVEYS'),
            'earnings': os.getenv('DISCORD_WEBHOOK_EARNINGS'),
            'errors': os.getenv('DISCORD_WEBHOOK_ERRORS'),
            'system': os.getenv('DISCORD_WEBHOOK_SYSTEM'),
            'withdrawals': os.getenv('DISCORD_WEBHOOK_WITHDRAWALS')
        }
        
        # Validate webhooks
        self.valid_webhooks = {}
        for webhook_type, url in self.webhooks.items():
            if url and url != 'your_webhook_url_here':
                self.valid_webhooks[webhook_type] = url
                logger.info(f"✅ {webhook_type.capitalize()} webhook configured")
            else:
                logger.warning(f"⚠️  {webhook_type.capitalize()} webhook not configured")
    
    def send_notification(self, webhook_type: str, content: str, embed: Optional[Dict] = None, 
                         username: str = "Survey Bot", avatar_url: Optional[str] = None) -> bool:
        """Send a notification to a specific webhook."""
        try:
            if webhook_type not in self.valid_webhooks:
                logger.warning(f"Webhook type '{webhook_type}' not configured")
                return False
            
            webhook_url = self.valid_webhooks[webhook_type]
            
            # Prepare the message data
            data = {
                "content": content,
                "username": username
            }
            
            if avatar_url:
                data["avatar_url"] = avatar_url
            
            if embed:
                data["embeds"] = [embed]
            
            # Send the webhook
            response = requests.post(webhook_url, json=data, timeout=10)
            
            if response.status_code == 204:
                logger.info(f"✅ {webhook_type.capitalize()} notification sent successfully")
                return True
            else:
                logger.error(f"❌ Failed to send {webhook_type} notification: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending {webhook_type} notification: {e}")
            return False
    
    def send_survey_completion(self, survey_name: str, earnings: float, duration: int) -> bool:
        """Send survey completion notification."""
        embed = {
            "title": "🎉 Survey Completed!",
            "description": f"Successfully completed **{survey_name}**",
            "color": 0x00ff00,
            "fields": [
                {"name": "💰 Earnings", "value": f"${earnings:.2f}", "inline": True},
                {"name": "⏱️ Duration", "value": f"{duration} minutes", "inline": True}
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Survey Bot"}
        }
        
        return self.send_notification('surveys', "", embed)
    
    def send_earnings_update(self, amount: float, total_earnings: float, source: str = "Survey") -> bool:
        """Send earnings update notification."""
        embed = {
            "title": "💰 Earnings Update",
            "description": f"New earnings from **{source}**",
            "color": 0xffd700,
            "fields": [
                {"name": "💵 Amount Earned", "value": f"${amount:.2f}", "inline": True},
                {"name": "🏦 Total Earnings", "value": f"${total_earnings:.2f}", "inline": True}
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Survey Bot"}
        }
        
        return self.send_notification('earnings', "", embed)
    
    def send_error_report(self, error_type: str, error_message: str, context: str = "") -> bool:
        """Send error report notification."""
        embed = {
            "title": "⚠️ Error Report",
            "description": f"**{error_type}** error occurred",
            "color": 0xff0000,
            "fields": [
                {"name": "❌ Error", "value": error_message, "inline": False}
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Survey Bot"}
        }
        
        if context:
            embed["fields"].append({"name": "🔍 Context", "value": context, "inline": False})
        
        return self.send_notification('errors', "", embed)
    
    def send_system_status(self, status: str, message: str, details: Dict[str, Any] = None) -> bool:
        """Send system status notification."""
        color_map = {
            "online": 0x00ff00,
            "offline": 0xff0000,
            "warning": 0xffff00,
            "info": 0x0099ff
        }
        
        embed = {
            "title": f"🤖 System Status: {status.upper()}",
            "description": message,
            "color": color_map.get(status.lower(), 0x0099ff),
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Survey Bot"}
        }
        
        if details:
            for key, value in details.items():
                embed["fields"] = embed.get("fields", [])
                embed["fields"].append({"name": key.title(), "value": str(value), "inline": True})
        
        return self.send_notification('system', "", embed)
    
    def send_withdrawal_confirmation(self, amount: float, method: str, transaction_id: str = None) -> bool:
        """Send withdrawal confirmation notification."""
        embed = {
            "title": "💸 Withdrawal Confirmed",
            "description": f"Withdrawal processed successfully",
            "color": 0x00ff00,
            "fields": [
                {"name": "💰 Amount", "value": f"${amount:.2f}", "inline": True},
                {"name": "🏦 Method", "value": method, "inline": True}
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {"text": "Survey Bot"}
        }
        
        if transaction_id:
            embed["fields"].append({"name": "🆔 Transaction ID", "value": transaction_id, "inline": False})
        
        return self.send_notification('withdrawals', "", embed)
    
    def test_all_webhooks(self) -> Dict[str, bool]:
        """Test all configured webhooks."""
        results = {}
        
        for webhook_type, url in self.valid_webhooks.items():
            try:
                data = {
                    "content": f"🔔 {webhook_type.capitalize()} webhook test successful!",
                    "username": "Survey Bot"
                }
                
                response = requests.post(url, json=data, timeout=10)
                results[webhook_type] = response.status_code == 204
                
                if results[webhook_type]:
                    logger.info(f"✅ {webhook_type.capitalize()} webhook test successful")
                else:
                    logger.error(f"❌ {webhook_type.capitalize()} webhook test failed")
                    
            except Exception as e:
                logger.error(f"❌ {webhook_type.capitalize()} webhook test error: {e}")
                results[webhook_type] = False
        
        return results 