#!/usr/bin/env python3
"""
Minimal Discord Bot Test
"""

import asyncio
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from loguru import logger
import discord
from discord.ext import commands

async def main():
    try:
        load_dotenv()
        logger.info("Starting minimal bot test...")
        
        # Create minimal intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.messages = True
        intents.reactions = True
        intents.members = False
        intents.presences = False
        
        # Create bot
        bot = commands.Bot(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        
        @bot.event
        async def on_ready():
            logger.info(f"Bot is ready! Logged in as {bot.user}")
            await bot.close()
        
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            logger.error("DISCORD_TOKEN not found in environment variables")
            return
            
        logger.info("Starting bot...")
        await bot.start(token)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 