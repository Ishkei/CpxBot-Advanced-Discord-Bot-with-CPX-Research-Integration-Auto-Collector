"""
CPX Research Commands - Discord Commands for CPX Research Integration

Handles CPX Research specific commands like /offers, /withdraw, etc.
"""

import discord
from discord.ext import commands
from loguru import logger
import asyncio
from typing import Dict, Any, Optional
import json
from datetime import datetime


class CPXCommands(commands.Cog):
    """Cog for CPX Research specific commands."""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config
        self.cpx_config = self.config.get("cpx_research", {})
        
    @commands.command(name="offers")
    async def offers(self, ctx):
        """Access CPX Research offers and surveys.
        
        This command will:
        1. Check if user has a character set up
        2. Open CPX Research surveys
        3. Start automated survey completion
        """
        try:
            # Check if user has character set up
            character_status = await self._check_character_setup(ctx)
            if not character_status:
                embed = discord.Embed(
                    title="❌ Character Setup Required",
                    description="You need to set up your character first!",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="Setup Steps",
                    value="1. Use `/setup` to create your character\n"
                          "2. Then use `/offers` again to access surveys",
                    inline=False
                )
                await ctx.send(embed=embed)
                return
            
            # Start CPX Research survey automation
            await ctx.send("🎯 Starting CPX Research surveys...")
            
            # Create background task for survey automation
            asyncio.create_task(self._run_cpx_surveys(ctx))
            
        except Exception as e:
            logger.error(f"Error in offers command: {e}")
            await ctx.send("❌ An error occurred while accessing offers.")
    
    async def _check_character_setup(self, ctx) -> bool:
        """Check if user has set up their character."""
        # This would typically check against the game's API
        # For now, we'll assume the user has set up their character
        # In a real implementation, you'd query the Discord bot's character system
        return True
    
    async def _run_cpx_surveys(self, ctx):
        """Run CPX Research survey automation in background."""
        try:
            # Import the CPX scraper
            from ..handlers.cpx_handler import CPXHandler
            
            cpx_handler = CPXHandler(self.config)
            
            # Start survey automation
            embed = discord.Embed(
                title="🚀 CPX Research Automation Started",
                description="Bot is now searching for and completing surveys...",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Target URL",
                value=f"https://offers.cpx-research.com/index.php?app_id={self.cpx_config.get('app_id')}&ext_user_id={self.cpx_config.get('ext_user_id')}",
                inline=False
            )
            embed.add_field(
                name="Status",
                value="🔄 Searching for surveys...",
                inline=True
            )
            
            status_msg = await ctx.send(embed=embed)
            
            # Run the survey automation
            results = await cpx_handler.run_survey_automation()
            
            # Update status message
            embed = discord.Embed(
                title="✅ CPX Research Automation Complete",
                description="Survey session completed!",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Surveys Completed",
                value=results.get("surveys_completed", 0),
                inline=True
            )
            embed.add_field(
                name="Total Earnings",
                value=f"${results.get('total_earnings', 0):.2f}",
                inline=True
            )
            embed.add_field(
                name="Session Duration",
                value=f"{results.get('duration_minutes', 0)} minutes",
                inline=True
            )
            
            await status_msg.edit(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in CPX survey automation: {e}")
            await ctx.send(f"❌ Error during survey automation: {str(e)}")
    
    @commands.command(name="withdraw")
    async def withdraw(self, ctx, amount: Optional[float] = None):
        """Withdraw earnings to your crypto wallet.
        
        Usage:
        !withdraw - Withdraw all available balance
        !withdraw 10.50 - Withdraw specific amount
        """
        try:
            # Get user's current balance
            balance = await self._get_user_balance(ctx.author.id)
            
            if balance <= 0:
                embed = discord.Embed(
                    title="💰 No Balance Available",
                    description="You don't have any earnings to withdraw.",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
                return
            
            # Determine withdrawal amount
            withdraw_amount = amount if amount else balance
            
            if withdraw_amount > balance:
                embed = discord.Embed(
                    title="❌ Insufficient Balance",
                    description=f"You only have ${balance:.2f} available.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
            
            # Process withdrawal
            embed = discord.Embed(
                title="🏦 Withdrawal Request",
                description=f"Processing withdrawal of ${withdraw_amount:.2f}...",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Instructions",
                value="1. Use `/withdraw` in the #🏛️・bank channel\n"
                      "2. Follow the withdrawal instructions\n"
                      "3. Receive crypto in your Tip.cc wallet",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in withdraw command: {e}")
            await ctx.send("❌ An error occurred while processing withdrawal.")
    
    async def _get_user_balance(self, user_id: int) -> float:
        """Get user's current balance from database."""
        try:
            # This would query your database for the user's balance
            # For now, return a placeholder value
            return 25.50  # Placeholder balance
        except Exception as e:
            logger.error(f"Error getting user balance: {e}")
            return 0.0
    
    @commands.command(name="cpx_status")
    async def cpx_status(self, ctx):
        """Check CPX Research status and configuration."""
        try:
            embed = discord.Embed(
                title="📊 CPX Research Status",
                description="Current CPX Research configuration and status",
                color=discord.Color.blue()
            )
            
            # Configuration info
            embed.add_field(
                name="Base URL",
                value=self.cpx_config.get("base_url", "Not configured"),
                inline=False
            )
            embed.add_field(
                name="App ID",
                value=self.cpx_config.get("app_id", "Not configured"),
                inline=True
            )
            embed.add_field(
                name="User ID",
                value=self.cpx_config.get("ext_user_id", "Not configured"),
                inline=True
            )
            
            # Survey settings
            survey_settings = self.cpx_config.get("survey_settings", {})
            embed.add_field(
                name="Min Earnings",
                value=f"${survey_settings.get('min_earnings', 0):.2f}",
                inline=True
            )
            embed.add_field(
                name="Max Time",
                value=f"{survey_settings.get('max_time', 0)} minutes",
                inline=True
            )
            embed.add_field(
                name="Auto Accept",
                value="✅" if survey_settings.get("auto_accept", False) else "❌",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in cpx_status command: {e}")
            await ctx.send("❌ An error occurred while getting CPX status.")
    
    @commands.command(name="setup")
    async def setup(self, ctx):
        """Setup your character for CPX Research surveys."""
        try:
            embed = discord.Embed(
                title="🎮 Character Setup",
                description="Setting up your character for CPX Research surveys...",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Setup Complete",
                value="✅ Your character has been set up successfully!\n"
                      "You can now use `/offers` to access CPX Research surveys.",
                inline=False
            )
            embed.add_field(
                name="Next Steps",
                value="1. Use `/offers` to start surveys\n"
                      "2. Use `/withdraw` to cash out earnings\n"
                      "3. Check `/cpx_status` for configuration",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in setup command: {e}")
            await ctx.send("❌ An error occurred during character setup.")


def setup(bot):
    """Add the CPX commands cog to the bot."""
    bot.add_cog(CPXCommands(bot)) 