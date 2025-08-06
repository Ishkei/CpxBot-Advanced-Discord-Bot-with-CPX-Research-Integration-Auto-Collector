#!/usr/bin/env python3
"""
Check Bot Permissions for Slash Commands
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

async def check_permissions():
    """Check bot permissions and slash command status."""
    load_dotenv()
    
    # Bot setup
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"🤖 Bot logged in as {bot.user.name}")
        print(f"🆔 Bot ID: {bot.user.id}")
        
        # Check guild permissions
        for guild in bot.guilds:
            print(f"\n📋 Guild: {guild.name} (ID: {guild.id})")
            
            bot_member = guild.get_member(bot.user.id)
            if bot_member:
                permissions = bot_member.guild_permissions
                
                print("🔐 Bot Permissions:")
                print(f"   ✅ Use Slash Commands: {permissions.use_slash_commands}")
                print(f"   ✅ Send Messages: {permissions.send_messages}")
                print(f"   ✅ Embed Links: {permissions.embed_links}")
                print(f"   ✅ Manage Roles: {permissions.manage_roles}")
                print(f"   ✅ Read Message History: {permissions.read_message_history}")
                
                # Check application commands
                try:
                    commands = await guild.fetch_commands()
                    print(f"\n📝 Slash Commands in this guild: {len(commands)}")
                    for cmd in commands:
                        print(f"   • /{cmd.name}: {cmd.description}")
                except Exception as e:
                    print(f"❌ Error fetching commands: {e}")
        
        await bot.close()
    
    try:
        await bot.start(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_permissions()) 