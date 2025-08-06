#!/usr/bin/env python3
"""
Survey Bot - Main Application Entry Point

This bot integrates with CPX Research for survey completion and Discord for gaming commands.
"""

import asyncio
import os
import sys
import signal
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from loguru import logger
import yaml

# Import with explicit src path to avoid IDE issues
from src.discord_bot.bot import SurveyBot
from src.utils.config_manager import ConfigManager
from src.utils.database_manager import DatabaseManager


class SurveyBotApp:
    """Main application class for the Survey Bot."""
    
    def __init__(self):
        self.bot = None
        self.db_manager = None
        self.config = None
        self.shutdown_event = asyncio.Event()
        
    async def setup_logging(self):
        """Setup logging configuration."""
        try:
            logger.add(
                "logs/survey_bot.log",
                rotation="10 MB",
                retention="7 days",
                level=os.getenv("LOG_LEVEL", "INFO")
            )
            logger.info("Logging setup completed")
        except Exception as e:
            logger.error(f"Failed to setup logging: {e}")
            raise
    
    async def load_configuration(self):
        """Load and validate configuration."""
        try:
            config_manager = ConfigManager("config.yaml")
            self.config = config_manager.get_config()
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    async def initialize_database(self):
        """Initialize database connection."""
        try:
            self.db_manager = DatabaseManager(self.config["database"]["url"])
            await self.db_manager.initialize()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def create_bot(self):
        """Create and configure the Discord bot."""
        try:
            self.bot = SurveyBot(self.config, self.db_manager)
            logger.info("Discord bot created successfully")
        except Exception as e:
            logger.error(f"Failed to create Discord bot: {e}")
            raise
    
    async def start_bot(self):
        """Start the Discord bot."""
        try:
            token = os.getenv("DISCORD_TOKEN")
            if not token:
                logger.error("DISCORD_TOKEN not found in environment variables")
                raise ValueError("DISCORD_TOKEN environment variable is required")
            
            logger.info("Starting Discord bot...")
            await self.bot.start(token)
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown of the application."""
        try:
            logger.info("Shutting down Survey Bot...")
            
            if self.bot:
                await self.bot.close()
                logger.info("Discord bot closed")
            
            if self.db_manager:
                await self.db_manager.close()
                logger.info("Database connection closed")
            
            logger.info("Shutdown completed successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Main application run method."""
        try:
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Load environment variables
            load_dotenv()
            
            # Setup logging
            await self.setup_logging()
            
            # Load configuration
            await self.load_configuration()
            
            # Initialize database
            await self.initialize_database()
            
            # Create bot
            await self.create_bot()
            
            # Start bot
            logger.info("Survey Bot is ready! Starting...")
            
            # Run bot until shutdown signal
            await self.start_bot()
            
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
        finally:
            await self.shutdown()


async def main():
    """Main application entry point."""
    app = SurveyBotApp()
    await app.run()


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Run the bot
    asyncio.run(main()) 