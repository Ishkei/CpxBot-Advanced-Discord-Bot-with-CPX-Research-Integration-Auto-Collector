"""
Ready Event Handler

Handles the bot's ready event when it comes online.
"""

import discord
from loguru import logger
from datetime import datetime


class ReadyEvent:
    """Handles the bot's ready event."""
    
    def __init__(self, bot):
        """Initialize the ready event handler.
        
        Args:
            bot: Discord bot instance
        """
        self.bot = bot
    
    async def on_ready(self):
        """Called when the bot is ready."""
        try:
            # Log bot information
            logger.info(f"Bot is ready! Logged in as {self.bot.user}")
            logger.info(f"Bot ID: {self.bot.user.id}")
            logger.info(f"Bot created at: {self.bot.user.created_at}")
            
            # Set bot status
            await self._set_bot_status()
            
            # Initialize channels
            await self._initialize_channels()
            
            # Log guild information
            await self._log_guild_info()
            
            # Send startup notification
            await self._send_startup_notification()
            
            logger.info("Bot initialization complete")
            
        except Exception as e:
            logger.error(f"Error in ready event: {e}")
    
    async def _set_bot_status(self):
        """Set the bot's status."""
        try:
            # Get status from config
            presence = self.bot.config["discord"].get("presence", "online")
            
            # Set activity
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name="surveys and tips"
            )
            
            await self.bot.change_presence(
                status=getattr(discord.Status, presence),
                activity=activity
            )
            
            logger.info(f"Bot status set to: {presence}")
            
        except Exception as e:
            logger.error(f"Error setting bot status: {e}")
    
    async def _initialize_channels(self):
        """Initialize channel references."""
        try:
            guild = self.bot.get_guild(int(self.bot.config["discord"]["guild_id"]))
            
            if not guild:
                logger.warning("Guild not found")
                return
            
            # Store channel references
            for channel_name, channel_id in self.bot.config["channels"].items():
                if channel_id.isdigit():
                    channel = guild.get_channel(int(channel_id))
                else:
                    channel = discord.utils.get(guild.channels, name=channel_id)
                
                if channel:
                    self.bot.channels[channel_name] = channel
                    logger.info(f"Found channel: {channel_name} -> {channel.name}")
                else:
                    logger.warning(f"Channel not found: {channel_name} ({channel_id})")
            
            logger.info(f"Initialized {len(self.bot.channels)} channels")
            
        except Exception as e:
            logger.error(f"Error initializing channels: {e}")
    
    async def _log_guild_info(self):
        """Log information about the guild."""
        try:
            guild = self.bot.get_guild(int(self.bot.config["discord"]["guild_id"]))
            
            if guild:
                logger.info(f"Connected to guild: {guild.name}")
                logger.info(f"Guild ID: {guild.id}")
                logger.info(f"Member count: {guild.member_count}")
                logger.info(f"Channel count: {len(guild.channels)}")
                
                # Log role information
                roles = [role.name for role in guild.roles if role.name != "@everyone"]
                logger.info(f"Roles: {', '.join(roles[:10])}{'...' if len(roles) > 10 else ''}")
                
        except Exception as e:
            logger.error(f"Error logging guild info: {e}")
    
    async def _send_startup_notification(self):
        """Send startup notification to configured channel."""
        try:
            # Find a suitable channel for notifications
            notification_channel = None
            
            # Try to find a general or announcements channel
            for channel_name in ["general", "announcements", "bot"]:
                if channel_name in self.bot.channels:
                    notification_channel = self.bot.channels[channel_name]
                    break
            
            if notification_channel:
                embed = discord.Embed(
                    title="🤖 Bot Online",
                    color=discord.Color.green(),
                    description="Survey Bot is now online and ready!"
                )
                
                embed.add_field(
                    name="Status",
                    value="🟢 Online",
                    inline=True
                )
                embed.add_field(
                    name="Uptime",
                    value="Just started",
                    inline=True
                )
                embed.add_field(
                    name="Features",
                    value="Survey automation, tip collection, gaming commands",
                    inline=False
                )
                
                embed.set_footer(text=f"Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                await notification_channel.send(embed=embed)
                logger.info("Startup notification sent")
            
        except Exception as e:
            logger.error(f"Error sending startup notification: {e}")
    
    async def _check_permissions(self):
        """Check bot permissions in channels."""
        try:
            guild = self.bot.get_guild(int(self.bot.config["discord"]["guild_id"]))
            
            if not guild:
                return
            
            bot_member = guild.get_member(self.bot.user.id)
            
            for channel_name, channel in self.bot.channels.items():
                permissions = channel.permissions_for(bot_member)
                
                required_permissions = [
                    "send_messages",
                    "read_messages",
                    "embed_links",
                    "attach_files"
                ]
                
                missing_permissions = [
                    perm for perm in required_permissions 
                    if not getattr(permissions, perm, False)
                ]
                
                if missing_permissions:
                    logger.warning(f"Missing permissions in {channel_name}: {', '.join(missing_permissions)}")
                else:
                    logger.info(f"All permissions OK in {channel_name}")
                    
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
    
    async def _update_bot_stats(self):
        """Update bot statistics."""
        try:
            # Update startup time
            await self.bot.db_manager.update_bot_stat("startup_time", datetime.now().isoformat())
            
            # Update guild info
            guild = self.bot.get_guild(int(self.bot.config["discord"]["guild_id"]))
            if guild:
                await self.bot.db_manager.update_bot_stat("guild_info", {
                    "name": guild.name,
                    "id": guild.id,
                    "member_count": guild.member_count,
                    "channel_count": len(guild.channels)
                })
            
            logger.info("Bot statistics updated")
            
        except Exception as e:
            logger.error(f"Error updating bot stats: {e}") 