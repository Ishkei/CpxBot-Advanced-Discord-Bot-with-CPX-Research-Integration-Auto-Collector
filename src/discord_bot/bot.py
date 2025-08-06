"""
Discord Bot - Main Bot Class

Handles Discord bot initialization, event handling, and command processing.
"""

import discord
from discord.ext import commands
from loguru import logger
import asyncio
from typing import Dict, Any

from .events.ready_event import ReadyEvent
from .events.message_event import MessageEvent
from .handlers.survey_handler import SurveyHandler



class SurveyBot(commands.Bot):
    """Main Discord bot class for survey automation and gaming integration."""
    
    def __init__(self, config: Dict[str, Any], db_manager):
        """Initialize the bot with configuration and database manager."""
        # Use proper intents configuration as shown in the tutorial
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.reactions = True
        
        super().__init__(
            command_prefix=config["discord"]["prefix"],
            intents=intents,
            help_command=None
        )
        
        self.config = config
        self.db_manager = db_manager
        self.survey_handler = SurveyHandler(config, db_manager)
        
        # Store channel references
        self.channels = {}
        
        # Setup event handlers
        self.setup_events()
        self.setup_commands()
        
        logger.info("SurveyBot initialized successfully")
    
    def setup_events(self):
        """Setup Discord event handlers."""
        self.add_listener(ReadyEvent(self).on_ready, "on_ready")
        self.add_listener(MessageEvent(self).on_message, "on_message")
        self.add_listener(self.on_command_error, "on_command_error")
        
    def setup_commands(self):
        """Setup basic commands."""
        
        # Survey Commands
        @self.command(name="survey")
        async def survey(ctx, action: str = "status"):
            """Survey commands: !survey [status|start|earnings|list]"""
            try:
                if action == "status":
                    embed = discord.Embed(
                        title="🤖 Survey Bot Status",
                        description="Current bot status and statistics",
                        color=0x00ff00
                    )
                    
                    embed.add_field(
                        name="🔧 Bot Status",
                        value="✅ Online and Ready",
                        inline=False
                    )
                    
                    await ctx.send(embed=embed)
                    
                elif action == "start":
                    await ctx.send("🔍 Starting survey automation...")
                    # This would trigger the survey automation
                    
                elif action == "earnings":
                    earnings_data = await self.db_manager.get_earnings()
                    embed = discord.Embed(
                        title="💰 Survey Earnings",
                        description="Your survey earnings overview",
                        color=0xffd700
                    )
                    
                    embed.add_field(
                        name="💵 Total Earnings",
                        value=f"${earnings_data['total']:.2f}",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="📅 Today's Earnings",
                        value=f"${earnings_data['today']:.2f}",
                        inline=True
                    )
                    
                    await ctx.send(embed=embed)
                    
                elif action == "list":
                    await ctx.send("📋 Checking for available surveys...")
                    # This would list available surveys
                    
                else:
                    await ctx.send("❌ Invalid survey action. Use: status, start, earnings, or list")
                    
            except Exception as e:
                logger.error(f"Error in survey command: {e}")
                await ctx.send("❌ Error processing survey command")
        
        @self.command(name="status")
        async def status(ctx):
            """Check the current survey bot status."""
            try:
                embed = discord.Embed(
                    title="🤖 Survey Bot Status",
                    description="Current bot status and system information",
                    color=0x00ff00,
                    timestamp=discord.utils.utcnow()
                )
                
                # Bot status
                embed.add_field(
                    name="🔧 Bot Status",
                    value="✅ Online and Ready",
                    inline=True
                )
                
                # System info
                embed.add_field(
                    name="📊 System Info",
                    value=f"Uptime: {discord.utils.utcnow().strftime('%H:%M:%S')}\n"
                          f"Latency: {round(self.latency * 1000)}ms",
                    inline=True
                )
                
                # Survey stats
                try:
                    stats = await self.db_manager.get_bot_stat("survey_stats")
                    if stats:
                        embed.add_field(
                            name="📈 Survey Statistics",
                            value=f"Completed: {stats.get('completed', 0)}\n"
                                  f"Earnings: ${stats.get('total_earnings', 0.0):.2f}",
                            inline=True
                        )
                    else:
                        embed.add_field(
                            name="📈 Survey Statistics",
                            value="No data available",
                            inline=True
                        )
                except Exception as e:
                    logger.error(f"Error getting survey stats: {e}")
                    embed.add_field(
                        name="📈 Survey Statistics",
                        value="Error loading stats",
                        inline=True
                    )
                
                # Footer
                embed.set_footer(text="Survey Bot v1.0", icon_url=self.user.avatar.url if self.user.avatar else None)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in status command: {e}")
                await ctx.send("❌ Error getting bot status")
        
        @self.command(name="earnings")
        async def earnings(ctx):
            """View earnings statistics."""
            try:
                earnings_data = await self.db_manager.get_earnings()
                
                embed = discord.Embed(
                    title="💰 Earnings Statistics",
                    description="Your survey earnings overview",
                    color=0xffd700
                )
                
                embed.add_field(
                    name="💵 Total Earnings",
                    value=f"${earnings_data['total']:.2f}",
                    inline=True
                )
                
                embed.add_field(
                    name="📅 Today's Earnings",
                    value=f"${earnings_data['today']:.2f}",
                    inline=True
                )
                
                embed.add_field(
                    name="📊 This Week",
                    value=f"${earnings_data['week']:.2f}",
                    inline=True
                )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in earnings command: {e}")
                await ctx.send("❌ Error getting earnings")
        
        @self.command(name="mine")
        async def mine(ctx):
            """Mine for cryptocurrency."""
            try:
                import random
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
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in mine command: {e}")
                await ctx.send("❌ Error while mining")
        
        @self.command(name="help")
        async def help_command(ctx):
            """Show help information and available commands."""
            try:
                embed = discord.Embed(
                    title="📚 Survey Bot Help",
                    description="Available commands and their usage",
                    color=0x0099ff,
                    timestamp=discord.utils.utcnow()
                )
                
                # Survey commands
                embed.add_field(
                    name="🔍 Survey Commands",
                    value="`!survey status` - Check current survey status\n"
                          "`!survey start` - Start a new survey\n"
                          "`!survey earnings` - Check current earnings\n"
                          "`!survey list` - List available surveys",
                    inline=False
                )
                
                # Utility commands
                embed.add_field(
                    name="💰 Utility Commands",
                    value="`!earnings` - Quick earnings check\n"
                          "`!withdraw [amount]` - Withdraw earnings\n"
                          "`!status` - Bot status and system info\n"
                          "`!help` - Show this help message",
                    inline=False
                )
                
                # Role management
                embed.add_field(
                    name="🎭 Role Commands",
                    value="`!assign` - Assign gamer role\n"
                          "`!remove` - Remove gamer role\n"
                          "`!secret` - Secret command (requires gamer role)",
                    inline=False
                )
                
                # Communication commands
                embed.add_field(
                    name="💬 Communication",
                    value="`!dm [message]` - Send yourself a DM\n"
                          "`!reply` - Reply to your message\n"
                          "`!poll [question]` - Create a poll",
                    inline=False
                )
                
                # Footer
                embed.set_footer(text="Use !help [command] for detailed information", 
                               icon_url=self.user.avatar.url if self.user.avatar else None)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in help command: {e}")
                await ctx.send("❌ Error displaying help")
        
        @self.command(name="assign")
        async def assign_role(ctx):
            """Assign a role to the user."""
            try:
                role_name = "gamer"  # Change this to your role name
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                
                if role:
                    await ctx.author.add_roles(role)
                    await ctx.send(f"{ctx.author.mention} is now assigned to {role_name}")
                else:
                    await ctx.send("Role doesn't exist")
                    
            except Exception as e:
                logger.error(f"Error in assign command: {e}")
                await ctx.send("❌ Error assigning role")
        
        @self.command(name="remove")
        async def remove_role(ctx):
            """Remove a role from the user."""
            try:
                role_name = "gamer"  # Change this to your role name
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                
                if role:
                    await ctx.author.remove_roles(role)
                    await ctx.send(f"{ctx.author.mention} has had the {role_name} role removed")
                else:
                    await ctx.send("Role doesn't exist")
                    
            except Exception as e:
                logger.error(f"Error in remove command: {e}")
                await ctx.send("❌ Error removing role")
        
        @self.command(name="secret")
        @commands.has_role("gamer")  # Requires the gamer role
        async def secret_command(ctx):
            """Secret command that requires the gamer role."""
            await ctx.send("Welcome to the club! 🎉")
        
        @secret_command.error
        async def secret_error(ctx, error):
            """Handle errors for the secret command."""
            if isinstance(error, commands.MissingRole):
                await ctx.send("You do not have permission to do that!")
            else:
                await ctx.send("❌ An error occurred")
        
        @self.command(name="dm")
        async def send_dm(ctx, *, message):
            """Send a DM to the user."""
            try:
                await ctx.author.send(f"You said: {message}")
                await ctx.send("✅ DM sent!")
            except Exception as e:
                logger.error(f"Error in dm command: {e}")
                await ctx.send("❌ Error sending DM")
        
        @self.command(name="reply")
        async def reply_to_message(ctx):
            """Reply to the user's message."""
            try:
                await ctx.reply("This is a reply to your message!")
            except Exception as e:
                logger.error(f"Error in reply command: {e}")
                await ctx.send("❌ Error replying to message")
        
        @self.command(name="poll")
        async def create_poll(ctx, *, question):
            """Create a poll with reactions."""
            try:
                embed = discord.Embed(
                    title="📊 New Poll",
                    description=question,
                    color=0x00ff00
                )
                
                poll_message = await ctx.send(embed=embed)
                
                # Add reactions
                await poll_message.add_reaction("👍")
                await poll_message.add_reaction("👎")
                
            except Exception as e:
                logger.error(f"Error in poll command: {e}")
                await ctx.send("❌ Error creating poll")
    
    async def on_ready(self):
        """Called when the bot is ready and connected to Discord."""
        try:
            logger.info(f"Logged in as {self.user.name}")
            logger.info(f"Bot ID: {self.user.id}")
            
            # Set bot status
            await self.change_presence(activity=discord.Game(name="Surveys | !help"))
            
        except Exception as e:
            logger.error(f"Error in on_ready: {e}")
    
    async def on_message(self, message):
        """Handle incoming messages."""
        try:
            # Don't respond to our own messages
            if message.author == self.user:
                return
            
            # Swear word filter (like in the tutorial)
            bad_words = ["badword", "swear", "curse"]  # Add your list of words
            if any(word in message.content.lower() for word in bad_words):
                await message.delete()
                await message.channel.send(f"{message.author.mention} Don't use that word!")
                return
            
            # Process commands
            await self.process_commands(message)
            
        except Exception as e:
            logger.error(f"Error in on_message: {e}")
    
    async def on_member_join(self, member):
        """Handle new member joins."""
        try:
            await member.send(f"Welcome to the server, {member.name}! 🎉")
            logger.info(f"New member joined: {member.name}")
        except Exception as e:
            logger.error(f"Error in on_member_join: {e}")
    
    async def background_tasks(self):
        """Background tasks for the bot."""
        while not self.is_closed():
            try:
                # Check for new surveys
                await self.survey_handler.check_for_surveys()
                
                # Wait before next iteration
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in background tasks: {e}")
                await asyncio.sleep(60)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors."""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have permission to do that.")
        else:
            logger.error(f"Command error: {error}")
            await ctx.send(f"An error occurred: {error}")
    
    def get_channel(self, channel_name: str):
        """Get a channel by name."""
        return self.channels.get(channel_name)
    
    async def send_to_channel(self, channel_name: str, message: str):
        """Send a message to a specific channel."""
        channel = self.get_channel(channel_name)
        if channel:
            await channel.send(message)
        else:
            logger.warning(f"Channel {channel_name} not found")
    
    def is_valid_channel(self, channel_name: str) -> bool:
        """Check if a channel name is valid."""
        return channel_name in self.config["channels"]
    
    async def close(self):
        """Close the bot and cleanup resources."""
        try:
            # Close survey handler
            if hasattr(self, 'survey_handler'):
                await self.survey_handler.close()
            
            # Close database connection
            if hasattr(self, 'db_manager'):
                await self.db_manager.close()
            
            # Close Discord connection
            await super().close()
            
            logger.info("Bot shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during bot shutdown: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close() 