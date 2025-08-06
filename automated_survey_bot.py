#!/usr/bin/env python3
"""
Automated Survey Bot - Complete Automation System

This script provides fully automated survey completion and Discord bot management.
"""

import asyncio
import os
import sys
import time
import signal
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from loguru import logger
import yaml

# Import bot components
from src.discord_bot.bot import SurveyBot
from src.utils.config_manager import ConfigManager
from src.utils.database_manager import DatabaseManager
from cpx_survey_automation import CPXSurveyAutomation


class AutomatedSurveyBot:
    """
    Complete automation system that manages both Discord bot and CPX survey automation.
    """
    
    def __init__(self):
        """Initialize the automated survey bot system."""
        self.discord_bot = None
        self.cpx_automation = None
        self.config = None
        self.db_manager = None
        self.shutdown_event = asyncio.Event()
        self.survey_thread = None
        self.is_running = False
        
        # Load environment variables
        load_dotenv()
        
        # Setup logging
        self.setup_logging()
        
        logger.info("Automated Survey Bot initialized")
    
    def setup_logging(self):
        """Setup comprehensive logging."""
        try:
            # Create logs directory
            os.makedirs("logs", exist_ok=True)
            
            # Configure loguru
            logger.add(
                "logs/automated_bot.log",
                rotation="10 MB",
                retention="7 days",
                level=os.getenv("LOG_LEVEL", "INFO"),
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
            )
            
            logger.info("Logging setup completed")
        except Exception as e:
            print(f"Failed to setup logging: {e}")
            raise
    
    async def load_configuration(self):
        """Load and validate configuration."""
        try:
            config_manager = ConfigManager("config.yaml")
            self.config = config_manager.get_config()
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    async def initialize_database(self):
        """Initialize database connection."""
        try:
            self.db_manager = DatabaseManager(self.config["database"]["url"])
            await self.db_manager.initialize()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def create_discord_bot(self):
        """Create and configure the Discord bot."""
        try:
            self.discord_bot = SurveyBot(self.config, self.db_manager)
            logger.info("Discord bot created successfully")
        except Exception as e:
            logger.error(f"Failed to create Discord bot: {e}")
            raise
    
    def create_cpx_automation(self, headless: bool = True):
        """Create CPX survey automation instance."""
        try:
            self.cpx_automation = CPXSurveyAutomation(headless=headless)
            logger.info("CPX automation created successfully")
        except Exception as e:
            logger.error(f"Failed to create CPX automation: {e}")
            raise
    
    async def start_discord_bot(self):
        """Start the Discord bot."""
        try:
            token = os.getenv("DISCORD_TOKEN")
            if not token:
                logger.error("DISCORD_TOKEN not found in environment variables")
                raise ValueError("DISCORD_TOKEN environment variable is required")
            
            logger.info("Starting Discord bot...")
            await self.discord_bot.start(token)
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {e}")
            raise
    
    def start_survey_automation(self):
        """Start the survey automation in a separate thread."""
        try:
            logger.info("Starting survey automation thread...")
            
            # Create CPX automation instance
            self.create_cpx_automation(headless=True)
            
            # Start browser
            if not self.cpx_automation.start_browser():
                logger.error("Failed to start browser for survey automation")
                return
            
            # Run survey automation loop
            while self.is_running:
                try:
                    logger.info("Starting new survey...")
                    
                    # Complete a survey
                    success = self.cpx_automation.complete_cpx_survey(
                        max_pages=15,
                        use_hybrid=True
                    )
                    
                    if success:
                        logger.info(f"Survey completed successfully! Earnings: ${self.cpx_automation.current_survey_earnings:.2f}")
                        
                        # Send Discord notification
                        self.send_discord_notification(
                            "Survey Completed",
                            f"✅ Survey completed successfully!\n💰 Earnings: ${self.cpx_automation.current_survey_earnings:.2f}\n📊 Total surveys: {self.cpx_automation.surveys_completed}",
                            "success"
                        )
                    else:
                        logger.warning("Survey automation failed")
                        
                        # Send Discord notification
                        self.send_discord_notification(
                            "Survey Failed",
                            "❌ Survey automation failed. Will retry...",
                            "error"
                        )
                    
                    # Wait before next survey
                    wait_time = random.randint(30, 120)  # 30 seconds to 2 minutes
                    logger.info(f"Waiting {wait_time} seconds before next survey...")
                    time.sleep(wait_time)
                    
                except Exception as e:
                    logger.error(f"Error in survey automation loop: {e}")
                    time.sleep(60)  # Wait 1 minute before retry
            
            # Cleanup
            if self.cpx_automation:
                self.cpx_automation.close_browser()
                
        except Exception as e:
            logger.error(f"Error in survey automation thread: {e}")
    
    def send_discord_notification(self, title: str, message: str, notification_type: str = "info"):
        """Send notification to Discord."""
        try:
            if self.discord_bot and hasattr(self.discord_bot, 'webhook_manager'):
                self.discord_bot.webhook_manager.send_system_status(
                    notification_type,
                    title,
                    {"Message": message}
                )
                logger.info(f"Discord notification sent: {title}")
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown_event.set()
            self.is_running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run_discord_bot_async(self):
        """Run Discord bot in async mode."""
        try:
            await self.start_discord_bot()
        except Exception as e:
            logger.error(f"Discord bot error: {e}")
    
    def run_survey_automation_sync(self):
        """Run survey automation in sync mode."""
        try:
            self.start_survey_automation()
        except Exception as e:
            logger.error(f"Survey automation error: {e}")
    
    async def run(self):
        """Main application run method."""
        try:
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Load configuration
            await self.load_configuration()
            
            # Initialize database
            await self.initialize_database()
            
            # Create Discord bot
            await self.create_discord_bot()
            
            # Set running flag
            self.is_running = True
            
            # Start survey automation in separate thread
            self.survey_thread = threading.Thread(
                target=self.run_survey_automation_sync,
                daemon=True
            )
            self.survey_thread.start()
            
            logger.info("Starting automated survey bot system...")
            
            # Run Discord bot
            await self.run_discord_bot_async()
            
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown of the application."""
        try:
            logger.info("Shutting down Automated Survey Bot...")
            
            # Stop survey automation
            self.is_running = False
            
            # Wait for survey thread to finish
            if self.survey_thread and self.survey_thread.is_alive():
                logger.info("Waiting for survey automation to finish...")
                self.survey_thread.join(timeout=30)
            
            # Close Discord bot
            if self.discord_bot:
                await self.discord_bot.close()
                logger.info("Discord bot closed")
            
            # Close CPX automation
            if self.cpx_automation:
                self.cpx_automation.close_browser()
                logger.info("CPX automation closed")
            
            # Close database connection
            if self.db_manager:
                await self.db_manager.close()
                logger.info("Database connection closed")
            
            logger.info("Shutdown completed successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


class SurveyAutomationManager:
    """
    Manager class for handling multiple survey automation instances.
    """
    
    def __init__(self):
        """Initialize the survey automation manager."""
        self.automation_instances = []
        self.is_running = False
        
    def add_automation_instance(self, headless: bool = True):
        """Add a new automation instance."""
        try:
            automation = CPXSurveyAutomation(headless=headless)
            self.automation_instances.append(automation)
            logger.info(f"Added automation instance {len(self.automation_instances)}")
            return automation
        except Exception as e:
            logger.error(f"Failed to add automation instance: {e}")
            return None
    
    def start_all_automations(self):
        """Start all automation instances."""
        try:
            self.is_running = True
            
            for i, automation in enumerate(self.automation_instances):
                if automation.start_browser():
                    logger.info(f"Started automation instance {i + 1}")
                else:
                    logger.error(f"Failed to start automation instance {i + 1}")
            
        except Exception as e:
            logger.error(f"Error starting automations: {e}")
    
    def stop_all_automations(self):
        """Stop all automation instances."""
        try:
            self.is_running = False
            
            for i, automation in enumerate(self.automation_instances):
                automation.close_browser()
                logger.info(f"Stopped automation instance {i + 1}")
            
        except Exception as e:
            logger.error(f"Error stopping automations: {e}")
    
    def run_survey_loop(self):
        """Run survey completion loop for all instances."""
        while self.is_running:
            try:
                for i, automation in enumerate(self.automation_instances):
                    if not self.is_running:
                        break
                    
                    try:
                        logger.info(f"Running survey on instance {i + 1}")
                        
                        success = automation.complete_cpx_survey(
                            max_pages=15,
                            use_hybrid=True
                        )
                        
                        if success:
                            logger.info(f"Instance {i + 1} completed survey successfully")
                        else:
                            logger.warning(f"Instance {i + 1} failed to complete survey")
                    
                    except Exception as e:
                        logger.error(f"Error in automation instance {i + 1}: {e}")
                
                # Wait before next round
                if self.is_running:
                    wait_time = random.randint(60, 300)  # 1-5 minutes
                    logger.info(f"Waiting {wait_time} seconds before next survey round...")
                    time.sleep(wait_time)
            
            except Exception as e:
                logger.error(f"Error in survey loop: {e}")
                time.sleep(60)


async def main():
    """Main application entry point."""
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    # Run the automated survey bot
    bot = AutomatedSurveyBot()
    await bot.run()


def run_survey_only():
    """Run only the survey automation without Discord bot."""
    try:
        print("Starting CPX Survey Automation (Survey Only Mode)")
        print("=" * 50)
        
        # Create necessary directories
        os.makedirs("logs", exist_ok=True)
        os.makedirs("screenshots", exist_ok=True)
        
        # Setup logging
        logger.add(
            "logs/survey_only.log",
            rotation="10 MB",
            retention="7 days",
            level="INFO"
        )
        
        # Create automation manager
        manager = SurveyAutomationManager()
        
        # Add automation instances
        num_instances = int(input("Number of automation instances (1-5): ") or "1")
        num_instances = max(1, min(5, num_instances))
        
        for i in range(num_instances):
            manager.add_automation_instance(headless=True)
        
        # Start automations
        manager.start_all_automations()
        
        # Run survey loop
        try:
            manager.run_survey_loop()
        except KeyboardInterrupt:
            print("\nStopping survey automation...")
        finally:
            manager.stop_all_automations()
            print("Survey automation stopped")
    
    except Exception as e:
        logger.error(f"Error in survey-only mode: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    import random
    
    print("Automated Survey Bot System")
    print("=" * 30)
    print("1. Full automation (Discord + Surveys)")
    print("2. Survey automation only")
    print("3. Discord bot only")
    
    choice = input("\nSelect mode (1-3): ").strip()
    
    if choice == "1":
        print("\nStarting full automation system...")
        asyncio.run(main())
    elif choice == "2":
        print("\nStarting survey automation only...")
        run_survey_only()
    elif choice == "3":
        print("\nStarting Discord bot only...")
        # This would run just the Discord bot
        asyncio.run(main())
    else:
        print("Invalid choice. Exiting.")