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
                title="💳 Withdrawal Request",
                color=discord.Color.green(),
                description=f"Processing withdrawal of ${amount:.2f}"
            )
            embed.add_field(name="Amount", value=f"${amount:.2f}", inline=True)
            embed.add_field(name="User", value=interaction.user.mention, inline=True)
            embed.add_field(name="Status", value="Processing...", inline=True)
            
            # Send withdrawal notification
            self.bot.webhook_manager.send_withdrawal_confirmation(amount, "Discord", f"User: {interaction.user.name}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in withdraw slash command: {e}")
            await interaction.followup.send("❌ An error occurred while processing withdrawal.")
    
    @app_commands.command(name="help", description="Show all commands")
    async def help(self, interaction: discord.Interaction):
        """Show all available commands."""
        embed = discord.Embed(
            title="🤖 Survey Bot Help",
            color=discord.Color.blue(),
            description="Available commands and features"
        )
        
        embed.add_field(
            name="📊 Survey Commands",
            value="• `/survey` - Check bot status\n"
                  "• `/start` - Start survey automation\n"
                  "• `/earnings` - Check your earnings\n"
                  "• `/withdraw <amount>` - Withdraw earnings",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Role Commands",
            value="• `/assign` - Assign gamer role\n"
                  "• `/remove` - Remove gamer role\n"
                  "• `/secret` - Secret command (requires role)",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Utility Commands",
            value="• `/help` - Show this help message\n"
                  "• `/poll <question>` - Create a poll",
            inline=False
        )
        
        embed.add_field(
            name="🔗 Prefix Commands",
            value="• `!survey status` - Alternative commands\n"
                  "• `!withdraw <amount>` - Alternative withdrawal",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="assign", description="Assign gamer role")
    async def assign(self, interaction: discord.Interaction):
        """Assign gamer role to user."""
        await interaction.response.defer()
        
        try:
            guild = interaction.guild
            role = discord.utils.get(guild.roles, name="gamer")
            
            if not role:
                # Create the role if it doesn't exist
                role = await guild.create_role(name="gamer", color=discord.Color.green())
                logger.info(f"Created gamer role: {role.name}")
            
            member = interaction.user
            
            if role in member.roles:
                await interaction.followup.send("❌ You already have the gamer role!")
                return
            
            await member.add_roles(role)
            
            embed = discord.Embed(
                title="🎮 Role Assigned",
                color=discord.Color.green(),
                description=f"Successfully assigned gamer role to {member.mention}"
            )
            embed.add_field(name="Role", value=role.mention, inline=True)
            embed.add_field(name="User", value=member.mention, inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in assign slash command: {e}")
            await interaction.followup.send("❌ An error occurred while assigning role.")
    
    @app_commands.command(name="remove", description="Remove gamer role")
    async def remove(self, interaction: discord.Interaction):
        """Remove gamer role from user."""
        await interaction.response.defer()
        
        try:
            guild = interaction.guild
            role = discord.utils.get(guild.roles, name="gamer")
            
            if not role:
                await interaction.followup.send("❌ Gamer role doesn't exist!")
                return
            
            member = interaction.user
            
            if role not in member.roles:
                await interaction.followup.send("❌ You don't have the gamer role!")
                return
            
            await member.remove_roles(role)
            
            embed = discord.Embed(
                title="🎮 Role Removed",
                color=discord.Color.red(),
                description=f"Successfully removed gamer role from {member.mention}"
            )
            embed.add_field(name="Role", value=role.mention, inline=True)
            embed.add_field(name="User", value=member.mention, inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in remove slash command: {e}")
            await interaction.followup.send("❌ An error occurred while removing role.")
    
    @app_commands.command(name="secret", description="Secret command (requires gamer role)")
    async def secret(self, interaction: discord.Interaction):
        """Secret command that requires gamer role."""
        await interaction.response.defer()
        
        try:
            member = interaction.user
            role = discord.utils.get(interaction.guild.roles, name="gamer")
            
            if not role or role not in member.roles:
                await interaction.followup.send("❌ You need the gamer role to use this command!")
                return
            
            embed = discord.Embed(
                title="🤫 Secret Command",
                color=discord.Color.purple(),
                description="You found the secret command!"
            )
            embed.add_field(name="User", value=member.mention, inline=True)
            embed.add_field(name="Role", value=role.mention, inline=True)
            embed.add_field(name="Message", value="🎉 Congratulations! You have access to secret features!", inline=False)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in secret slash command: {e}")
            await interaction.followup.send("❌ An error occurred with the secret command.")
    
    @app_commands.command(name="poll", description="Create a poll")
    @app_commands.describe(question="The poll question")
    async def poll(self, interaction: discord.Interaction, question: str):
        """Create a poll with reactions."""
        try:
            embed = discord.Embed(
                title="📊 Poll",
                color=discord.Color.blue(),
                description=question
            )
            embed.add_field(name="Created by", value=interaction.user.mention, inline=True)
            embed.add_field(name="Votes", value="👍 0 | 👎 0", inline=True)
            
            message = await interaction.response.send_message(embed=embed)
            
            # Add reactions
            await message.add_reaction("👍")
            await message.add_reaction("👎")
            
        except Exception as e:
            logger.error(f"Error in poll slash command: {e}")
            await interaction.response.send_message("❌ An error occurred while creating the poll.")


async def setup(bot):
    """Setup function for the slash commands cog."""
    await bot.add_cog(SlashCommands(bot))
    logger.info("✅ Slash commands cog loaded")


async def register_commands(bot):
    """Register slash commands with Discord."""
    try:
        # Sync commands to Discord
        await bot.tree.sync()
        logger.info("✅ Slash commands registered successfully")
    except Exception as e:
        logger.error(f"❌ Error registering slash commands: {e}") 