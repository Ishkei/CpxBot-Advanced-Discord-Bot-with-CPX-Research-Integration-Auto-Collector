#!/usr/bin/env python3
"""
Slash Commands for Survey Bot

This module handles Discord slash commands registration and implementation.
"""

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger
from datetime import datetime
from typing import Optional


class SlashCommands(commands.Cog):
    """Slash commands for the Survey Bot."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="survey", description="Check survey bot status")
    async def survey(self, interaction: discord.Interaction):
        """Check survey bot status."""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="📊 Survey Bot Status",
                color=discord.Color.blue(),
                description="Current survey bot status and information"
            )
            embed.add_field(name="Status", value="🟢 Online", inline=True)
            embed.add_field(name="Uptime", value="Running", inline=True)
            embed.add_field(name="Surveys Completed", value="0", inline=True)
            embed.add_field(name="Total Earnings", value="$0.00", inline=True)
            embed.add_field(name="Webhooks", value="✅ Configured", inline=True)
            embed.add_field(name="CPX Integration", value="✅ Ready", inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in survey slash command: {e}")
            await interaction.followup.send("❌ An error occurred while checking status.")
    
    @app_commands.command(name="start", description="Start a new survey")
    async def start(self, interaction: discord.Interaction):
        """Start a new survey."""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="🚀 Starting Survey",
                color=discord.Color.green(),
                description="Starting survey automation..."
            )
            embed.add_field(name="Status", value="🔍 Searching for surveys...", inline=True)
            embed.add_field(name="User", value=interaction.user.mention, inline=True)
            
            # Send system notification
            self.bot.webhook_manager.send_system_status(
                "info",
                "Survey automation started by user",
                {
                    "User": interaction.user.name,
                    "Server": interaction.guild.name,
                    "Channel": interaction.channel.name
                }
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in start slash command: {e}")
            await interaction.followup.send("❌ An error occurred while starting survey.")
    
    @app_commands.command(name="earnings", description="Check current earnings")
    async def earnings(self, interaction: discord.Interaction):
        """Check current earnings."""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="💰 Earnings Summary",
                color=discord.Color.gold(),
                description="Your current earnings and statistics"
            )
            embed.add_field(name="Total Earnings", value="$0.00", inline=True)
            embed.add_field(name="This Session", value="$0.00", inline=True)
            embed.add_field(name="Surveys Completed", value="0", inline=True)
            embed.add_field(name="Average Per Survey", value="$0.00", inline=True)
            embed.add_field(name="Withdrawals", value="$0.00", inline=True)
            embed.add_field(name="Available Balance", value="$0.00", inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in earnings slash command: {e}")
            await interaction.followup.send("❌ An error occurred while checking earnings.")
    
    @app_commands.command(name="withdraw", description="Withdraw earnings")
    @app_commands.describe(amount="Amount to withdraw")
    async def withdraw(self, interaction: discord.Interaction, amount: float):
        """Withdraw earnings."""
        await interaction.response.defer()
        
        try:
            if amount <= 0:
                await interaction.followup.send("❌ Amount must be greater than 0.")
                return
            
            embed = discord.Embed(
                title="💰 Withdrawal Request",
                color=discord.Color.gold(),
                description=f"Processing withdrawal of ${amount:.2f}"
            )
            embed.add_field(name="Amount", value=f"${amount:.2f}", inline=True)
            embed.add_field(name="Status", value="⏳ Processing", inline=True)
            embed.add_field(name="User", value=interaction.user.mention, inline=True)
            
            await interaction.followup.send(embed=embed)
            
            # Send webhook notification
            self.bot.webhook_manager.send_withdrawal_notification(
                interaction.user.name,
                amount,
                interaction.guild.name
            )
            
        except Exception as e:
            logger.error(f"Error in withdraw slash command: {e}")
            await interaction.followup.send("❌ An error occurred while processing withdrawal.")
    
    @app_commands.command(name="help", description="Show all commands")
    async def help(self, interaction: discord.Interaction):
        """Show help information."""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="🤖 Survey Bot Help",
                color=discord.Color.blue(),
                description="Available slash commands and features"
            )
            
            # Survey Commands
            embed.add_field(
                name="📊 Survey Commands",
                value="""`/survey` - Check survey status
