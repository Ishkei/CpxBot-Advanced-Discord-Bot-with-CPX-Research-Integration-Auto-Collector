"""
Survey Commands - Discord commands for survey automation

Handles survey-related commands like !survey, !status, !earnings, etc.
"""

import discord
from discord.ext import commands
from loguru import logger
from typing import Dict, Any
import asyncio


class SurveyCommands(commands.Cog):
    """Survey-related commands for the bot."""
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="status")
    async def status(self, ctx):
        """Check the current survey bot status."""
        try:
            embed = discord.Embed(
                title="🤖 Survey Bot Status",
                description="Current bot status and statistics",
                color=0x00ff00
            )
            
            # Get bot stats from database
            stats = await self.bot.db_manager.get_bot_stat("survey_stats")
            if stats:
                embed.add_field(
                    name="📊 Statistics",
                    value=f"Surveys Completed: {stats.get('completed', 0)}\n"
                          f"Total Earnings: ${stats.get('total_earnings', 0.0):.2f}\n"
                          f"Last Survey: {stats.get('last_survey', 'Never')}",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📊 Statistics",
                    value="No survey data available yet",
                    inline=False
                )
            
            embed.add_field(
                name="🔧 Bot Status",
                value="✅ Online and Ready",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await ctx.send("❌ Error getting bot status")
    
    @commands.command(name="earnings")
    async def earnings(self, ctx):
        """View earnings statistics."""
        try:
            earnings = await self.bot.db_manager.get_earnings()
            
            embed = discord.Embed(
                title="💰 Earnings Statistics",
                description="Your survey earnings overview",
                color=0xffd700
            )
            
            embed.add_field(
                name="💵 Total Earnings",
                value=f"${earnings['total']:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="📅 Today's Earnings",
                value=f"${earnings['today']:.2f}",
                inline=True
            )
            
            embed.add_field(
                name="📊 This Week",
                value=f"${earnings['week']:.2f}",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in earnings command: {e}")
            await ctx.send("❌ Error getting earnings")
    
    @commands.command(name="start")
    async def start_survey(self, ctx):
        """Start a new survey."""
        try:
            await ctx.send("🔍 Searching for available surveys...")
            
            # This would integrate with CPX Research
            # For now, just show a placeholder
            embed = discord.Embed(
                title="📝 Survey Started",
                description="Survey automation is now active",
                color=0x00ff00
            )
            
            embed.add_field(
                name="⚠️ Note",
                value="CPX Research integration needs to be configured in .env file",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error starting survey: {e}")
            await ctx.send("❌ Error starting survey")
    
    @commands.command(name="stop")
    async def stop_survey(self, ctx):
        """Stop survey automation."""
        try:
            embed = discord.Embed(
                title="⏹️ Survey Stopped",
                description="Survey automation has been stopped",
                color=0xff0000
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error stopping survey: {e}")
            await ctx.send("❌ Error stopping survey")
    
    @commands.command(name="help")
    async def help_survey(self, ctx):
        """Show survey command help."""
        embed = discord.Embed(
            title="📚 Survey Commands Help",
            description="Available survey-related commands",
            color=0x0099ff
        )
        
        embed.add_field(
            name="!survey status",
            value="Check bot status and statistics",
            inline=False
        )
        
        embed.add_field(
            name="!survey earnings",
            value="View earnings statistics",
            inline=False
        )
        
        embed.add_field(
            name="!survey start",
            value="Start survey automation",
            inline=False
        )
        
        embed.add_field(
            name="!survey stop",
            value="Stop survey automation",
            inline=False
        )
        
        embed.add_field(
            name="!survey help",
            value="Show this help message",
            inline=False
        )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(SurveyCommands(bot)) 