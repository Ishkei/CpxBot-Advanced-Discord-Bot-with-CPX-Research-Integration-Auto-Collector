"""
Discord Bot - Main Bot Class

Handles Discord bot initialization, event handling, and command processing.
"""

import discord
from discord.ext import commands
from loguru import logger
import asyncio
from typing import Dict, Any

from .events.ready_event import ReadyEvent
from .events.message_event import MessageEvent
from .handlers.survey_handler import SurveyHandler
from .handlers.auto_collector import AutoCollector


class SurveyBot(commands.Bot):
    """Main Discord bot class for survey automation and gaming integration."""
    
    def __init__(self, config: Dict[str, Any], db_manager):
        """Initialize the bot with configuration and database manager."""
        # Use only non-privileged intents
        intents = discord.Intents.none()
        intents.guilds = True
        intents.messages = True
        intents.message_content = True
        intents.reactions = True
        
        super().__init__(
            command_prefix=config["discord"]["prefix"],
            intents=intents,
            help_command=None
        )
        
        self.config = config
        self.db_manager = db_manager
        self.survey_handler = SurveyHandler(config, db_manager)
        self.auto_collector = AutoCollector(config, db_manager)
        
        # Store channel references
        self.channels = {}
        
        # Setup event handlers
        self.setup_events()
        self.setup_commands()
        
        logger.info("SurveyBot initialized successfully")
    
    def setup_events(self):
        """Setup Discord event handlers."""
        self.add_listener(ReadyEvent(self).on_ready, "on_ready")
        self.add_listener(MessageEvent(self).on_message, "on_message")
        self.add_listener(self.on_command_error, "on_command_error")
        
    def setup_commands(self):
        """Setup basic commands."""
        @self.command(name="status")
        async def status(ctx):
            """Check the current survey bot status."""
            try:
                embed = discord.Embed(
                    title="🤖 Survey Bot Status",
                    description="Current bot status and statistics",
                    color=0x00ff00
                )
                
                embed.add_field(
                    name="🔧 Bot Status",
                    value="✅ Online and Ready",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in status command: {e}")
                await ctx.send("❌ Error getting bot status")
        
        @self.command(name="earnings")
        async def earnings(ctx):
            """View earnings statistics."""
            try:
                earnings_data = await self.db_manager.get_earnings()
                
                embed = discord.Embed(
                    title="💰 Earnings Statistics",
                    description="Your survey earnings overview",
                    color=0xffd700
                )
                
                embed.add_field(
                    name="💵 Total Earnings",
                    value=f"${earnings_data['total']:.2f}",
                    inline=True
                )
                
                embed.add_field(
                    name="📅 Today's Earnings",
                    value=f"${earnings_data['today']:.2f}",
                    inline=True
                )
                
                embed.add_field(
                    name="📊 This Week",
                    value=f"${earnings_data['week']:.2f}",
                    inline=True
                )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in earnings command: {e}")
                await ctx.send("❌ Error getting earnings")
        
        @self.command(name="mine")
        async def mine(ctx):
            """Mine for cryptocurrency."""
            try:
                import random
                earnings = random.uniform(0.01, 0.50)
                
                embed = discord.Embed(
                    title="⛏️ Mining Complete",
                    description="You found some cryptocurrency!",
                    color=0xffd700
                )
                
                embed.add_field(
                    name="💰 Earnings",
                    value=f"${earnings:.4f}",
                    inline=True
                )
                
                embed.add_field(
                    name="⏱️ Time",
                    value="30 seconds",
                    inline=True
                )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in mine command: {e}")
                await ctx.send("❌ Error while mining")
        
        @self.command(name="help")
        async def help_command(ctx):
            """Show available commands."""
            embed = discord.Embed(
                title="📚 Available Commands",
                description="Here are the available commands:",
                color=0x0099ff
            )
            
            embed.add_field(
                name="!status",
                value="Check bot status",
                inline=False
            )
            
            embed.add_field(
                name="!earnings",
                value="View earnings statistics",
                inline=False
            )
            
            embed.add_field(
                name="!mine",
                value="Mine for cryptocurrency",
                inline=False
            )
            
            embed.add_field(
                name="!help",
                value="Show this help message",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user}")
        logger.info(f"Bot ID: {self.user.id}")
        
        # Store channel references
        guild = self.get_guild(int(self.config["discord"]["guild_id"]))
        if guild:
            for channel_name, channel_id in self.config["channels"].items():
                channel = guild.get_channel(int(channel_id)) if channel_id.isdigit() else discord.utils.get(guild.channels, name=channel_id)
                if channel:
                    self.channels[channel_name] = channel
                    logger.info(f"Found channel: {channel_name} -> {channel.name}")
        
        # Start background tasks
        self.bg_task = self.loop.create_task(self.background_tasks())
        
    async def background_tasks(self):
        """Background tasks for the bot."""
        while not self.is_closed():
            try:
                # Auto-collect tips
                if self.config["auto_collection"]["enabled"]:
                    await self.auto_collector.collect_tips()
                
                # Check for new surveys
                await self.survey_handler.check_for_surveys()
                
                # Wait before next iteration
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in background tasks: {e}")
                await asyncio.sleep(60)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have permission to do that.")
        else:
            logger.error(f"Command error: {error}")
            await ctx.send(f"An error occurred: {error}")
    
    def get_channel(self, channel_name: str):
        """Get a channel by name."""
        return self.channels.get(channel_name)
    
    async def send_to_channel(self, channel_name: str, message: str):
        """Send a message to a specific channel."""
        channel = self.get_channel(channel_name)
        if channel:
            await channel.send(message)
        else:
            logger.warning(f"Channel {channel_name} not found")
    
    def is_valid_channel(self, channel_name: str) -> bool:
        """Check if a channel name is valid."""
        return channel_name in self.config["channels"]
    
    async def close(self):
        """Close the bot and cleanup resources."""
        try:
            # Close survey handler
            if hasattr(self, 'survey_handler'):
                await self.survey_handler.close()
            
            # Close database connection
            if hasattr(self, 'db_manager'):
                await self.db_manager.close()
            
            # Close Discord connection
            await super().close()
            
            logger.info("Bot shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during bot shutdown: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close() 