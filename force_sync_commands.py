#!/usr/bin/env python3
"""
Force Sync Slash Commands with Discord
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

async def force_sync():
    """Force sync slash commands with Discord."""
    load_dotenv()
    
    # Bot setup
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"🤖 Bot logged in as {bot.user.name}")
        
        try:
            # Sync commands globally
            print("🔄 Syncing commands globally...")
            await bot.tree.sync()
            print("✅ Commands synced globally!")
            
            # Also sync to specific guild for faster testing
            for guild in bot.guilds:
                print(f"🔄 Syncing commands to guild: {guild.name}")
                await bot.tree.sync(guild=guild)
                print(f"✅ Commands synced to {guild.name}!")
            
            print("\n🎉 All commands synced! Try typing / in Discord now.")
            
        except Exception as e:
            print(f"❌ Error syncing commands: {e}")
        
        await bot.close()
    
    try:
        await bot.start(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(force_sync()) 