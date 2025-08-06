"""
Gaming Commands - Discord commands for gaming features

Handles gaming-related commands like !mine, !fish, !rob, etc.
"""

import discord
from discord.ext import commands
from discord import app_commands
from loguru import logger
import random
import asyncio


class GamingCommands(commands.Cog):
    """Gaming-related commands for the bot."""
    
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="mine", description="Mine for cryptocurrency.")
    async def mine(self, interaction: discord.Interaction):
        """Mine for cryptocurrency."""
        try:
            # Simulate mining
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
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in mine command: {e}")
            await interaction.response.send_message("❌ Error while mining", ephemeral=True)
    
    @app_commands.command(name="fish", description="Fish for cryptocurrency.")
    async def fish(self, interaction: discord.Interaction):
        """Fish for cryptocurrency."""
        try:
            # Simulate fishing
            earnings = random.uniform(0.005, 0.25)
            
            embed = discord.Embed(
                title="🎣 Fishing Complete",
                description="You caught some crypto!",
                color=0x00bfff
            )
            
            embed.add_field(
                name="💰 Earnings",
                value=f"${earnings:.4f}",
                inline=True
            )
            
            embed.add_field(
                name="⏱️ Time",
                value="45 seconds",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in fish command: {e}")
            await interaction.response.send_message("❌ Error while fishing", ephemeral=True)
    
    @app_commands.command(name="rob", description="Rob the bank for cryptocurrency.")
    async def rob(self, interaction: discord.Interaction):
        """Rob the bank for cryptocurrency."""
        try:
            # Simulate robbery
            success = random.choice([True, False])
            
            if success:
                earnings = random.uniform(0.10, 1.00)
                embed = discord.Embed(
                    title="🦹 Robbery Successful",
                    description="You successfully robbed the bank!",
                    color=0xff0000
                )
                
                embed.add_field(
                    name="💰 Stolen",
                    value=f"${earnings:.4f}",
                    inline=True
                )
            else:
                embed = discord.Embed(
                    title="🚔 Robbery Failed",
                    description="You were caught by the police!",
                    color=0x808080
                )
                
                embed.add_field(
                    name="💸 Fine",
                    value="$0.25",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in rob command: {e}")
            await interaction.response.send_message("❌ Error during robbery", ephemeral=True)
    
    @app_commands.command(name="daily", description="Collect daily reward.")
    async def daily(self, interaction: discord.Interaction):
        """Collect daily reward."""
        try:
            # Simulate daily reward
            earnings = random.uniform(0.05, 0.20)
            
            embed = discord.Embed(
                title="🎁 Daily Reward",
                description="Here's your daily cryptocurrency reward!",
                color=0x00ff00
            )
            
            embed.add_field(
                name="💰 Reward",
                value=f"${earnings:.4f}",
                inline=True
            )
            
            embed.add_field(
                name="📅 Next Daily",
                value="24 hours",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in daily command: {e}")
            await interaction.response.send_message("❌ Error collecting daily reward", ephemeral=True)
    
    @app_commands.command(name="balance", description="Check your cryptocurrency balance.")
    async def balance(self, interaction: discord.Interaction):
        """Check your cryptocurrency balance."""
        try:
            # Get balance from database
            earnings = await self.bot.db_manager.get_earnings()
            
            embed = discord.Embed(
                title="💰 Balance",
                description="Your cryptocurrency balance",
                color=0xffd700
            )
            
            embed.add_field(
                name="💵 Total Balance",
                value=f"${earnings['total']:.4f}",
                inline=True
            )
            
            embed.add_field(
                name="📊 Today's Earnings",
                value=f"${earnings['today']:.4f}",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in balance command: {e}")
            await interaction.response.send_message("❌ Error getting balance", ephemeral=True)
    
    @app_commands.command(name="help_gaming", description="Show gaming command help.")
    async def help_gaming(self, interaction: discord.Interaction):
        """Show gaming command help."""
        embed = discord.Embed(
            title="🎮 Gaming Commands Help",
            description="Available gaming commands",
            color=0x0099ff
        )
        
        embed.add_field(
            name="!mine",
            value="Mine for cryptocurrency",
            inline=False
        )
        
        embed.add_field(
            name="!fish",
            value="Fish for cryptocurrency",
            inline=False
        )
        
        embed.add_field(
            name="!rob",
            value="Rob the bank (risky!)",
            inline=False
        )
        
        embed.add_field(
            name="!daily",
            value="Collect daily reward",
            inline=False
        )
        
        embed.add_field(
            name="!balance",
            value="Check your balance",
            inline=False
        )
        
        embed.add_field(
            name="!help",
            value="Show this help message",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(GamingCommands(bot)) 