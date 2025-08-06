"""
Auto Collector - Tip.cc Auto-collector Integration

Handles automatic collection of tips from Discord channels and tip.cc integration.
"""

import asyncio
import aiohttp
import json
import random
import time
from typing import Dict, List, Any, Optional
from loguru import logger
from datetime import datetime, timedelta


class AutoCollector:
    """Handles automatic tip collection from Discord channels."""
    
    def __init__(self, config: Dict[str, Any], db_manager):
        """Initialize the auto-collector.
        
        Args:
            config: Configuration dictionary
            db_manager: Database manager instance
        """
        self.config = config
        self.db_manager = db_manager
        self.is_enabled = config["auto_collection"]["enabled"]
        self.collection_interval = config["auto_collection"]["collection_interval"]
        self.min_amount = config["auto_collection"]["min_tip_amount"]
        self.webhook_url = config.get("discord_commands", {}).get("tip_cc", {}).get("webhook_url")
        self.last_collection = None
        
        # Advanced features from GitHub issue
        self.multi_accounting = config.get("auto_collection", {}).get("multi_accounting", False)
        self.accounts = config.get("auto_collection", {}).get("accounts", [])
        self.current_account_index = 0
        
        # Randomized CPM settings
        self.cpm_min = config.get("auto_collection", {}).get("cpm_min", 200)
        self.cpm_max = config.get("auto_collection", {}).get("cpm_max", 400)
        
        # Channel whitelisting
        self.channel_whitelist = config.get("auto_collection", {}).get("channel_whitelist", [])
        self.channel_blacklist = config.get("auto_collection", {}).get("channel_blacklist", [])
        
        # Drop filtering
        self.ignore_drops_under = config.get("auto_collection", {}).get("ignore_drops_under", 0.0)
        self.ignore_thresholds = config.get("auto_collection", {}).get("ignore_thresholds", [])
        
        # Smart delay settings
        self.smart_delay_enabled = config.get("auto_collection", {}).get("smart_delay_enabled", True)
        self.smart_delay_types = config.get("auto_collection", {}).get("smart_delay_types", ["airdrop", "phrasedrop", "mathdrop"])
        
        # Cooldown settings
        self.cooldown_minutes = config.get("auto_collection", {}).get("cooldown_minutes", 3)
        self.last_claim_time = {}
        
        # Thank you messages
        self.thank_you_messages = config.get("auto_collection", {}).get("thank_you_messages", [
            "Thank you!",
            "Thanks!",
            "Appreciate it!",
            "Much appreciated!",
            "Thank you so much!"
        ])
        
    async def collect_tips(self) -> Dict[str, Any]:
        """Collect tips from Discord channels.
        
        Returns:
            Dictionary with collection results
        """
        try:
            if not self.is_enabled:
                return {"success": False, "error": "Auto-collector is disabled"}
            
            logger.info("Starting tip collection...")
            
            # Check cooldown
            if self._is_in_cooldown():
                logger.info("Bot is in cooldown, skipping collection")
                return {"success": True, "amount": 0.0, "count": 0, "message": "In cooldown"}
            
            # Simulate tip collection (in real implementation, this would scan Discord channels)
            collected_amount = await self._simulate_tip_collection()
            
            if collected_amount > 0:
                # Add to database
                await self.db_manager.add_earning(collected_amount, "tip_collection", "completed")
                
                # Log collection
                await self.db_manager.add_auto_collector_log(
                    collected_amount,
                    1,  # Number of tips found
                    "success"
                )
                
                # Send notification
                await self._send_collection_notification(collected_amount)
                
                # Send thank you message
                await self._send_thank_you_message()
                
                # Update cooldown
                self._update_cooldown()
                
                self.last_collection = datetime.now()
                
                logger.info(f"Collected ${collected_amount:.2f} in tips")
                
                return {
                    "success": True,
                    "amount": collected_amount,
                    "count": 1,
                    "message": f"Collected ${collected_amount:.2f} in tips"
                }
            else:
                logger.info("No tips found to collect")
                return {
                    "success": True,
                    "amount": 0.0,
                    "count": 0,
                    "message": "No tips found"
                }
                
        except Exception as e:
            logger.error(f"Error collecting tips: {e}")
            
            # Log error
            await self.db_manager.add_auto_collector_log(
                0.0,
                0,
                "error",
                str(e)
            )
            
            return {"success": False, "error": str(e)}
    
    def _is_in_cooldown(self) -> bool:
        """Check if bot is in cooldown period."""
        if not self.last_claim_time:
            return False
        
        cooldown_duration = timedelta(minutes=self.cooldown_minutes)
        time_since_last_claim = datetime.now() - self.last_claim_time.get("last_claim", datetime.min)
        
        return time_since_last_claim < cooldown_duration
    
    def _update_cooldown(self):
        """Update the cooldown timer."""
        self.last_claim_time["last_claim"] = datetime.now()
    
    async def _send_thank_you_message(self):
        """Send a random thank you message."""
        try:
            if not self.thank_you_messages:
                return
            
            message = random.choice(self.thank_you_messages)
            
            # In a real implementation, this would send to the channel where the tip was collected
            logger.info(f"Sending thank you message: {message}")
            
        except Exception as e:
            logger.error(f"Error sending thank you message: {e}")
    
    def _get_randomized_cpm(self) -> int:
        """Get a randomized CPM value."""
        return random.randint(self.cpm_min, self.cpm_max)
    
    def _should_ignore_drop(self, drop_type: str, amount: float) -> bool:
        """Check if a drop should be ignored based on settings.
        
        Args:
            drop_type: Type of drop (redpacket, airdrop, phrasedrop, etc.)
            amount: Amount of the drop
            
        Returns:
            True if drop should be ignored, False otherwise
        """
        # Check minimum amount threshold
        if amount < self.ignore_drops_under:
            return True
        
        # Check ignore thresholds with percentage chance
        for threshold_config in self.ignore_thresholds:
            if ":" in threshold_config:
                threshold_str, chance_str = threshold_config.split(":")
                try:
                    threshold = float(threshold_str)
                    chance = float(chance_str)
                    
                    if amount < threshold and random.random() < (chance / 100):
                        return True
                except ValueError:
                    continue
        
        # Special handling for redpackets (from GitHub issue)
        if drop_type == "redpacket" and amount == 0.0:
            return True
        
        return False
    
    def _is_valid_channel(self, channel_name: str) -> bool:
        """Check if channel is valid for collection.
        
        Args:
            channel_name: Name of the channel
            
        Returns:
            True if channel is valid, False otherwise
        """
        # Check blacklist first
        if channel_name.lower() in [ch.lower() for ch in self.channel_blacklist]:
            return False
        
        # Check whitelist
        if self.channel_whitelist:
            return channel_name.lower() in [ch.lower() for ch in self.channel_whitelist]
        
        return True
    
    def _get_next_account(self) -> Optional[str]:
        """Get the next account for multi-accounting.
        
        Returns:
            Account token or None if no accounts available
        """
        if not self.multi_accounting or not self.accounts:
            return None
        
        account = self.accounts[self.current_account_index]
        self.current_account_index = (self.current_account_index + 1) % len(self.accounts)
        
        return account
    
    async def _simulate_tip_collection(self) -> float:
        """Simulate tip collection (for demonstration purposes).
        
        Returns:
            Amount collected
        """
        # In a real implementation, this would:
        # 1. Scan Discord channels for tip messages
        # 2. Parse tip amounts and recipients
        # 3. Collect tips that match criteria
        
        # For now, simulate random collection
        import random
        
        # 20% chance of finding a tip
        if random.random() < 0.2:
            # Random amount between $0.01 and $5.00
            amount = random.uniform(0.01, 5.00)
            return round(amount, 2)
        
        return 0.0
    
    async def _send_collection_notification(self, amount: float):
        """Send notification about tip collection.
        
        Args:
            amount: Amount collected
        """
        try:
            if not self.webhook_url:
                return
            
            embed = {
                "title": "💰 Tip Collection Complete",
                "color": 0x00ff00,
                "description": f"Auto-collector found and collected tips!",
                "fields": [
                    {
                        "name": "Amount Collected",
                        "value": f"${amount:.2f}",
                        "inline": True
                    },
                    {
                        "name": "Collection Time",
                        "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "inline": True
                    },
                    {
                        "name": "CPM Used",
                        "value": str(self._get_randomized_cpm()),
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Tip.cc Auto-collector"
                }
            }
            
            payload = {
                "embeds": [embed]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 204:
                        logger.info("Collection notification sent")
                    else:
                        logger.warning(f"Failed to send notification: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error sending collection notification: {e}")
    
    async def enable(self) -> Dict[str, Any]:
        """Enable the auto-collector.
        
        Returns:
            Dictionary with result
        """
        try:
            self.is_enabled = True
            await self.db_manager.update_bot_stat("auto_collector_enabled", True)
            
            logger.info("Auto-collector enabled")
            
            return {"success": True, "message": "Auto-collector enabled"}
            
        except Exception as e:
            logger.error(f"Error enabling auto-collector: {e}")
            return {"success": False, "error": str(e)}
    
    async def disable(self) -> Dict[str, Any]:
        """Disable the auto-collector.
        
        Returns:
            Dictionary with result
        """
        try:
            self.is_enabled = False
            await self.db_manager.update_bot_stat("auto_collector_enabled", False)
            
            logger.info("Auto-collector disabled")
            
            return {"success": True, "message": "Auto-collector disabled"}
            
        except Exception as e:
            logger.error(f"Error disabling auto-collector: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get auto-collector status.
        
        Returns:
            Dictionary with status information
        """
        try:
            stats = await self.db_manager.get_auto_collector_stats()
            
            return {
                "enabled": self.is_enabled,
                "last_collection": self.last_collection.isoformat() if self.last_collection else None,
                "total_collected": stats["total_collected"],
                "total_collections": stats["total_collections"],
                "interval": self.collection_interval,
                "min_amount": self.min_amount,
                "multi_accounting": self.multi_accounting,
                "accounts_count": len(self.accounts),
                "current_cpm": self._get_randomized_cpm(),
                "cooldown_active": self._is_in_cooldown()
            }
            
        except Exception as e:
            logger.error(f"Error getting auto-collector status: {e}")
            return {
                "enabled": False,
                "last_collection": None,
                "total_collected": 0.0,
                "total_collections": 0,
                "interval": self.collection_interval,
                "min_amount": self.min_amount,
                "multi_accounting": False,
                "accounts_count": 0,
                "current_cpm": 0,
                "cooldown_active": False
            }
    
    async def get_settings(self) -> Dict[str, Any]:
        """Get auto-collector settings.
        
        Returns:
            Dictionary with settings
        """
        try:
            return {
                "enabled": self.is_enabled,
                "interval": self.collection_interval,
                "min_amount": self.min_amount,
                "webhook_url": "Configured" if self.webhook_url else None,
                "notifications": bool(self.webhook_url),
                "multi_accounting": self.multi_accounting,
                "accounts_count": len(self.accounts),
                "cpm_min": self.cpm_min,
                "cpm_max": self.cpm_max,
                "channel_whitelist": self.channel_whitelist,
                "channel_blacklist": self.channel_blacklist,
                "ignore_drops_under": self.ignore_drops_under,
                "ignore_thresholds": self.ignore_thresholds,
                "smart_delay_enabled": self.smart_delay_enabled,
                "smart_delay_types": self.smart_delay_types,
                "cooldown_minutes": self.cooldown_minutes,
                "thank_you_messages": self.thank_you_messages
            }
            
        except Exception as e:
            logger.error(f"Error getting auto-collector settings: {e}")
            return {
                "enabled": False,
                "interval": 300,
                "min_amount": 0.01,
                "webhook_url": None,
                "notifications": False,
                "multi_accounting": False,
                "accounts_count": 0,
                "cpm_min": 200,
                "cpm_max": 400,
                "channel_whitelist": [],
                "channel_blacklist": [],
                "ignore_drops_under": 0.0,
                "ignore_thresholds": [],
                "smart_delay_enabled": True,
                "smart_delay_types": ["airdrop", "phrasedrop", "mathdrop"],
                "cooldown_minutes": 3,
                "thank_you_messages": []
            }
    
    async def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update auto-collector settings.
        
        Args:
            settings: New settings
            
        Returns:
            Dictionary with result
        """
        try:
            if "enabled" in settings:
                self.is_enabled = settings["enabled"]
            
            if "interval" in settings:
                self.collection_interval = settings["interval"]
            
            if "min_amount" in settings:
                self.min_amount = settings["min_amount"]
            
            if "multi_accounting" in settings:
                self.multi_accounting = settings["multi_accounting"]
            
            if "accounts" in settings:
                self.accounts = settings["accounts"]
            
            if "cpm_min" in settings:
                self.cpm_min = settings["cpm_min"]
            
            if "cpm_max" in settings:
                self.cpm_max = settings["cpm_max"]
            
            if "channel_whitelist" in settings:
                self.channel_whitelist = settings["channel_whitelist"]
            
            if "channel_blacklist" in settings:
                self.channel_blacklist = settings["channel_blacklist"]
            
            if "ignore_drops_under" in settings:
                self.ignore_drops_under = settings["ignore_drops_under"]
            
            if "ignore_thresholds" in settings:
                self.ignore_thresholds = settings["ignore_thresholds"]
            
            if "smart_delay_enabled" in settings:
                self.smart_delay_enabled = settings["smart_delay_enabled"]
            
            if "smart_delay_types" in settings:
                self.smart_delay_types = settings["smart_delay_types"]
            
            if "cooldown_minutes" in settings:
                self.cooldown_minutes = settings["cooldown_minutes"]
            
            if "thank_you_messages" in settings:
                self.thank_you_messages = settings["thank_you_messages"]
            
            # Save settings to database
            await self.db_manager.update_bot_stat("auto_collector_settings", settings)
            
            logger.info("Auto-collector settings updated")
            
            return {"success": True, "message": "Settings updated"}
            
        except Exception as e:
            logger.error(f"Error updating auto-collector settings: {e}")
            return {"success": False, "error": str(e)}
    
    async def scan_channels_for_tips(self, channels: List[str]) -> List[Dict[str, Any]]:
        """Scan Discord channels for tip messages.
        
        Args:
            channels: List of channel names to scan
            
        Returns:
            List of found tips
        """
        try:
            tips = []
            
            # In a real implementation, this would:
            # 1. Get Discord channel objects
            # 2. Fetch recent messages
            # 3. Parse for tip patterns
            # 4. Extract tip information
            
            # For now, simulate finding tips
            import random
            
            for channel in channels:
                # Check if channel is valid
                if not self._is_valid_channel(channel):
                    continue
                
                # 10% chance of finding a tip in each channel
                if random.random() < 0.1:
                    tip = {
                        "channel": channel,
                        "sender": f"user_{random.randint(1000, 9999)}",
                        "amount": round(random.uniform(0.01, 10.00), 2),
                        "message": "Thanks for the tip!",
                        "timestamp": datetime.now().isoformat()
                    }
                    tips.append(tip)
            
            return tips
            
        except Exception as e:
            logger.error(f"Error scanning channels for tips: {e}")
            return []
    
    async def process_tip_message(self, message_content: str, channel_name: str) -> Optional[Dict[str, Any]]:
        """Process a Discord message to extract tip information.
        
        Args:
            message_content: Content of the Discord message
            channel_name: Name of the channel
            
        Returns:
            Tip information if found, None otherwise
        """
        try:
            # Check if channel is valid
            if not self._is_valid_channel(channel_name):
                return None
            
            # Common tip patterns
            tip_patterns = [
                r'\$(\d+\.?\d*)',  # $1.50
                r'(\d+\.?\d*)\s*usd',  # 1.50 USD
                r'tip\s*(\d+\.?\d*)',  # tip 1.50
                r'(\d+\.?\d*)\s*tip',  # 1.50 tip
                r'\+(\d+\.?\d*)',  # +1.50
            ]
            
            import re
            
            for pattern in tip_patterns:
                match = re.search(pattern, message_content.lower())
                if match:
                    amount_str = match.group(1)
                    
                    # Clean up amount string
                    if amount_str.startswith('$'):
                        amount_str = amount_str[1:]
                    
                    try:
                        amount = float(amount_str)
                        
                        # Check minimum amount
                        if amount >= self.min_amount:
                            return {
                                "amount": amount,
                                "channel": channel_name,
                                "message": message_content,
                                "timestamp": datetime.now().isoformat()
                            }
                    except ValueError:
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing tip message: {e}")
            return None
    
    async def collect_tip(self, tip_info: Dict[str, Any]) -> bool:
        """Collect a specific tip.
        
        Args:
            tip_info: Tip information
            
        Returns:
            True if collected successfully, False otherwise
        """
        try:
            amount = tip_info["amount"]
            
            # Check if we should ignore this drop
            if self._should_ignore_drop("tip", amount):
                logger.info(f"Ignoring tip: ${amount:.2f} (below threshold)")
                return False
            
            # Add to database
            await self.db_manager.add_earning(amount, "tip_collection", "completed")
            
            # Log collection
            await self.db_manager.add_auto_collector_log(
                amount,
                1,
                "success"
            )
            
            logger.info(f"Collected tip: ${amount:.2f} from {tip_info['channel']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error collecting tip: {e}")
            return False 