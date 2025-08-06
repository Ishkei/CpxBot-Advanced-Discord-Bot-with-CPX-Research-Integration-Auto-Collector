"""
Message Event Handler

Handles Discord message events for tip detection and auto-collection.
"""

import discord
from discord.ext import commands
from loguru import logger
import re
from typing import Optional


class MessageEvent:
    """Handles Discord message events."""
    
    def __init__(self, bot):
        """Initialize the message event handler.
        
        Args:
            bot: Discord bot instance
        """
        self.bot = bot
    
    async def on_message(self, message):
        """Called when a message is sent."""
        try:
            # Ignore bot messages
            if message.author.bot:
                return
            
            # Process commands first
            await self.bot.process_commands(message)
            
            # Check for tips in the message
            await self._check_for_tips(message)
            
            # Check for survey-related keywords
            await self._check_for_survey_keywords(message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _check_for_tips(self, message):
        """Check if a message contains tip information.
        
        Args:
            message: Discord message object
        """
        try:
            # Skip if auto-collector is disabled
            if not self.bot.auto_collector.is_enabled:
                return
            
            # Get channel name
            channel_name = message.channel.name
            
            # Process the message for tips
            tip_info = await self.bot.auto_collector.process_tip_message(
                message.content,
                channel_name
            )
            
            if tip_info:
                logger.info(f"Tip detected in {channel_name}: ${tip_info['amount']:.2f}")
                
                # Collect the tip
                success = await self.bot.auto_collector.collect_tip(tip_info)
                
                if success:
                    # Send confirmation to the channel
                    embed = discord.Embed(
                        title="💰 Tip Collected",
                        color=discord.Color.green(),
                        description=f"Auto-collected tip from {message.author.display_name}"
                    )
                    
                    embed.add_field(
                        name="Amount",
                        value=f"${tip_info['amount']:.2f}",
                        inline=True
                    )
                    embed.add_field(
                        name="Channel",
                        value=channel_name,
                        inline=True
                    )
                    
                    await message.channel.send(embed=embed)
                    
                    # Send notification to tip sender
                    await self._send_tip_confirmation(message.author, tip_info)
                
        except Exception as e:
            logger.error(f"Error checking for tips: {e}")
    
    async def _check_for_survey_keywords(self, message):
        """Check if a message contains survey-related keywords.
        
        Args:
            message: Discord message object
        """
        try:
            # Survey-related keywords
            survey_keywords = [
                "survey", "earn", "money", "cash", "reward", "offer",
                "complete", "participate", "study", "research", "questionnaire"
            ]
            
            message_lower = message.content.lower()
            
            for keyword in survey_keywords:
                if keyword in message_lower:
                    # Check if it's in a survey-related channel
                    if any(channel in message.channel.name.lower() for channel in ["survey", "earn", "offers"]):
                        await self._handle_survey_keyword(message, keyword)
                        break
                        
        except Exception as e:
            logger.error(f"Error checking for survey keywords: {e}")
    
    async def _handle_survey_keyword(self, message, keyword):
        """Handle survey-related keywords in messages.
        
        Args:
            message: Discord message object
            keyword: The keyword that was found
        """
        try:
            embed = discord.Embed(
                title="📋 Survey Opportunity",
                color=discord.Color.blue(),
                description=f"Detected survey-related keyword: **{keyword}**"
            )
            
            embed.add_field(
                name="Action",
                value="Use `!survey start` to begin a survey",
                inline=False
            )
            
            embed.add_field(
                name="Earnings",
                value="Earn money by completing surveys",
                inline=True
            )
            
            embed.add_field(
                name="Status",
                value="Available",
                inline=True
            )
            
            await message.channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error handling survey keyword: {e}")
    
    async def _send_tip_confirmation(self, user, tip_info):
        """Send tip confirmation to the user who sent the tip.
        
        Args:
            user: Discord user who sent the tip
            tip_info: Tip information
        """
        try:
            embed = discord.Embed(
                title="✅ Tip Confirmation",
                color=discord.Color.green(),
                description="Your tip has been collected successfully!"
            )
            
            embed.add_field(
                name="Amount",
                value=f"${tip_info['amount']:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="Status",
                value="Collected",
                inline=True
            )
            
            embed.add_field(
                name="Thank You",
                value="Thanks for the tip! 💰",
                inline=False
            )
            
            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                # User has DMs disabled, ignore
                pass
                
        except Exception as e:
            logger.error(f"Error sending tip confirmation: {e}")
    
    async def _detect_tip_patterns(self, content: str) -> Optional[dict]:
        """Detect tip patterns in message content.
        
        Args:
            content: Message content
            
        Returns:
            Tip information if found, None otherwise
        """
        try:
            # Common tip patterns
            patterns = [
                # $1.50, $5, $10.00
                (r'\$(\d+\.?\d*)', 'dollar_amount'),
                # 1.50 USD, 5 USD
                (r'(\d+\.?\d*)\s*usd', 'usd_amount'),
                # tip 1.50, tip $5
                (r'tip\s*(\$?\d+\.?\d*)', 'tip_command'),
                # 1.50 tip, $5 tip
                (r'(\$?\d+\.?\d*)\s*tip', 'tip_command'),
                # +1.50, +$5
                (r'\+(\$?\d+\.?\d*)', 'positive_amount'),
            ]
            
            for pattern, pattern_type in patterns:
                match = re.search(pattern, content.lower())
                if match:
                    amount_str = match.group(1)
                    
                    # Clean up amount string
                    if amount_str.startswith('$'):
                        amount_str = amount_str[1:]
                    
                    try:
                        amount = float(amount_str)
                        
                        # Check minimum amount
                        if amount >= self.bot.auto_collector.min_amount:
                            return {
                                "amount": amount,
                                "pattern_type": pattern_type,
                                "original_match": match.group(0)
                            }
                    except ValueError:
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting tip patterns: {e}")
            return None
    
    async def _is_valid_tip_channel(self, channel) -> bool:
        """Check if the channel is valid for tip collection.
        
        Args:
            channel: Discord channel object
            
        Returns:
            True if valid for tips, False otherwise
        """
        try:
            # Check channel name for tip-related keywords
            tip_keywords = ["tip", "tips", "money", "earn", "cash", "donate"]
            channel_name = channel.name.lower()
            
            for keyword in tip_keywords:
                if keyword in channel_name:
                    return True
            
            # Check if it's a general channel
            general_channels = ["general", "chat", "main", "lobby"]
            if channel_name in general_channels:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking tip channel validity: {e}")
            return False
    
    async def _log_message_stats(self, message):
        """Log message statistics for analysis.
        
        Args:
            message: Discord message object
        """
        try:
            # Update message count
            await self.bot.db_manager.update_bot_stat("total_messages", 
                (await self.bot.db_manager.get_bot_stat("total_messages") or 0) + 1)
            
            # Update channel activity
            channel_stats = await self.bot.db_manager.get_bot_stat("channel_activity") or {}
            channel_name = message.channel.name
            
            if channel_name not in channel_stats:
                channel_stats[channel_name] = 0
            channel_stats[channel_name] += 1
            
            await self.bot.db_manager.update_bot_stat("channel_activity", channel_stats)
            
        except Exception as e:
            logger.error(f"Error logging message stats: {e}")
    
    async def _check_for_commands(self, message):
        """Check if message contains bot commands.
        
        Args:
            message: Discord message object
        """
        try:
            # Check for prefix
            prefix = self.bot.command_prefix
            
            if message.content.startswith(prefix):
                # Extract command
                command_parts = message.content[len(prefix):].split()
                if command_parts:
                    command_name = command_parts[0].lower()
                    
                    # Log command usage
                    await self.bot.db_manager.update_bot_stat("command_usage", 
                        (await self.bot.db_manager.get_bot_stat("command_usage") or {}) | {command_name: 
                            (await self.bot.db_manager.get_bot_stat("command_usage") or {}).get(command_name, 0) + 1})
                    
        except Exception as e:
            logger.error(f"Error checking for commands: {e}")
    
    async def _handle_error_message(self, message, error):
        """Handle error messages gracefully.
        
        Args:
            message: Discord message object
            error: Error that occurred
        """
        try:
            embed = discord.Embed(
                title="❌ Error",
                color=discord.Color.red(),
                description="An error occurred while processing your message."
            )
            
            embed.add_field(
                name="Error",
                value=str(error)[:100] + "..." if len(str(error)) > 100 else str(error),
                inline=False
            )
            
            embed.add_field(
                name="Help",
                value="Please try again or contact support if the problem persists.",
                inline=False
            )
            
            await message.channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error handling error message: {e}") 