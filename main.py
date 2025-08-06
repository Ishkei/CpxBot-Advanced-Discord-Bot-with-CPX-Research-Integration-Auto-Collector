#!/usr/bin/env python3
"""
Survey Bot - Main Application Entry Point

This bot integrates with CPX Research for survey completion and Discord for gaming commands.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from loguru import logger
import yaml

from discord_bot.bot import SurveyBot
from utils.config_manager import ConfigManager
from utils.database_manager import DatabaseManager


async def main():
    """Main application entry point."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Setup logging
        logger.add(
            "logs/survey_bot.log",
            rotation="10 MB",
            retention="7 days",
            level=os.getenv("LOG_LEVEL", "INFO")
        )
        
        logger.info("Starting Survey Bot...")
        
        # Load configuration
        config_manager = ConfigManager("config.yaml")
        config = config_manager.get_config()
        
        # Initialize database
        db_manager = DatabaseManager(config["database"]["url"])
        await db_manager.initialize()
        
        # Create and run the Discord bot
        bot = SurveyBot(config, db_manager)
        
        # Start the bot
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            logger.error("DISCORD_TOKEN not found in environment variables")
            return
            
        logger.info("Bot is ready! Starting...")
        await bot.start(token)
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        logger.info("Bot shutdown complete.")


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Run the bot
    asyncio.run(main()) 