`/start` - Start survey automation
`/earnings` - Check earnings
`/withdraw <amount>` - Withdraw earnings""",
                inline=False
            )
            
            # Role Commands
            embed.add_field(
                name="🎭 Role Commands",
                value="""`/assign` - Assign gamer role
`/remove` - Remove gamer role
`/secret` - Secret command (requires gamer role)""",
                inline=False
            )
            
            # Utility Commands
            embed.add_field(
                name="🔧 Utility Commands",
                value="""`/help` - Show this help
`/poll <question>` - Create a poll""",
                inline=False
            )
            
            embed.set_footer(text="Use !help for prefix commands")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in help slash command: {e}")
            await interaction.followup.send("❌ An error occurred while showing help.")
    
    @app_commands.command(name="assign", description="Assign gamer role")
    async def assign(self, interaction: discord.Interaction):
        """Assign gamer role to user."""
        await interaction.response.defer()
        
        try:
            # Check if gamer role exists
            gamer_role = discord.utils.get(interaction.guild.roles, name="gamer")
            
            if not gamer_role:
                # Create the gamer role if it doesn't exist
                gamer_role = await interaction.guild.create_role(
                    name="gamer",
                    color=discord.Color.green(),
                    reason="Auto-created gamer role"
                )
                logger.info(f"Created gamer role in {interaction.guild.name}")
            
            # Check if user already has the role
            if gamer_role in interaction.user.roles:
                await interaction.followup.send("✅ You already have the gamer role!")
                return
            
            # Assign the role
            await interaction.user.add_roles(gamer_role)
            
            embed = discord.Embed(
                title="🎮 Role Assigned",
                color=discord.Color.green(),
                description=f"Successfully assigned gamer role to {interaction.user.mention}"
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in assign slash command: {e}")
            await interaction.followup.send("❌ An error occurred while assigning role.")
    
    @app_commands.command(name="remove", description="Remove gamer role")
    async def remove(self, interaction: discord.Interaction):
        """Remove gamer role from user."""
        await interaction.response.defer()
        
        try:
            gamer_role = discord.utils.get(interaction.guild.roles, name="gamer")
            
            if not gamer_role:
                await interaction.followup.send("❌ Gamer role doesn't exist.")
                return
            
            if gamer_role not in interaction.user.roles:
                await interaction.followup.send("❌ You don't have the gamer role.")
                return
            
            # Remove the role
            await interaction.user.remove_roles(gamer_role)
            
            embed = discord.Embed(
                title="🎮 Role Removed",
                color=discord.Color.red(),
                description=f"Successfully removed gamer role from {interaction.user.mention}"
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in remove slash command: {e}")
            await interaction.followup.send("❌ An error occurred while removing role.")
    
    @app_commands.command(name="secret", description="Secret command (requires gamer role)")
    async def secret(self, interaction: discord.Interaction):
        """Secret command for gamers only."""
        await interaction.response.defer()
        
        try:
            # Check if user has gamer role
            gamer_role = discord.utils.get(interaction.guild.roles, name="gamer")
            
            if not gamer_role or gamer_role not in interaction.user.roles:
                await interaction.followup.send("❌ You need the gamer role to use this command!")
                return
            
            embed = discord.Embed(
                title="🎮 Secret Command",
                color=discord.Color.purple(),
                description="You found the secret command! This is only for gamers."
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in secret slash command: {e}")
            await interaction.followup.send("❌ An error occurred with the secret command.")
    
    @app_commands.command(name="poll", description="Create a poll")
    @app_commands.describe(question="The poll question")
    async def poll(self, interaction: discord.Interaction, question: str):
        """Create a poll with reactions."""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="📊 Poll",
                description=question,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Poll created by {interaction.user.name}")
            
            poll_message = await interaction.followup.send(embed=embed)
            
            # Add reaction options
            reactions = ["👍", "👎", "🤷"]
            for reaction in reactions:
                await poll_message.add_reaction(reaction)
            
        except Exception as e:
            logger.error(f"Error in poll slash command: {e}")
            await interaction.followup.send("❌ An error occurred while creating poll.")


async def setup(bot):
    """Setup the slash commands cog."""
    await bot.add_cog(SlashCommands(bot))


async def register_commands(bot):
    """Register slash commands with Discord."""
    try:
        await bot.tree.sync()
        logger.info("✅ Slash commands registered successfully")
    except Exception as e:
        logger.error(f"❌ Error registering slash commands: {e}") 