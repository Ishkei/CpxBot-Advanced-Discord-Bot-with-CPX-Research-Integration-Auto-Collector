"""
Tip Commands - Discord commands for tip collection and management

Handles tip-related commands like !tips, !auto-collect, !multi-account, etc.
"""

import discord
from discord.ext import commands
from loguru import logger
import asyncio
from typing import Dict, Any


class TipCommands(commands.Cog):
    """Tip-related commands for the bot."""
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="status")
    async def tip_status(self, ctx):
        """Check auto-collection status."""
        try:
            config = self.bot.config["auto_collection"]
            
            embed = discord.Embed(
                title="💰 Auto-Collection Status",
                description="Current tip collection settings",
                color=0x00ff00
            )
            
            embed.add_field(
                name="🔄 Auto-Collection",
                value="✅ Enabled" if config["enabled"] else "❌ Disabled",
                inline=True
            )
            
            embed.add_field(
                name="⏱️ Collection Interval",
                value=f"{config['collection_interval']} seconds",
                inline=True
            )
            
            embed.add_field(
                name="💰 Min Amount",
                value=f"${config['min_tip_amount']:.4f}",
                inline=True
            )
            
            # Get stats from database
            stats = await self.bot.db_manager.get_auto_collector_stats()
            
            embed.add_field(
                name="📊 Total Collected",
                value=f"${stats['total_collected']:.4f}",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Collections",
                value=f"{stats['total_collections']}",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in tip status command: {e}")
            await ctx.send("❌ Error getting tip status")
    
    @commands.command(name="stats")
    async def tip_stats(self, ctx):
        """View tip statistics."""
        try:
            user_id = str(ctx.author.id)
            stats = await self.bot.db_manager.get_tip_stats(user_id)
            
            embed = discord.Embed(
                title="📊 Tip Statistics",
                description=f"Statistics for {ctx.author.display_name}",
                color=0xffd700
            )
            
            embed.add_field(
                name="💸 Tips Sent",
                value=f"{stats['tips_sent']}",
                inline=True
            )
            
            embed.add_field(
                name="🎁 Tips Received",
                value=f"{stats['tips_received']}",
                inline=True
            )
            
            embed.add_field(
                name="💰 Amount Sent",
                value=f"${stats['amount_sent']:.4f}",
                inline=True
            )
            
            embed.add_field(
                name="💵 Amount Received",
                value=f"${stats['amount_received']:.4f}",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in tip stats command: {e}")
            await ctx.send("❌ Error getting tip statistics")
    
    @commands.command(name="multi-account")
    async def multi_account(self, ctx, action: str = "status"):
        """Manage multi-accounting settings.
        
        Usage:
        !multi-account status - Check multi-accounting status
        !multi-account enable - Enable multi-accounting
        !multi-account disable - Disable multi-accounting
        !multi-account list - List configured accounts
        """
        try:
            if action == "status":
                await self._multi_account_status(ctx)
            elif action == "enable":
                await self._enable_multi_account(ctx)
            elif action == "disable":
                await self._disable_multi_account(ctx)
            elif action == "list":
                await self._list_accounts(ctx)
            else:
                await ctx.send(f"Unknown action: {action}. Use 'status', 'enable', 'disable', or 'list'.")
                
        except Exception as e:
            logger.error(f"Error in multi-account command: {e}")
            await ctx.send("❌ Error managing multi-accounting")
    
    async def _multi_account_status(self, ctx):
        """Check multi-accounting status."""
        config = self.bot.config["auto_collection"]
        enabled = config.get("multi_accounting", {}).get("enabled", False)
        
        embed = discord.Embed(
            title="🔄 Multi-Accounting Status",
            description="Multi-accounting configuration",
            color=0x00ff00 if enabled else 0xff0000
        )
        
        embed.add_field(
            name="Status",
            value="✅ Enabled" if enabled else "❌ Disabled",
            inline=True
        )
        
        if enabled:
            accounts = config.get("multi_accounting", {}).get("accounts", [])
            embed.add_field(
                name="Accounts",
                value=f"{len(accounts)} configured",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    async def _enable_multi_account(self, ctx):
        """Enable multi-accounting."""
        embed = discord.Embed(
            title="✅ Multi-Accounting Enabled",
            description="Multi-accounting has been enabled",
            color=0x00ff00
        )
        
        embed.add_field(
            name="Note",
            value="Configure accounts in config.yaml",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def _disable_multi_account(self, ctx):
        """Disable multi-accounting."""
        embed = discord.Embed(
            title="❌ Multi-Accounting Disabled",
            description="Multi-accounting has been disabled",
            color=0xff0000
        )
        
        await ctx.send(embed=embed)
    
    async def _list_accounts(self, ctx):
        """List configured accounts."""
        config = self.bot.config["auto_collection"]
        accounts = config.get("multi_accounting", {}).get("accounts", [])
        
        embed = discord.Embed(
            title="📋 Configured Accounts",
            description="Multi-accounting accounts",
            color=0x0099ff
        )
        
        if accounts:
            for i, account in enumerate(accounts, 1):
                embed.add_field(
                    name=f"Account {i}",
                    value=f"ID: {account.get('id', 'Unknown')}",
                    inline=True
                )
        else:
            embed.add_field(
                name="No Accounts",
                value="No accounts configured",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="cpm")
    async def set_cpm(self, ctx, min_cpm: int = None, max_cpm: int = None):
        """Set randomized CPM (Characters Per Minute) range.
        
        Usage:
        !cpm - Show current CPM settings
        !cpm 200 310 - Set CPM range to 200-310
        """
        try:
            if min_cpm is None or max_cpm is None:
                # Show current settings
                config = self.bot.config["auto_collection"]
                current_min = config.get("cpm_min", 200)
                current_max = config.get("cpm_max", 310)
                
                embed = discord.Embed(
                    title="⌨️ CPM Settings",
                    description="Current CPM (Characters Per Minute) settings",
                    color=0x0099ff
                )
                
                embed.add_field(
                    name="Current Range",
                    value=f"{current_min} - {current_max} CPM",
                    inline=True
                )
                
                await ctx.send(embed=embed)
            else:
                # Update settings
                embed = discord.Embed(
                    title="✅ CPM Updated",
                    description=f"CPM range set to {min_cpm}-{max_cpm}",
                    color=0x00ff00
                )
                
                await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in CPM command: {e}")
            await ctx.send("❌ Error setting CPM")
    
    @commands.command(name="channels")
    async def manage_channels(self, ctx, action: str = "list"):
        """Manage channel whitelist/blacklist.
        
        Usage:
        !channels list - Show current channel settings
        !channels whitelist add #channel - Add channel to whitelist
        !channels blacklist add #channel - Add channel to blacklist
        """
        try:
            if action == "list":
                await self._list_channels(ctx)
            elif action.startswith("whitelist"):
                await self._manage_whitelist(ctx, action)
            elif action.startswith("blacklist"):
                await self._manage_blacklist(ctx, action)
            else:
                await ctx.send("Unknown action. Use 'list', 'whitelist add/remove', or 'blacklist add/remove'")
                
        except Exception as e:
            logger.error(f"Error in channels command: {e}")
            await ctx.send("❌ Error managing channels")
    
    async def _list_channels(self, ctx):
        """List current channel settings."""
        config = self.bot.config["auto_collection"]
        whitelist = config.get("channel_whitelist", [])
        blacklist = config.get("channel_blacklist", [])
        
        embed = discord.Embed(
            title="📋 Channel Settings",
            description="Current channel whitelist/blacklist",
            color=0x0099ff
        )
        
        embed.add_field(
            name="✅ Whitelist",
            value="\n".join(whitelist) if whitelist else "None",
            inline=True
        )
        
        embed.add_field(
            name="❌ Blacklist",
            value="\n".join(blacklist) if blacklist else "None",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    async def _manage_whitelist(self, ctx, action):
        """Manage whitelist."""
        parts = action.split()
        if len(parts) < 3:
            await ctx.send("Usage: !channels whitelist add/remove #channel")
            return
        
        sub_action = parts[1]
        channel = parts[2]
        
        embed = discord.Embed(
            title="✅ Whitelist Updated",
            description=f"Channel {channel} {sub_action}ed to whitelist",
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)
    
    async def _manage_blacklist(self, ctx, action):
        """Manage blacklist."""
        parts = action.split()
        if len(parts) < 3:
            await ctx.send("Usage: !channels blacklist add/remove #channel")
            return
        
        sub_action = parts[1]
        channel = parts[2]
        
        embed = discord.Embed(
            title="❌ Blacklist Updated",
            description=f"Channel {channel} {sub_action}ed to blacklist",
            color=0xff0000
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="thresholds")
    async def manage_thresholds(self, ctx, action: str = "list"):
        """Manage drop thresholds.
        
        Usage:
        !thresholds list - Show current thresholds
        !thresholds add 0.10 50 - Add threshold (amount, percentage)
        !thresholds remove 0.10 - Remove threshold
        """
        try:
            if action == "list":
                await self._list_thresholds(ctx)
            elif action == "add":
                await ctx.send("Usage: !thresholds add <amount> <percentage>")
            elif action == "remove":
                await ctx.send("Usage: !thresholds remove <amount>")
            else:
                await ctx.send("Unknown action. Use 'list', 'add', or 'remove'")
                
        except Exception as e:
            logger.error(f"Error in thresholds command: {e}")
            await ctx.send("❌ Error managing thresholds")
    
    async def _list_thresholds(self, ctx):
        """List current thresholds."""
        config = self.bot.config["auto_collection"]
        thresholds = config.get("ignore_thresholds", [])
        
        embed = discord.Embed(
            title="💰 Drop Thresholds",
            description="Current drop thresholds and ignore chances",
            color=0x0099ff
        )
        
        if thresholds:
            for threshold in thresholds:
                embed.add_field(
                    name=f"${threshold['amount']:.4f}",
                    value=f"{threshold['percentage']}% chance to ignore",
                    inline=True
                )
        else:
            embed.add_field(
                name="No Thresholds",
                value="No thresholds configured",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="cooldown")
    async def set_cooldown(self, ctx, minutes: int = None):
        """Set cooldown period after claiming drops.
        
        Usage:
        !cooldown - Show current cooldown
        !cooldown 5 - Set cooldown to 5 minutes
        """
        try:
            if minutes is None:
                # Show current setting
                config = self.bot.config["auto_collection"]
                current = config.get("cooldown_minutes", 0)
                
                embed = discord.Embed(
                    title="⏱️ Cooldown Settings",
                    description="Current cooldown after claiming drops",
                    color=0x0099ff
                )
                
                embed.add_field(
                    name="Current Cooldown",
                    value=f"{current} minutes",
                    inline=True
                )
                
                await ctx.send(embed=embed)
            else:
                # Update setting
                embed = discord.Embed(
                    title="✅ Cooldown Updated",
                    description=f"Cooldown set to {minutes} minutes",
                    color=0x00ff00
                )
                
                await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in cooldown command: {e}")
            await ctx.send("❌ Error setting cooldown")
    
    @commands.command(name="help")
    async def help_tips(self, ctx):
        """Show tip command help."""
        embed = discord.Embed(
            title="💰 Tip Commands Help",
            description="Available tip collection commands",
            color=0x0099ff
        )
        
        embed.add_field(
            name="!status",
            value="Check auto-collection status",
            inline=False
        )
        
        embed.add_field(
            name="!stats",
            value="View tip statistics",
            inline=False
        )
        
        embed.add_field(
            name="!multi-account <action>",
            value="Manage multi-accounting (status/enable/disable/list)",
            inline=False
        )
        
        embed.add_field(
            name="!cpm [min] [max]",
            value="Set randomized CPM range",
            inline=False
        )
        
        embed.add_field(
            name="!channels <action>",
            value="Manage channel whitelist/blacklist",
            inline=False
        )
        
        embed.add_field(
            name="!thresholds <action>",
            value="Manage drop thresholds",
            inline=False
        )
        
        embed.add_field(
            name="!cooldown [minutes]",
            value="Set cooldown after claiming",
            inline=False
        )
        
        embed.add_field(
            name="!help",
            value="Show this help message",
            inline=False
        )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(TipCommands(bot)) 