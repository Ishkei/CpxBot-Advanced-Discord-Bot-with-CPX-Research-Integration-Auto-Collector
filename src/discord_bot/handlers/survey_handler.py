"""
Survey Handler - Manages survey automation and integration

Handles survey completion, earnings tracking, and integration with Discord bot.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from loguru import logger
from datetime import datetime, timedelta

from src.web_scraper.cpx_scraper import CPXScraper


class SurveyHandler:
    """Handles survey automation and management."""
    
    def __init__(self, config: Dict[str, Any], db_manager):
        """Initialize the survey handler.
        
        Args:
            config: Configuration dictionary
            db_manager: Database manager instance
        """
        self.config = config
        self.db_manager = db_manager
        self.scraper = None
        self.is_running = False
        self.current_survey = None
        
    async def initialize(self):
        """Initialize the survey handler."""
        try:
            self.scraper = CPXScraper(self.config)
            await self.scraper.initialize_driver()
            logger.info("Survey handler initialized")
        except Exception as e:
            logger.error(f"Error initializing survey handler: {e}")
            raise
    
    async def check_for_surveys(self):
        """Check for available surveys and start them if conditions are met."""
        try:
            if self.is_running:
                logger.info("Survey handler already running, skipping check")
                return
            
            # Check if scraper is initialized
            if self.scraper is None:
                logger.warning("Survey handler not initialized, attempting to initialize...")
                try:
                    await self.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize survey handler: {e}")
                    return
            
            # Get available surveys
            surveys = await self.scraper.get_available_surveys()
            
            if not surveys:
                logger.info("No suitable surveys available")
                return
            
            # Sort surveys by earnings (highest first)
            surveys.sort(key=lambda x: x["earnings"], reverse=True)
            
            # Start the best survey
            best_survey = surveys[0]
            await self.start_survey(best_survey)
            
        except Exception as e:
            logger.error(f"Error checking for surveys: {e}")
    
    async def start_survey(self, survey_data: Dict[str, Any]) -> bool:
        """Start a survey.
        
        Args:
            survey_data: Survey information
            
        Returns:
            True if survey started successfully, False otherwise
        """
        try:
            if self.is_running:
                logger.warning("Survey already in progress")
                return False
            
            self.is_running = True
            self.current_survey = survey_data
            
            logger.info(f"Starting survey: {survey_data['title']}")
            
            # Add survey to database
            await self.db_manager.add_survey({
                "survey_id": f"survey_{int(time.time())}",
                "title": survey_data["title"],
                "earnings": survey_data["earnings"],
                "duration": survey_data["duration"],
                "status": "in_progress"
            })
            
            # Check if scraper is initialized
            if self.scraper is None:
                logger.warning("Survey handler not initialized, attempting to initialize...")
                try:
                    await self.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize survey handler: {e}")
                    self.is_running = False
                    self.current_survey = None
                    return False
            
            # Complete the survey
            result = await self.scraper.complete_survey(survey_data)
            
            if result["success"]:
                # Update database with completion
                await self.db_manager.add_earning(
                    result["earnings"],
                    "survey_completion",
                    "completed"
                )
                
                # Update survey status
                await self.db_manager.add_survey({
                    "survey_id": f"survey_{int(time.time())}",
                    "title": survey_data["title"],
                    "earnings": survey_data["earnings"],
                    "duration": survey_data["duration"],
                    "status": "completed",
                    "completed_at": datetime.now()
                })
                
                logger.info(f"Survey completed successfully: ${result['earnings']:.2f}")
                
            else:
                logger.error(f"Survey failed: {result.get('error', 'Unknown error')}")
                
            self.is_running = False
            self.current_survey = None
            
            return result["success"]
            
        except Exception as e:
            logger.error(f"Error starting survey: {e}")
            self.is_running = False
            self.current_survey = None
            return False
    
    async def find_and_start_survey(self) -> Optional[Dict[str, Any]]:
        """Find and start the best available survey.
        
        Returns:
            Survey data if started successfully, None otherwise
        """
        try:
            # Check if scraper is initialized
            if self.scraper is None:
                logger.warning("Survey handler not initialized, attempting to initialize...")
                try:
                    await self.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize survey handler: {e}")
                    return None
            
            surveys = await self.scraper.get_available_surveys()
            
            if not surveys:
                return None
            
            # Sort by earnings and start the best one
            surveys.sort(key=lambda x: x["earnings"], reverse=True)
            best_survey = surveys[0]
            
            success = await self.start_survey(best_survey)
            
            if success:
                return best_survey
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error finding and starting survey: {e}")
            return None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current survey status.
        
        Returns:
            Dictionary with status information
        """
        try:
            earnings = await self.db_manager.get_earnings()
            
            return {
                "active_surveys": 1 if self.is_running else 0,
                "total_earnings": earnings["total"],
                "today_earnings": earnings["today"],
                "current_survey": self.current_survey["title"] if self.current_survey else None,
                "is_running": self.is_running
            }
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {
                "active_surveys": 0,
                "total_earnings": 0.0,
                "today_earnings": 0.0,
                "current_survey": None,
                "is_running": False
            }
    
    async def get_earnings(self) -> Dict[str, float]:
        """Get earnings statistics.
        
        Returns:
            Dictionary with earnings information
        """
        try:
            return await self.db_manager.get_earnings()
        except Exception as e:
            logger.error(f"Error getting earnings: {e}")
            return {"total": 0.0, "today": 0.0, "week": 0.0}
    
    async def get_available_surveys(self) -> List[Dict[str, Any]]:
        """Get list of available surveys.
        
        Returns:
            List of survey dictionaries
        """
        try:
            # Check if scraper is initialized
            if self.scraper is None:
                logger.warning("Survey handler not initialized, attempting to initialize...")
                try:
                    await self.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize survey handler: {e}")
                    return []
            
            return await self.scraper.get_available_surveys()
        except Exception as e:
            logger.error(f"Error getting available surveys: {e}")
            return []
    
    async def withdraw_all(self) -> Dict[str, Any]:
        """Withdraw all available balance.
        
        Returns:
            Dictionary with withdrawal result
        """
        try:
            earnings = await self.db_manager.get_earnings()
            total_available = earnings["total"]
            
            if total_available <= 0:
                return {
                    "success": False,
                    "error": "No funds available for withdrawal",
                    "amount": 0.0
                }
            
            # Simulate withdrawal to tip.cc
            # In a real implementation, this would integrate with tip.cc API
            
            # Mark earnings as withdrawn
            await self.db_manager.add_earning(
                -total_available,
                "withdrawal",
                "completed"
            )
            
            logger.info(f"Withdrew ${total_available:.2f}")
            
            return {
                "success": True,
                "amount": total_available,
                "message": f"Withdrew ${total_available:.2f} to tip.cc wallet"
            }
            
        except Exception as e:
            logger.error(f"Error withdrawing funds: {e}")
            return {
                "success": False,
                "error": str(e),
                "amount": 0.0
            }
    
    async def withdraw_amount(self, amount: float) -> Dict[str, Any]:
        """Withdraw a specific amount.
        
        Args:
            amount: Amount to withdraw
            
        Returns:
            Dictionary with withdrawal result
        """
        try:
            earnings = await self.db_manager.get_earnings()
            total_available = earnings["total"]
            
            if amount > total_available:
                return {
                    "success": False,
                    "error": f"Insufficient funds. Available: ${total_available:.2f}",
                    "amount": 0.0
                }
            
            # Simulate withdrawal to tip.cc
            # In a real implementation, this would integrate with tip.cc API
            
            # Mark earnings as withdrawn
            await self.db_manager.add_earning(
                -amount,
                "withdrawal",
                "completed"
            )
            
            logger.info(f"Withdrew ${amount:.2f}")
            
            return {
                "success": True,
                "amount": amount,
                "message": f"Withdrew ${amount:.2f} to tip.cc wallet"
            }
            
        except Exception as e:
            logger.error(f"Error withdrawing amount: {e}")
            return {
                "success": False,
                "error": str(e),
                "amount": 0.0
            }
    
    async def stop_current_survey(self) -> bool:
        """Stop the currently running survey.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        try:
            if not self.is_running:
                logger.warning("No survey currently running")
                return False
            
            # Close the browser/driver to stop the survey
            if self.scraper and self.scraper.driver:
                self.scraper.driver.quit()
                await self.scraper.initialize_driver()
            
            self.is_running = False
            self.current_survey = None
            
            logger.info("Survey stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping survey: {e}")
            return False
    
    async def get_survey_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get survey completion history.
        
        Args:
            limit: Maximum number of surveys to return
            
        Returns:
            List of completed surveys
        """
        try:
            return await self.db_manager.get_surveys(limit=limit, status="completed")
        except Exception as e:
            logger.error(f"Error getting survey history: {e}")
            return []
    
    async def close(self):
        """Close the survey handler."""
        try:
            if self.scraper:
                await self.scraper.close()
            logger.info("Survey handler closed")
        except Exception as e:
            logger.error(f"Error closing survey handler: {e}") 