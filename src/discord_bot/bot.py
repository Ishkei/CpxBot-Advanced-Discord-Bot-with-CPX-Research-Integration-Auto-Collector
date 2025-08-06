"""
Discord Bot - Main Bot Class

Handles Discord bot initialization, event handling, and command processing.
"""

import discord
from discord.ext import commands
from loguru import logger
import asyncio
from typing import Dict, Any
import os

from .events.ready_event import ReadyEvent
from .events.message_event import MessageEvent
from .handlers.survey_handler import SurveyHandler
from src.utils.config_manager import ConfigManager
from src.utils.database_manager import DatabaseManager
from src.utils.webhook_manager import WebhookManager



class SurveyBot(commands.Bot):
    """Main Discord bot class for survey automation and gaming integration."""
    
    def __init__(self, config: Dict[str, Any], db_manager):
        """Initialize the bot with configuration and database manager."""
        # Use proper intents configuration as shown in the tutorial
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.reactions = True
        
        super().__init__(
            command_prefix=config["discord"]["prefix"],
            intents=intents,
            help_command=None
        )
        
        self.config = config
        self.db_manager = db_manager
        self.survey_handler = SurveyHandler(config, db_manager)
        self.webhook_manager = WebhookManager()
        
        # Store channel references
        self.channels = {}
        
        # Setup event handlers
        self.setup_events()
        
        # Slash commands will be loaded in on_ready
        
        logger.info("SurveyBot initialized successfully")
    
    def setup_events(self):
        """Setup Discord event handlers."""
        self.add_listener(self.on_ready, "on_ready")
        self.add_listener(self.on_command_error, "on_command_error")
        
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        try:
            logger.info(f"Logged in as {self.user.name}")
            logger.info(f"Bot ID: {self.user.id}")
            
            # Set bot status
            await self.change_presence(activity=discord.Game(name="Surveys | /help"))
            
            # Load slash commands
            await self.load_slash_commands()
            
            # Send system status notification
            self.webhook_manager.send_system_status(
                "online", 
                "Survey Bot is now online and ready to process surveys!",
                {
                    "Bot Name": self.user.name,
                    "Bot ID": self.user.id,
                    "Servers": len(self.guilds)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in on_ready: {e}")
            self.webhook_manager.send_error_report("Startup Error", str(e))
    
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
    
    async def load_slash_commands(self):
        """Load and register slash commands from cogs."""
        try:
            # Load cogs from the commands directory
            cogs_dir = "src.discord_bot.commands"
            for filename in os.listdir("src/discord_bot/commands"):
                if filename.endswith(".py") and not filename.startswith("__"):
                    await self.load_extension(f"{cogs_dir}.{filename[:-3]}")
            
            # Sync all commands to Discord
            await self.tree.sync()
            logger.info("✅ Slash commands loaded and synced successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading slash commands: {e}")
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close() 