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
from src.utils.config_manager import ConfigManager
from src.utils.database_manager import DatabaseManager
from src.utils.webhook_manager import WebhookManager



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
        self.webhook_manager = WebhookManager()
        
        # Store channel references
        self.channels = {}
        
        # Setup event handlers
        self.setup_events()
        self.setup_commands()
        
        # Slash commands will be loaded in on_ready
        
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
                    
                    # Send system notification
                    self.webhook_manager.send_system_status(
                        "info",
                        "Survey automation started by user",
                        {
                            "User": ctx.author.name,
                            "Server": ctx.guild.name,
                            "Channel": ctx.channel.name
                        }
                    )
                    
                elif action == "earnings":
                    embed = discord.Embed(
                        title="💰 Earnings Summary",
                        description="Your current earnings and statistics",
                        color=0xffd700
                    )
                    
                    embed.add_field(name="Total Earnings", value="$0.00", inline=True)
                    embed.add_field(name="This Session", value="$0.00", inline=True)
                    embed.add_field(name="Surveys Completed", value="0", inline=True)
                    embed.add_field(name="Average Per Survey", value="$0.00", inline=True)
                    embed.add_field(name="Withdrawals", value="$0.00", inline=True)
                    embed.add_field(name="Available Balance", value="$0.00", inline=True)
                    
                    await ctx.send(embed=embed)
                    
                else:
                    await ctx.send("❌ Invalid action. Use: status, start, or earnings")
                    
            except Exception as e:
                logger.error(f"Error in survey command: {e}")
                await ctx.send("❌ An error occurred while processing the command.")
        
        @self.command(name="status")
        async def status(ctx):
            """Check bot status."""
            try:
                embed = discord.Embed(
                    title="🤖 Bot Status",
                    description="Current bot status and information",
                    color=0x00ff00
                )
                
                embed.add_field(name="Status", value="🟢 Online", inline=True)
                embed.add_field(name="Uptime", value="Running", inline=True)
                embed.add_field(name="Ping", value=f"{round(self.latency * 1000)}ms", inline=True)
                embed.add_field(name="Servers", value=len(self.guilds), inline=True)
                embed.add_field(name="Users", value=len(self.users), inline=True)
                embed.add_field(name="Commands", value=len(self.commands), inline=True)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in status command: {e}")
                await ctx.send("❌ An error occurred while checking status.")
        
        @self.command(name="withdraw")
        async def withdraw(ctx, amount: float = None):
            """Withdraw earnings."""
            try:
                if amount is None:
                    await ctx.send("❌ Please specify an amount to withdraw.")
                    return
                
                if amount <= 0:
                    await ctx.send("❌ Amount must be greater than 0.")
                    return
                
                embed = discord.Embed(
                    title="💰 Withdrawal Request",
                    description=f"Processing withdrawal of ${amount:.2f}",
                    color=0xffd700
                )
                
                embed.add_field(name="Amount", value=f"${amount:.2f}", inline=True)
                embed.add_field(name="Status", value="⏳ Processing", inline=True)
                embed.add_field(name="User", value=ctx.author.mention, inline=True)
                
                await ctx.send(embed=embed)
                
                # Send webhook notification
                self.webhook_manager.send_withdrawal_notification(
                    ctx.author.name,
                    amount,
                    ctx.guild.name
                )
                
            except Exception as e:
                logger.error(f"Error in withdraw command: {e}")
                await ctx.send("❌ An error occurred while processing withdrawal.")
        
        @self.command(name="earnings")
        async def earnings(ctx):
            """Check earnings."""
            try:
                embed = discord.Embed(
                    title="💰 Earnings Summary",
                    description="Your current earnings and statistics",
                    color=0xffd700
                )
                
                embed.add_field(name="Total Earnings", value="$0.00", inline=True)
                embed.add_field(name="This Session", value="$0.00", inline=True)
                embed.add_field(name="Surveys Completed", value="0", inline=True)
                embed.add_field(name="Average Per Survey", value="$0.00", inline=True)
                embed.add_field(name="Withdrawals", value="$0.00", inline=True)
                embed.add_field(name="Available Balance", value="$0.00", inline=True)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in earnings command: {e}")
                await ctx.send("❌ An error occurred while checking earnings.")
        
        @self.command(name="mine")
        async def mine(ctx):
            """Mining command for gaming integration."""
            try:
                embed = discord.Embed(
                    title="⛏️ Mining",
                    description="You went mining and found some resources!",
                    color=0x8b4513
                )
                
                embed.add_field(name="Resources Found", value="Iron: 5, Coal: 3", inline=True)
                embed.add_field(name="Experience", value="+10 XP", inline=True)
                embed.add_field(name="Cooldown", value="5 minutes", inline=True)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in mine command: {e}")
                await ctx.send("❌ An error occurred while mining.")
        
        @self.command(name="help")
        async def help_command(ctx):
            """Show help information."""
            try:
                embed = discord.Embed(
                    title="🤖 Survey Bot Help",
                    description="Available commands and features",
                    color=0x0099ff
                )
                
                # Survey Commands
                embed.add_field(
                    name="📊 Survey Commands",
                    value="""`!survey status` - Check bot status
`!survey start` - Start survey automation
`!survey earnings` - Check earnings
`!earnings` - Quick earnings check
`!withdraw <amount>` - Withdraw earnings""",
                    inline=False
                )
                
                # Gaming Commands
                embed.add_field(
                    name="🎮 Gaming Commands",
                    value="""`!mine` - Go mining
`!fish` - Go fishing
`!rob` - Rob someone
`!open <chest>` - Open a chest
`!refine <material>` - Refine materials
`!learn <skill>` - Learn a skill
`!craft <item>` - Craft an item""",
                    inline=False
                )
                
                # Slash Commands
                embed.add_field(
                    name="🔧 Slash Commands",
                    value="""`/survey` - Check survey status
`/start` - Start survey automation
`/earnings` - Check earnings
`/withdraw <amount>` - Withdraw earnings
`/help` - Show this help
`/assign` - Assign gamer role
`/remove` - Remove gamer role
`/poll <question>` - Create a poll""",
                    inline=False
                )
                
                embed.set_footer(text="Use /help for slash commands or !help for prefix commands")
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in help command: {e}")
                await ctx.send("❌ An error occurred while showing help.")
        
        @self.command(name="assign")
        async def assign_role(ctx):
            """Assign gamer role to user."""
            try:
                # Check if gamer role exists
                gamer_role = discord.utils.get(ctx.guild.roles, name="gamer")
                
                if not gamer_role:
                    # Create the gamer role if it doesn't exist
                    gamer_role = await ctx.guild.create_role(
                        name="gamer",
                        color=discord.Color.green(),
                        reason="Auto-created gamer role"
                    )
                    logger.info(f"Created gamer role in {ctx.guild.name}")
                
                # Check if user already has the role
                if gamer_role in ctx.author.roles:
                    await ctx.send("✅ You already have the gamer role!")
                    return
                
                # Assign the role
                await ctx.author.add_roles(gamer_role)
                
                embed = discord.Embed(
                    title="🎮 Role Assigned",
                    description=f"Successfully assigned gamer role to {ctx.author.mention}",
                    color=0x00ff00
                )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in assign command: {e}")
                await ctx.send("❌ An error occurred while assigning role.")
        
        @self.command(name="remove")
        async def remove_role(ctx):
            """Remove gamer role from user."""
            try:
                gamer_role = discord.utils.get(ctx.guild.roles, name="gamer")
                
                if not gamer_role:
                    await ctx.send("❌ Gamer role doesn't exist.")
                    return
                
                if gamer_role not in ctx.author.roles:
                    await ctx.send("❌ You don't have the gamer role.")
                    return
                
                # Remove the role
                await ctx.author.remove_roles(gamer_role)
                
                embed = discord.Embed(
                    title="🎮 Role Removed",
                    description=f"Successfully removed gamer role from {ctx.author.mention}",
                    color=0xff0000
                )
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in remove command: {e}")
                await ctx.send("❌ An error occurred while removing role.")
        
        @self.command(name="secret")
        @commands.has_role("gamer")  # Requires the gamer role
        async def secret_command(ctx):
            """Secret command for gamers only."""
            await ctx.send("🎮 You found the secret command! This is only for gamers.")
        
        @secret_command.error
        async def secret_error(ctx, error):
            if isinstance(error, commands.MissingRole):
                await ctx.send("❌ You need the gamer role to use this command!")
            else:
                await ctx.send("❌ An error occurred with the secret command.")
        
        @self.command(name="dm")
        async def send_dm(ctx, *, message):
            """Send a DM to the bot owner."""
            try:
                owner = self.get_user(self.owner_id)
                if owner:
                    await owner.send(f"DM from {ctx.author}: {message}")
                    await ctx.send("✅ Message sent to bot owner.")
                else:
                    await ctx.send("❌ Could not find bot owner.")
            except Exception as e:
                logger.error(f"Error in dm command: {e}")
                await ctx.send("❌ An error occurred while sending DM.")
        
        @self.command(name="reply")
        async def reply_to_message(ctx):
            """Reply to the last message in the channel."""
            try:
                messages = await ctx.channel.history(limit=2).flatten()
                if len(messages) > 1:
                    last_message = messages[1]  # Skip the command message
                    await ctx.send(f"Replying to: {last_message.content}")
                else:
                    await ctx.send("❌ No previous message to reply to.")
            except Exception as e:
                logger.error(f"Error in reply command: {e}")
                await ctx.send("❌ An error occurred while replying.")
        
        @self.command(name="poll")
        async def create_poll(ctx, *, question):
            """Create a poll with reactions."""
            try:
                embed = discord.Embed(
                    title="📊 Poll",
                    description=question,
                    color=0x0099ff
                )
                embed.set_footer(text=f"Poll created by {ctx.author.name}")
                
                poll_message = await ctx.send(embed=embed)
                
                # Add reaction options
                reactions = ["👍", "👎", "🤷"]
                for reaction in reactions:
                    await poll_message.add_reaction(reaction)
                
            except Exception as e:
                logger.error(f"Error in poll command: {e}")
                await ctx.send("❌ An error occurred while creating poll.")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        try:
            logger.info(f"✅ Bot is ready! Logged in as {self.user}")
            logger.info(f"Bot ID: {self.user.id}")
            logger.info(f"Connected to {len(self.guilds)} guilds")
            
            # Store channel references
            for guild in self.guilds:
                for channel in guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        self.channels[channel.name] = channel
            
            # Load slash commands
            await self.load_slash_commands()
            
            # Start background tasks
            asyncio.create_task(self.background_tasks())
            
            # Set bot status
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="for surveys | /help"
                )
            )
            
            logger.info("Bot setup completed successfully")
            
        except Exception as e:
            logger.error(f"Error in on_ready: {e}")
    
    async def on_message(self, message):
        """Handle incoming messages."""
        try:
            # Ignore bot messages
            if message.author == self.user:
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
    
    async def load_slash_commands(self):
        """Load and register slash commands."""
        try:
            # Import and setup slash commands
            from .slash_commands import setup, register_commands
            
            # Setup the cog
            await setup(self)
            
            # Register commands with Discord (both globally and per guild)
            await self.tree.sync()  # Global sync
            
            # Also sync to each guild for immediate availability
            for guild in self.guilds:
                try:
                    await self.tree.sync(guild=guild)
                    logger.info(f"✅ Commands synced to guild: {guild.name}")
                except Exception as e:
                    logger.warning(f"Failed to sync commands to guild {guild.name}: {e}")
            
            logger.info("✅ Slash commands loaded and synced successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading slash commands: {e}")
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close() 